#!/usr/bin/env python3
"""
EBS Volume Initialization FastMCP Server

This FastMCP server provides tools for automatically initializing AWS EBS volumes
attached to EC2 instances using AWS Systems Manager.
"""

import json
import logging
from typing import Dict, List, Any

from mcp.server.fastmcp import FastMCP

# Import our modularized components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from aws_clients import get_ec2_client, get_ssm_client, DEFAULT_REGION
from throughput import get_instance_ebs_throughput
from estimation import (
    estimate_parallel_initialization_time, 
    estimate_single_volume_time, 
    format_estimated_time,
    create_estimation_comment
)
from utils import create_volume_summary, needs_initialization
from initialization import build_initialization_commands, create_process_cleanup_commands
from status import (
    get_command_status,
    parse_estimation_from_comment,
    calculate_elapsed_time,
    calculate_progress_info,
    format_status_message,
    format_text_response
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("EBS Initialization Server")


@mcp.tool()
def get_instance_volumes(instance_id: str, region: str = DEFAULT_REGION) -> str:
    """
    Get all EBS volumes attached to an EC2 instance.
    
    Args:
        instance_id: EC2 instance ID (e.g., i-1234567890abcdef0)
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-east-1)
    
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
                    volumes.append(create_volume_summary(volume))
        
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
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-east-1)
    
    Returns:
        JSON string with initialization status and command ID
    """
    try:
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
        
        # Filter volumes that need initialization and collect information
        volume_info = []
        volumes_for_estimation = []
        
        for volume in response['Volumes']:
            for attachment in volume['Attachments']:
                if (attachment['InstanceId'] == instance_id and 
                    attachment['State'] == 'attached' and 
                    needs_initialization(volume)):
                    
                    volume_summary = create_volume_summary(volume)
                    volume_info.append(volume_summary)
                    
                    # Add to estimation data
                    volumes_for_estimation.append({
                        'size_gb': volume['Size'],
                        'max_throughput_mbps': volume.get('Throughput', 1000)
                    })
        
        # Count total volumes vs volumes needing initialization  
        total_volumes = sum(1 for vol in response['Volumes'] 
                          for att in vol['Attachments'] 
                          if att['InstanceId'] == instance_id and att['State'] == 'attached')
        volumes_without_snapshots = total_volumes - len(volume_info)
        
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
        
        # Build initialization commands
        commands = build_initialization_commands(volume_info, method, parallel=True)
        
        # Execute via Systems Manager
        logger.info(f"Executing initialization for {len(volume_info)} volumes on {instance_id}")
        
        # Create comment with estimation data
        total_gb = sum(v['size_gb'] for v in volume_info)
        comment = create_estimation_comment(len(volume_info), total_gb, estimated_minutes, method)
        
        ssm_response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': commands,
                'executionTimeout': ['86400']  # 24 hours timeout
            },
            Comment=comment
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
            "estimated_completion_time": format_estimated_time(estimated_minutes),
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
        Text string with current status and progress information
    """
    # Get command status
    status_data, error = get_command_status(command_id, region)
    if error:
        return error
    
    response = status_data['response']
    invocation = status_data['invocation']
    instance_id = status_data['instance_id']
    
    # Get timing information
    start_time = invocation.get('RequestedDateTime')
    
    # Try to get end time from various sources
    end_time = response.get('EndDateTime') or invocation.get('EndDateTime')
    
    # If not found, check CommandPlugins
    if not end_time and 'CommandPlugins' in invocation:
        plugins = invocation['CommandPlugins']
        if plugins and len(plugins) > 0:
            end_time = plugins[0].get('ResponseFinishDateTime')
    
    # Debug: confirm end time extraction
    logger.info(f"Debug - Start time: {start_time}")
    logger.info(f"Debug - End time: {end_time}")
    logger.info(f"Debug - Response status: {response.get('Status')}")
    
    # Parse estimation data from command comment
    comment = invocation.get('Comment', '') or ""
    estimation_data = parse_estimation_from_comment(comment)
    
    # Calculate progress if initialization is in progress
    progress_info = None
    if response['Status'] == 'InProgress' and start_time:
        try:
            elapsed_minutes = calculate_elapsed_time(start_time)
            progress_info = calculate_progress_info(elapsed_minutes, estimation_data)
        except Exception as e:
            logger.warning(f"Could not calculate progress: {e}")
    
    # Format and return text response
    execution_start_time = str(start_time) if start_time else "Unknown"
    execution_end_time = str(end_time) if end_time else None
    return format_text_response(response['Status'], progress_info, instance_id, execution_start_time, execution_end_time)


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
        
        # Get command status first
        status_data, error = get_command_status(command_id, region)
        if error:
            return error
        
        instance_id = status_data['instance_id']
        
        # Cancel the original command
        try:
            ssm.cancel_command(CommandId=command_id, InstanceIds=[instance_id])
            logger.info(f"Cancelled command {command_id} on instance {instance_id}")
        except Exception as e:
            logger.warning(f"Could not cancel command {command_id}: {e}")
        
        # Send cleanup commands to kill any running processes
        cleanup_commands = create_process_cleanup_commands()
        
        cleanup_response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': cleanup_commands,
                'executionTimeout': ['300']  # 5 minutes timeout
            },
            Comment='EBS Init Cleanup - Kill initialization processes'
        )
        
        cleanup_command_id = cleanup_response['Command']['CommandId']
        
        result = {
            "status": "cancellation_requested",
            "original_command_id": command_id,
            "cleanup_command_id": cleanup_command_id,
            "instance_id": instance_id,
            "region": region,
            "message": "✅ Cancellation requested. Cleanup command sent to terminate initialization processes.",
            "next_steps": f"Monitor cleanup with command_id: {cleanup_command_id}"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Failed to cancel initialization for command {command_id}: {str(e)}"


@mcp.tool()
def initialize_volume_by_id(volume_id: str, method: str = "fio", region: str = DEFAULT_REGION) -> str:
    """
    Initialize a specific EBS volume by its volume ID.
    
    Args:
        volume_id: EBS volume ID (e.g., vol-1234567890abcdef0)
        method: Initialization method - 'fio' (recommended) or 'dd'
        region: AWS region name (default: from AWS_DEFAULT_REGION or AWS_REGION env var, fallback to us-east-1)
    
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
        
        # Calculate estimated completion time for single volume
        estimated_minutes = 0.0
        if instance_max_throughput > 0:
            volume_max_throughput = volume.get('Throughput', 1000)
            estimated_minutes = estimate_single_volume_time(size_gb, volume_max_throughput, instance_max_throughput)
        else:
            logger.warning(f"Debug - Cannot calculate estimation for single volume: throughput={instance_max_throughput}")
        
        # Build initialization commands for single volume
        volume_info = [{'volume_id': volume_id, 'device': device, 'size_gb': size_gb}]
        commands = build_initialization_commands(volume_info, method, parallel=False)
        
        # Execute via Systems Manager
        logger.info(f"Executing initialization for volume {volume_id} on instance {instance_id}")
        
        # Create comment with estimation data
        comment = create_estimation_comment(1, size_gb, estimated_minutes, method)
        
        ssm_response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': commands,
                'executionTimeout': ['86400']  # 24 hours timeout
            },
            Comment=comment
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
            "estimated_completion_time": format_estimated_time(estimated_minutes),
            "message": f"✅ Started initialization of volume {volume_id} ({size_gb}GB) using {method} method",
            "next_steps": f"Use check_initialization_status with command_id: {command_id}"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Failed to initialize volume {volume_id}: {str(e)}"


if __name__ == "__main__":
    mcp.run()