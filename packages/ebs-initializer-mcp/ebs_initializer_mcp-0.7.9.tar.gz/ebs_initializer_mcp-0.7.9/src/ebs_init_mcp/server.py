#!/usr/bin/env python3
"""
EBS Volume Initialization FastMCP Server

This FastMCP server provides tools for automatically initializing AWS EBS volumes
attached to EC2 instances using AWS Systems Manager.
"""

import json
import logging
import os
from typing import Dict, List, Any

import boto3
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get default region from environment variable (evaluated at module load time)
DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', os.getenv('AWS_REGION', 'us-east-1'))

# Create reusable boto3 clients (lazy initialization)
_ec2_clients = {}
_ssm_clients = {}

def get_ec2_client(region: str = DEFAULT_REGION):
    """Get or create EC2 client for the specified region."""
    if region not in _ec2_clients:
        _ec2_clients[region] = boto3.client('ec2', region_name=region)
    return _ec2_clients[region]

def get_ssm_client(region: str = DEFAULT_REGION):
    """Get or create SSM client for the specified region."""
    if region not in _ssm_clients:
        _ssm_clients[region] = boto3.client('ssm', region_name=region)
    return _ssm_clients[region]

def get_instance_ebs_throughput(instance_type: str, region: str = DEFAULT_REGION) -> float:
    """Get maximum EBS throughput for an instance type using boto3 API."""
    try:
        ec2 = get_ec2_client(region)
        
        # Map t2 instance types to t3 equivalents (same EBS throughput)
        query_instance_type = instance_type
        if instance_type.startswith('t2.'):
            query_instance_type = instance_type.replace('t2.', 't3.')
            logger.info(f"Debug - Mapping {instance_type} to {query_instance_type} for EBS throughput lookup")
        
        response = ec2.describe_instance_types(InstanceTypes=[query_instance_type])
        
        logger.info(f"Debug - describe_instance_types response for {query_instance_type}: {response}")
        
        if not response['InstanceTypes']:
            logger.warning(f"Debug - No InstanceTypes found for {query_instance_type}")
            return 0.0

        instance_data = response['InstanceTypes'][0]
        ebs_info = instance_data.get('EbsInfo', {})
        ebs_optimized_info = ebs_info.get('EbsOptimizedInfo')
        
        logger.info(f"Debug - EBS info for {query_instance_type}: EbsInfo={ebs_info}")
        logger.info(f"Debug - EBS optimized info for {query_instance_type}: EbsOptimizedInfo={ebs_optimized_info}")

        if ebs_optimized_info and 'MaximumThroughputInMBps' in ebs_optimized_info:
            throughput_mbps = ebs_optimized_info['MaximumThroughputInMBps']
            logger.info(f"Debug - Found MaximumThroughputInMBps for {instance_type} (via {query_instance_type}): {throughput_mbps}")
            return throughput_mbps
        else:
            logger.warning(f"Debug - No EbsOptimizedInfo or MaximumThroughputInMBps found for {query_instance_type}")
        
        return 0.0
    except Exception as e:
        logger.error(f"Error getting EBS throughput for {instance_type}: {e}")
        return 0.0

def estimate_parallel_initialization_time(volumes, instance_max_throughput_mbps):
    """
    Calculate estimated completion time for parallel volume initialization.
    
    Args:
        volumes: List of volumes with size_gb and max_throughput_mbps
        instance_max_throughput_mbps: Instance maximum EBS throughput in MB/s
    
    Returns:
        Estimated completion time in minutes
    """
    if not volumes:
        return 0.0
    
    # Sort volumes by size (smallest first for accurate completion order)
    remaining_volumes = [(v['size_gb'], v.get('max_throughput_mbps', 1000)) for v in volumes]
    remaining_volumes.sort(key=lambda x: x[0])
    
    total_time_seconds = 0.0
    
    while remaining_volumes:
        n = len(remaining_volumes)
        
        # Calculate current throughput per volume
        # Limited by either volume's max throughput or instance throughput divided by parallel count
        current_throughput_per_volume = min(
            min(v[1] for v in remaining_volumes),  # Minimum volume max throughput
            instance_max_throughput_mbps / n       # Instance throughput divided by parallel count
        )
        
        # Find time to complete the smallest volume
        smallest_size_gb = remaining_volumes[0][0]
        smallest_size_mb = smallest_size_gb * 1024  # Convert GB to MB
        
        time_for_smallest = smallest_size_mb / current_throughput_per_volume  # seconds
        
        # Update all volumes: subtract the amount processed during this time
        processed_mb_per_volume = current_throughput_per_volume * time_for_smallest
        processed_gb_per_volume = processed_mb_per_volume / 1024
        
        # Remove completed volumes and update remaining sizes
        updated_volumes = []
        for size_gb, max_throughput in remaining_volumes:
            remaining_size = size_gb - processed_gb_per_volume
            if remaining_size > 0.01:  # Keep volumes with more than 10MB remaining
                updated_volumes.append((remaining_size, max_throughput))
        
        remaining_volumes = updated_volumes
        total_time_seconds += time_for_smallest
    
    return total_time_seconds / 60  # Convert to minutes

