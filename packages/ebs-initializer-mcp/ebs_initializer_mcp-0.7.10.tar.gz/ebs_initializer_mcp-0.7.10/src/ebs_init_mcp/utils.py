"""
Utility Functions Module

This module contains utility functions and constants used across the EBS initialization system,
including device mapping scripts and common helper functions.
"""

# Device mapping script template for handling different EC2 instance types
# This script detects the device naming convention and provides mapping functions
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


def get_install_command(method: str) -> str:
    """
    Get the package installation command for the specified initialization method.
    
    Args:
        method: Initialization method ('fio' or 'dd')
        
    Returns:
        Shell command to install required packages
    """
    if method == 'fio':
        return ("echo '=== Installing fio ===' && "
                "(sudo yum install -y fio 2>/dev/null || "
                "sudo apt-get update && sudo apt-get install -y fio 2>/dev/null || "
                "sudo zypper install -y fio)")
    else:
        # dd is typically pre-installed, no installation needed
        return "echo '=== dd is pre-installed, no additional packages needed ==="


def needs_initialization(volume_info: dict) -> bool:
    """
    Determine if a volume needs initialization based on snapshot information.
    
    Args:
        volume_info: Volume information from AWS API
        
    Returns:
        True if volume needs initialization, False otherwise
    """
    snapshot_id = volume_info.get('SnapshotId', '')
    return bool(snapshot_id)


def get_initialization_reason(volume_info: dict) -> str:
    """
    Get human-readable reason for initialization requirement.
    
    Args:
        volume_info: Volume information from AWS API
        
    Returns:
        Reason string explaining why volume needs/doesn't need initialization
    """
    if needs_initialization(volume_info):
        return 'Created from snapshot'
    else:
        return 'Blank volume (no initialization needed)'


def create_volume_summary(volume_info: dict) -> dict:
    """
    Create a summary dictionary for a volume with relevant initialization info.
    
    Args:
        volume_info: Raw volume information from AWS API
        attachment: Volume attachment information from AWS API
        
    Returns:
        Dictionary with summarized volume information
    """
    # Assume the volume has attachments (this should be validated by caller)
    attachment = volume_info['Attachments'][0] if volume_info['Attachments'] else {}
    
    snapshot_id = volume_info.get('SnapshotId', '')
    needs_init = bool(snapshot_id)
    
    return {
        'volume_id': volume_info['VolumeId'],
        'device': attachment.get('Device', 'Unknown'),
        'size_gb': volume_info['Size'],
        'volume_type': volume_info['VolumeType'],
        'iops': volume_info.get('Iops', 'N/A'),
        'encrypted': volume_info['Encrypted'],
        'state': attachment.get('State', 'Unknown'),
        'attach_time': attachment.get('AttachTime').isoformat() if attachment.get('AttachTime') else None,
        'snapshot_id': snapshot_id if snapshot_id else None,
        'needs_initialization': needs_init,
        'initialization_reason': get_initialization_reason(volume_info)
    }