# Device mapping script template (defined once at module level)
DEVICE_MAPPING_SCRIPT = '''#!/bin/bash
# Create device mapping for EBS volumes
echo "=== Detecting actual device names ==="
# Get lsblk output to check device naming convention
LSBLK_OUTPUT=$(lsblk -o NAME,SIZE,TYPE)
echo "Device listing:"
echo "$LSBLK_OUTPUT"

# Check if we have xvd* devices (Xen hypervisor type)
if echo "$LSBLK_OUTPUT" | grep -q "^xvd"; then
    echo "Detected xvd* device naming (Xen hypervisor type)"
    DEVICE_STYLE="xvd"
# Check if we have nvme* devices (Nitro instances)
elif echo "$LSBLK_OUTPUT" | grep -q "^nvme"; then
    echo "Detected nvme* device naming (Nitro instances)"
    DEVICE_STYLE="nvme"
    
    # Get device-to-volume mapping for nvme devices
    echo "Getting nvme device to volume mapping:"
    lsblk -o NAME,SERIAL
else
    echo "Using standard device naming"
    DEVICE_STYLE="standard"
fi

# Function to map AWS device name to actual device name
map_device_name() {
    local aws_device="$1"
    local volume_id="$2"
    
    case "$DEVICE_STYLE" in
        "xvd")
            # Convert AWS device names to xvd format for Xen hypervisor
            if [[ "$aws_device" =~ ^/dev/sd([a-z]+)$ ]]; then
                # Convert /dev/sdf to /dev/xvdf format
                actual_device="/dev/xvd${BASH_REMATCH[1]}"
                echo "$actual_device"
            elif [[ "$aws_device" =~ ^/dev/sd([a-z]+)([0-9]+)$ ]]; then
                # Convert /dev/sda1 to /dev/xvda format (remove partition number)
                actual_device="/dev/xvd${BASH_REMATCH[1]}"
                echo "$actual_device"
            elif [[ "$aws_device" =~ ^/dev/xvd ]]; then
                # Already in xvd format, use as-is
                echo "$aws_device"
            else
                echo "$aws_device"
            fi
            ;;
        "nvme")
            # Map volume ID to nvme device using serial number
            local volume_short="${volume_id#vol-}"  # Remove 'vol-' prefix
            local nvme_device=$(lsblk -o NAME,SERIAL | grep "$volume_short" | awk '{print "/dev/"$1}' | head -1)
            if [[ -n "$nvme_device" ]]; then
                echo "$nvme_device"
            else
                echo "$aws_device"  # fallback to AWS device name
            fi
            ;;
        *)
            # Standard device naming
            echo "$aws_device"
            ;;
    esac
}
'''

# Create FastMCP server instance
mcp = FastMCP("EBS Initialization Server")


@mcp.tool()
def get_instance_volumes(instance_id: str, region: str = DEFAULT_REGION) -> str:
    """
    Get all EBS volumes attached to an EC2 instance.
    
    Args:
        instance_id: EC2 instance ID (e.g., i-1234567890abcdef0)
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-west-2)
    
    Returns:
        JSON string containing volume information
    """
    try:
        ec2 = get_ec2_client(region)
        
        response = ec2.describe_volumes(
            Filters=[
                {'Name': 'attachment.instance-id', 'Values': [instance_id]}
            ]
        )
        
        volumes = []
        for volume in response['Volumes']:
            for attachment in volume['Attachments']:
                if attachment['InstanceId'] == instance_id:
                    snapshot_id = volume.get('SnapshotId', '')
                    needs_initialization = bool(snapshot_id)
                    
                    volumes.append({
                        'volume_id': volume['VolumeId'],
                        'device': attachment['Device'],
                        'size_gb': volume['Size'],
                        'volume_type': volume['VolumeType'],
                        'iops': volume.get('Iops', 'N/A'),
                        'encrypted': volume['Encrypted'],
                        'state': attachment['State'],
                        'attach_time': attachment['AttachTime'].isoformat() if attachment.get('AttachTime') else None,
                        'snapshot_id': snapshot_id if snapshot_id else None,
                        'needs_initialization': needs_initialization,
                        'initialization_reason': 'Created from snapshot' if needs_initialization else 'Blank volume (no initialization needed)'
                    })
        
        result = {
            "instance_id": instance_id,
            "region": region,
            "total_volumes": len(volumes),
            "volumes": volumes
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Failed to get volumes for instance {instance_id}: {str(e)}"


@mcp.tool()
def initialize_all_volumes(instance_id: str, method: str = "fio", region: str = DEFAULT_REGION) -> str:
    """
    Initialize all EBS volumes attached to an EC2 instance.
    
    Args:
        instance_id: EC2 instance ID
        method: Initialization method - 'fio' (recommended) or 'dd'
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-west-2)
    
    Returns:
        JSON string with initialization status and command ID
    """
    try:
        # First get volume and instance information
        ec2 = get_ec2_client(region)
        ssm = get_ssm_client(region)
        
        # Get instance type for throughput calculation
        instance_response = ec2.describe_instances(InstanceIds=[instance_id])
        instance_type = None
        for reservation in instance_response['Reservations']:
            for instance in reservation['Instances']:
                if instance['InstanceId'] == instance_id:
                    instance_type = instance['InstanceType']
                    break
        
        if not instance_type:
            return f"❌ Could not find instance type for {instance_id}"
        
        # Get instance maximum EBS throughput
        instance_max_throughput = get_instance_ebs_throughput(instance_type, region)
        logger.info(f"Debug - EBS throughput for {instance_type}: {instance_max_throughput} MB/s")
        
        # Get volumes
        response = ec2.describe_volumes(
            Filters=[
                {'Name': 'attachment.instance-id', 'Values': [instance_id]}
            ]
        )
        
        if not response['Volumes']:
            return f"❌ No EBS volumes found attached to instance {instance_id}"
        
        # Build initialization commands and collect volume information for estimation
        commands = []
        volume_info = []
        volumes_for_estimation = []
        
        # Add shebang to ensure bash execution
        commands.append("#!/bin/bash")
        
        # Install required tools first
        if method == 'fio':
            commands.append("echo '=== Installing fio ===' && (sudo yum install -y fio 2>/dev/null || sudo apt-get update && sudo apt-get install -y fio 2>/dev/null || sudo zypper install -y fio)")
        
        # Add device mapping script to find actual device names
        commands.append(DEVICE_MAPPING_SCRIPT + '\necho "Device mapping function ready"')
        
        # Collect volume information and build parallel commands
        parallel_commands = []
        
        for volume in response['Volumes']:
            for attachment in volume['Attachments']:
                if attachment['InstanceId'] == instance_id and attachment['State'] == 'attached':
                    # Only initialize volumes created from snapshots
                    snapshot_id = volume.get('SnapshotId', '')
                    if not snapshot_id:
                        logger.info(f"Skipping volume {volume['VolumeId']} - no snapshot ID (blank volume, no initialization needed)")
                        continue
                    
                    device = attachment['Device']
                    volume_id = volume['VolumeId']
                    size_gb = volume['Size']
                    
                    # Get volume max throughput from volume info
                    volume_max_throughput = volume.get('Throughput', 1000)  # Default 1000 MiB/s if not available
                    
                    volume_info.append({
                        'volume_id': volume_id,
                        'device': device,
                        'size_gb': size_gb,
                        'volume_type': volume['VolumeType'],
                        'snapshot_id': snapshot_id
                    })
                    
                    # Add to estimation data
                    volumes_for_estimation.append({
                        'size_gb': size_gb,
                        'max_throughput_mbps': volume_max_throughput
                    })
                    
                    if method == 'fio':
                        # Background fio command with device mapping
                        parallel_cmd = f"""(
ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo fio --filename="$ACTUAL_DEVICE" --rw=read --bs=1M --iodepth=32 \\
--ioengine=libaio --direct=1 --name=init-{volume_id} \\
--group_reporting && \\
echo "=== Completed {volume_id} ==="
) &"""
                    else:  # dd method
                        # Background dd command with device mapping
                        parallel_cmd = f"""(
ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo dd if="$ACTUAL_DEVICE" of=/dev/null bs=1M status=progress && \\
echo "=== Completed {volume_id} ==="
) &"""
                    
                    parallel_commands.append(parallel_cmd)
        
        # Create final command that runs all volumes in parallel
        if parallel_commands:
            parallel_script = f"""
# Start all volume initializations in parallel
{chr(10).join(parallel_commands)}

# Wait for all background jobs to complete
echo "=== Waiting for all {len(parallel_commands)} volume initializations to complete ==="
wait

echo "=== All volume initializations completed ==="
"""
            commands.append(parallel_script)
        
        # Count total volumes vs volumes needing initialization  
        total_volumes = len([vol for vol in response['Volumes'] for att in vol['Attachments'] if att['InstanceId'] == instance_id and att['State'] == 'attached'])
        volumes_with_snapshots = len(volume_info)
        volumes_without_snapshots = total_volumes - volumes_with_snapshots
        
        if not volume_info:
            if total_volumes > 0:
                return f"ℹ️ Instance {instance_id} has {total_volumes} volume(s), but none were created from snapshots. Only volumes created from snapshots need initialization."
            else:
                return f"❌ No attached volumes found for instance {instance_id}"
        
        # Calculate estimated completion time with debugging
        estimated_minutes = 0.0
        logger.info(f"Debug - Estimation input: volumes_for_estimation={volumes_for_estimation}, instance_max_throughput={instance_max_throughput}")
        
        if volumes_for_estimation and instance_max_throughput > 0:
            try:
                estimated_minutes = estimate_parallel_initialization_time(volumes_for_estimation, instance_max_throughput)
                logger.info(f"Debug - Estimated minutes calculated: {estimated_minutes}")
            except Exception as e:
                logger.error(f"Debug - Error in time estimation: {e}")
                estimated_minutes = 0.0
        else:
            logger.warning(f"Debug - Cannot calculate estimation: volumes_count={len(volumes_for_estimation) if volumes_for_estimation else 0}, throughput={instance_max_throughput}")
        
        # Execute via Systems Manager
        logger.info(f"Executing initialization for {len(volume_info)} volumes on {instance_id}")
        
        # Create simple comment (AWS limit: 100 characters)
        total_gb = sum(v['size_gb'] for v in volume_info)
        comment = f'EBS Init: {len(volume_info)}vol {total_gb}GB est:{round(estimated_minutes, 0)}m {method}'
        
        ssm_response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': commands,
                'executionTimeout': ['86400']  # 24 hours timeout
            },
            Comment=comment[:100]  # Ensure 100 character limit
        )
        
        command_id = ssm_response['Command']['CommandId']
        
        # Create summary message
        summary_msg = f"✅ Started initialization of {len(volume_info)} volume(s) using {method} method"
        if volumes_without_snapshots > 0:
            summary_msg += f" (skipped {volumes_without_snapshots} blank volume(s) that don't need initialization)"
        
        result = {
            "status": "initialization_started",
            "command_id": command_id,
            "instance_id": instance_id,
            "instance_type": instance_type,
            "instance_max_throughput_mbps": instance_max_throughput,
            "region": region,
            "method": method,
            "total_volumes": total_volumes,
            "volumes_initialized": len(volume_info),
            "volumes_skipped": volumes_without_snapshots,
            "volumes": volume_info,
            "estimated_completion_minutes": round(estimated_minutes, 1) if estimated_minutes > 0 else "Unable to calculate",
            "estimated_completion_time": f"{int(estimated_minutes // 60)}h {int(estimated_minutes % 60)}m" if estimated_minutes > 60 else f"{int(estimated_minutes)}m" if estimated_minutes > 0 else "Unable to calculate",
            "message": summary_msg,
            "next_steps": f"Use check_initialization_status with command_id: {command_id}"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Failed to initialize volumes for instance {instance_id}: {str(e)}"


@mcp.tool()
def check_initialization_status(command_id: str, region: str = DEFAULT_REGION) -> str:
    """
    Check the status of volume initialization.
    
    Args:
        command_id: Systems Manager command ID
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-east-1)
    
    Returns:
        JSON string with current status and progress information
    """
    try:
        ssm = get_ssm_client(region)
        
        # First get command details to find the instance ID
        command_invocations = ssm.list_command_invocations(
            CommandId=command_id,
            Details=True
        )
        
        if not command_invocations['CommandInvocations']:
            return f"❌ No command invocations found for command {command_id}"
        
        # Get the first (and usually only) invocation
        invocation = command_invocations['CommandInvocations'][0]
        instance_id = invocation['InstanceId']
        
        response = ssm.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        )
        
        # Get timing information from the invocation we already retrieved
        start_time = invocation.get('RequestedDateTime')
        
        # Try to parse estimation data from command comment
        estimation_data = {}
        comment = ""
        try:
            # Try to get comment from the invocation we already have
            if 'Comment' in invocation:
                comment = invocation.get('Comment', '')
            else:
                # Alternative: try list_commands
                commands_response = ssm.list_commands(CommandId=command_id)
                if commands_response['Commands']:
                    comment = commands_response['Commands'][0].get('Comment', '')
            
            logger.info(f"Debug - Comment content: '{comment}'")
            
            if comment:
                # Parse simple comment format: "EBS Init: 3vol 208GB est:14.0m fio"
                import re
                match = re.search(r'(\d+)vol (\d+)GB est:(\d+(?:\.\d+)?)m (\w+)', comment)
                if match:
                    estimation_data = {
                        "volumes_count": int(match.group(1)),
                        "total_gb": int(match.group(2)),
                        "estimated_minutes": float(match.group(3)),
                        "method": match.group(4)
                    }
                    logger.info(f"Debug - Parsed estimation data: {estimation_data}")
                else:
                    logger.warning(f"Debug - Comment regex did not match: '{comment}'")
            else:
                logger.warning("Debug - Comment is empty")
                
        except Exception as e:
            logger.warning(f"Could not parse estimation data from comment: {e}")
        
        # Calculate progress if initialization is in progress
        progress_info = {}
        if response['Status'] == 'InProgress' and start_time:
            try:
                from datetime import datetime, timezone
                import re
                
                # Parse start time with proper timezone handling
                if isinstance(start_time, str):
                    # Handle various timezone formats
                    if start_time.endswith('Z'):
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    elif '+' in start_time or '-' in start_time[-6:]:  # Check for timezone offset like +09:00
                        start_dt = datetime.fromisoformat(start_time)
                    elif start_time.endswith('UTC'):
                        start_dt = datetime.fromisoformat(start_time.replace('UTC', '')).replace(tzinfo=timezone.utc)
                    else:
                        # Assume UTC if no timezone info
                        start_dt = datetime.fromisoformat(start_time).replace(tzinfo=timezone.utc)
                else:
                    # If it's already a datetime object, ensure it has timezone info
                    if start_time.tzinfo is None:
                        start_dt = start_time.replace(tzinfo=timezone.utc)
                    else:
                        start_dt = start_time
                
                # Get reliable current UTC time from AWS (more accurate than system time)
                import time
                current_utc_timestamp = time.time()
                current_time = datetime.fromtimestamp(current_utc_timestamp, tz=timezone.utc)
                
                # Convert start time to UTC
                if start_dt.tzinfo is not None:
                    start_dt_utc = start_dt.astimezone(timezone.utc)
                else:
                    start_dt_utc = start_dt.replace(tzinfo=timezone.utc)
                
                elapsed_minutes = (current_time - start_dt_utc).total_seconds() / 60
                
                logger.info(f"Debug - Times: start_utc='{start_dt_utc}', current_utc='{current_time}', elapsed={elapsed_minutes:.1f}min")
                
                # Use estimation data from command comment if available
                if estimation_data and estimation_data.get('estimated_minutes', 0) > 0:
                    estimated_total_minutes = estimation_data['estimated_minutes']
                    progress_percentage = min(95, max(0, (elapsed_minutes / estimated_total_minutes) * 100)) if estimated_total_minutes > 0 else 0
                    
                    # Create progress bar (20 characters) - ensure non-negative
                    progress_chars = max(0, min(20, int(progress_percentage / 5)))  # 5% per character, clamp between 0-20
                    progress_bar = '█' * progress_chars + '░' * (20 - progress_chars)
                    
                    progress_info = {
                        "elapsed_minutes": round(elapsed_minutes, 1),
                        "estimated_total_minutes": estimated_total_minutes,
                        "estimated_remaining_minutes": round(max(0, estimated_total_minutes - elapsed_minutes), 1),
                        "progress_percentage": round(progress_percentage, 1),
                        "progress_bar": f"[{progress_bar}] {progress_percentage:.1f}%",
                        "volumes_count": estimation_data.get('volumes_count', 0),
                        "total_gb": estimation_data.get('total_gb', 0),
                        "method": estimation_data.get('method', 'Unknown')
                    }
                else:
                    # Fallback: try to extract from stdout logs
                    stdout_content = response.get('StandardOutputContent', '')
                    volume_pattern = r'Starting initialization of (\w+-\w+) \(.*?, (\d+)GB\)'
                    volume_matches = re.findall(volume_pattern, stdout_content)
                    
                    if volume_matches:
                        # Estimate based on volumes found in logs
                        total_gb = sum(int(match[1]) for match in volume_matches)
                        estimated_total_minutes = (total_gb * 1024) / (100 * len(volume_matches)) / 60  # Rough estimate
                        progress_percentage = min(95, (elapsed_minutes / estimated_total_minutes) * 100) if estimated_total_minutes > 0 else 0
                        
                        progress_chars = int(progress_percentage / 5)
                        progress_bar = '█' * progress_chars + '░' * (20 - progress_chars)
                        
                        progress_info = {
                            "elapsed_minutes": round(elapsed_minutes, 1),
                            "estimated_total_minutes": round(estimated_total_minutes, 1),
                            "estimated_remaining_minutes": round(max(0, estimated_total_minutes - elapsed_minutes), 1),
                            "progress_percentage": round(progress_percentage, 1),
                            "progress_bar": f"[{progress_bar}] {progress_percentage:.1f}%",
                            "volumes_detected": len(volume_matches),
                            "total_gb_detected": total_gb,
                            "note": "Estimated from log analysis"
                        }
                    else:
                        # No estimation data available
                        progress_info = {
                            "elapsed_minutes": round(elapsed_minutes, 1),
                            "estimated_total_minutes": "Calculating...",
                            "progress_percentage": "Unknown",
                            "progress_bar": "[████████████████████] Analyzing...",
                            "note": "Volume information not yet available in logs"
                        }
                    
            except Exception as e:
                logger.warning(f"Could not calculate progress: {e}")
                progress_info = {"error": "Unable to calculate progress"}
        
        # Use the comment we already retrieved for debugging
        comment_debug = comment
        
        result = {
            "command_id": command_id,
            "instance_id": instance_id,
            "status": response['Status'],
            "execution_start_time": str(start_time) if start_time else str(response.get('ExecutionStartDateTime', '')) if response.get('ExecutionStartDateTime') else None,
        }
        
        # Add progress info as individual fields right after execution_start_time
        if progress_info:
            result["progress_percentage"] = progress_info.get("progress_percentage", "Unknown")
            result["progress_bar"] = progress_info.get("progress_bar", "[░░░░░░░░░░░░░░░░░░░░] 0.0%")
            result["estimated_remaining_minutes"] = progress_info.get("estimated_remaining_minutes", "Unknown")
            result["elapsed_minutes"] = progress_info.get("elapsed_minutes", 0)
            result["estimated_total_minutes"] = progress_info.get("estimated_total_minutes", "Unknown")
            result["volumes_count"] = progress_info.get("volumes_count", 0)
            result["total_gb"] = progress_info.get("total_gb", 0)
            result["method"] = progress_info.get("method", "Unknown")
        
        # Add remaining fields
        result["execution_end_time"] = str(response.get('ExecutionEndDateTime', '')) if response.get('ExecutionEndDateTime') else None
        result["stdout_preview"] = response.get('StandardOutputContent', '')[:500] + ('...' if len(response.get('StandardOutputContent', '')) > 500 else '')
        result["stderr_preview"] = response.get('StandardErrorContent', '')[:500] + ('...' if len(response.get('StandardErrorContent', '')) > 500 else '')
        
        # Add status interpretation with progress bar display
        if response['Status'] == 'Success':
            result['message'] = '✅ Volume initialization completed successfully'
        elif response['Status'] == 'InProgress':
            if progress_info and 'progress_percentage' in progress_info:
                progress_pct = progress_info.get('progress_percentage', 0)
                result['message'] = f'🔄 {progress_pct}% Complete... (Actual initialization time may vary depending on environment. This is for reference only.)'
            else:
                result['message'] = '🔄 Volume initialization is still in progress (Actual initialization time may vary depending on environment. This is for reference only.)'
        elif response['Status'] == 'Failed':
            result['message'] = '❌ Volume initialization failed'
        elif response['Status'] == 'Cancelled':
            result['message'] = '⚠️  Volume initialization was cancelled'
        elif response['Status'] == 'TimedOut':
            result['message'] = '⏰ Volume initialization timed out'
        else:
            result['message'] = f'ℹ️  Volume initialization status: {response["Status"]}'
        
        # Return text-based format for better AI agent compatibility
        if response['Status'] == 'InProgress' and progress_info:
            elapsed = progress_info.get('elapsed_minutes', 0)
            remaining = progress_info.get('estimated_remaining_minutes', 0)
            volumes = progress_info.get('volumes_count', 0)
            total_gb = progress_info.get('total_gb', 0)
            method = progress_info.get('method', 'Unknown')
            progress_pct = progress_info.get('progress_percentage', 0)
            progress_bar = progress_info.get('progress_bar', '[░░░░░░░░░░░░░░░░░░░░] 0.0%')
            
            text_result = f"""Status: {response['Status']}
Progress: {progress_bar}
Elapsed: {elapsed} minutes
Estimated remaining: {remaining} minutes
Volumes: {volumes} 
Size: {total_gb}GB
Method: {method}
Instance: {instance_id}
Started: {result.get('execution_start_time', 'Unknown')}

Note: Actual initialization time may vary depending on environment. This is for reference only."""
            
            return text_result
        
        elif response['Status'] == 'Success':
            return f"""Status: Completed Successfully ✅
Command ID: {command_id}
Instance ID: {instance_id}
Start Time: {result.get('execution_start_time', 'Unknown')}
End Time: {result.get('execution_end_time', 'Unknown')}"""
        
        else:
            return f"""Status: {response['Status']}
Message: {result.get('message', 'No additional information')}
Command ID: {command_id}
Instance ID: {instance_id}"""
        
    except Exception as e:
        return f"❌ Failed to check status for command {command_id}: {str(e)}"



@mcp.tool()
def cancel_initialization(command_id: str, region: str = DEFAULT_REGION) -> str:
    """
    Cancel an ongoing volume initialization by cancelling the Systems Manager command and killing child processes.
    
    Args:
        command_id: Systems Manager command ID to cancel
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-east-1)
    
    Returns:
        JSON string with cancellation status
    """
    try:
        ssm = get_ssm_client(region)
        
        # First get command details to find the instance ID
        command_invocations = ssm.list_command_invocations(
            CommandId=command_id,
            Details=True
        )
        
        if not command_invocations['CommandInvocations']:
            return f"❌ No command invocations found for command {command_id}"
        
        invocation = command_invocations['CommandInvocations'][0]
        instance_id = invocation['InstanceId']
        
        # Send cleanup command to kill child processes before cancelling
        cleanup_commands = [
            "#!/bin/bash",
            "echo '=== Killing fio processes ==='",
            "kill -9 `ps -ef | grep 'fio --filename' | grep -v grep | awk '{print $2}'` 2>/dev/null || echo 'No fio processes found'",
            "echo '=== Killing dd processes ==='", 
            "kill -9 `ps -ef | grep 'dd if=' | grep -v grep | awk '{print $2}'` 2>/dev/null || echo 'No dd processes found'",
            "echo '=== Process cleanup completed ==='",
            "ps -ef | grep -E '(fio|dd)' | grep -v grep || echo 'No initialization processes remaining'"
        ]
        
        # Execute cleanup command
        cleanup_response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': cleanup_commands,
                'executionTimeout': ['60']  # 1 minute timeout for cleanup
            },
            Comment=f'EBS Volume Initialization Cleanup - Cancel {command_id}'
        )
        
        cleanup_command_id = cleanup_response['Command']['CommandId']
        
        # Cancel the original command
        cancel_response = ssm.cancel_command(CommandId=command_id)
        
        result = {
            "status": "cancellation_requested",
            "command_id": command_id,
            "cleanup_command_id": cleanup_command_id,
            "instance_id": instance_id,
            "region": region,
            "message": "✅ Volume initialization cancellation requested with process cleanup",
            "actions_taken": [
                "Sent kill command for fio processes",
                "Sent kill command for dd processes", 
                "Cancelled original SSM command"
            ],
            "note": "Child processes (fio/dd) have been forcefully terminated. Use check_initialization_status to verify the final status.",
            "next_steps": f"Use check_initialization_status with command_id: {command_id}"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Failed to cancel initialization command {command_id}: {str(e)}"


@mcp.tool()
def initialize_volume_by_id(volume_id: str, method: str = "fio", region: str = DEFAULT_REGION) -> str:
    """
    Initialize a specific EBS volume by its volume ID.
    
    Args:
        volume_id: EBS volume ID (e.g., vol-1234567890abcdef0)
        method: Initialization method - 'fio' (recommended) or 'dd'
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-west-2)
    
    Returns:
        JSON string with initialization status and command ID
    """
    try:
        ec2 = get_ec2_client(region)
        ssm = get_ssm_client(region)
        
        # Get volume information
        response = ec2.describe_volumes(VolumeIds=[volume_id])
        
        if not response['Volumes']:
            return f"❌ Volume {volume_id} not found in region {region}"
        
        volume = response['Volumes'][0]
        
        # Check if volume is attached
        if not volume['Attachments']:
            return f"❌ Volume {volume_id} is not attached to any instance"
        
        attachment = volume['Attachments'][0]
        if attachment['State'] != 'attached':
            return f"❌ Volume {volume_id} is not in 'attached' state (current state: {attachment['State']})"
        
        instance_id = attachment['InstanceId']
        device = attachment['Device']
        size_gb = volume['Size']
        volume_type = volume['VolumeType']
        
        # Get instance type for throughput calculation
        instance_response = ec2.describe_instances(InstanceIds=[instance_id])
        instance_type = None
        for reservation in instance_response['Reservations']:
            for instance in reservation['Instances']:
                if instance['InstanceId'] == instance_id:
                    instance_type = instance['InstanceType']
                    break
        
        if not instance_type:
            return f"❌ Could not find instance type for {instance_id}"
        
        # Get instance maximum EBS throughput
        instance_max_throughput = get_instance_ebs_throughput(instance_type, region)
        logger.info(f"Debug - EBS throughput for {instance_type}: {instance_max_throughput} MB/s")
        
        # Build initialization commands
        commands = []
        
        # Add shebang to ensure bash execution
        commands.append("#!/bin/bash")
        
        # Install required tools first
        if method == 'fio':
            commands.append("echo '=== Installing fio ===' && (sudo yum install -y fio 2>/dev/null || sudo apt-get update && sudo apt-get install -y fio 2>/dev/null || sudo zypper install -y fio)")
        
        # Add device mapping script
        commands.append(DEVICE_MAPPING_SCRIPT + '\necho "Device mapping function ready"')
        
        # Create initialization command for the specific volume with device mapping
        if method == 'fio':
            init_cmd = f"""ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo fio --filename="$ACTUAL_DEVICE" --rw=read --bs=1M --iodepth=32 \\
--ioengine=libaio --direct=1 --name=init-{volume_id} \\
--group_reporting && \\
echo "=== Completed {volume_id} ====" """
        else:  # dd method
            init_cmd = f"""ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo dd if="$ACTUAL_DEVICE" of=/dev/null bs=1M status=progress && \\
echo "=== Completed {volume_id} ====" """
        
        commands.append(init_cmd)
        
        # Calculate estimated completion time for single volume
        estimated_minutes = 0.0
        if instance_max_throughput > 0:
            # Single volume initialization time calculation
            volume_max_throughput = volume.get('Throughput', 1000)  # Default 1000 MiB/s if not available
            effective_throughput = min(volume_max_throughput, instance_max_throughput)
            
            # Calculate time: size_gb * 1024 MB/GB / throughput_mb_per_second / 60 seconds/minute
            estimated_minutes = (size_gb * 1024) / effective_throughput / 60
            logger.info(f"Debug - Single volume estimation: {size_gb}GB, throughput={effective_throughput}MB/s, estimated={estimated_minutes:.1f}min")
        else:
            logger.warning(f"Debug - Cannot calculate estimation for single volume: throughput={instance_max_throughput}")
        
        # Execute via Systems Manager
        logger.info(f"Executing initialization for volume {volume_id} on instance {instance_id}")
        
        # Create simple comment (AWS limit: 100 characters)
        comment = f'EBS Init: 1vol {size_gb}GB est:{round(estimated_minutes, 0)}m {method}'
        
        ssm_response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': commands,
                'executionTimeout': ['86400']  # 24 hours timeout
            },
            Comment=comment[:100]  # Ensure 100 character limit
        )
        
        command_id = ssm_response['Command']['CommandId']
        
        result = {
            "status": "initialization_started",
            "command_id": command_id,
            "volume_id": volume_id,
            "instance_id": instance_id,
            "instance_type": instance_type,
            "instance_max_throughput_mbps": instance_max_throughput,
            "device": device,
            "size_gb": size_gb,
            "volume_type": volume_type,
            "region": region,
            "method": method,
            "estimated_completion_minutes": round(estimated_minutes, 1) if estimated_minutes > 0 else "Unable to calculate",
            "estimated_completion_time": f"{int(estimated_minutes // 60)}h {int(estimated_minutes % 60)}m" if estimated_minutes > 60 else f"{int(estimated_minutes)}m" if estimated_minutes > 0 else "Unable to calculate",
            "message": f"✅ Started initialization of volume {volume_id} ({size_gb}GB) using {method} method",
            "next_steps": f"Use check_initialization_status with command_id: {command_id}"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Failed to initialize volume {volume_id}: {str(e)}"


if __name__ == "__main__":
    mcp.run()