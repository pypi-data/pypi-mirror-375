"""
EBS Volume Initialization Command Generation Module

This module handles the generation of shell commands for initializing EBS volumes
using different methods (fio or dd) and managing parallel execution.
"""

import logging
from typing import List, Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils import DEVICE_MAPPING_SCRIPT, get_install_command

logger = logging.getLogger(__name__)


def create_fio_command(volume_id: str, device: str, size_gb: int) -> str:
    """
    Create a fio command for volume initialization.
    
    Args:
        volume_id: EBS volume ID
        device: AWS device path
        size_gb: Volume size in GB
        
    Returns:
        Shell command string for fio initialization
    """
    return f"""(
ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo fio --filename="$ACTUAL_DEVICE" --rw=read --bs=1M --iodepth=32 \\
--ioengine=libaio --direct=1 --name=init-{volume_id} \\
--group_reporting && \\
echo "=== Completed {volume_id} ==="
) &"""


def create_dd_command(volume_id: str, device: str, size_gb: int) -> str:
    """
    Create a dd command for volume initialization.
    
    Args:
        volume_id: EBS volume ID
        device: AWS device path
        size_gb: Volume size in GB
        
    Returns:
        Shell command string for dd initialization
    """
    return f"""(
ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo dd if="$ACTUAL_DEVICE" of=/dev/null bs=1M status=progress && \\
echo "=== Completed {volume_id} ==="
) &"""


def create_single_volume_command(volume_id: str, device: str, size_gb: int, method: str) -> str:
    """
    Create initialization command for a single volume (non-parallel).
    
    Args:
        volume_id: EBS volume ID
        device: AWS device path
        size_gb: Volume size in GB
        method: Initialization method ('fio' or 'dd')
        
    Returns:
        Shell command string for single volume initialization
    """
    if method == 'fio':
        return f"""ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo fio --filename="$ACTUAL_DEVICE" --rw=read --bs=1M --iodepth=32 \\
--ioengine=libaio --direct=1 --name=init-{volume_id} \\
--group_reporting && \\
echo "=== Completed {volume_id} ====" """
    else:  # dd method
        return f"""ACTUAL_DEVICE=$(map_device_name "{device}" "{volume_id}")
echo "=== Volume {volume_id}: AWS device {device} mapped to actual device $ACTUAL_DEVICE ===" && \\
echo "=== Starting initialization of {volume_id} ($ACTUAL_DEVICE, {size_gb}GB) ===" && \\
sudo dd if="$ACTUAL_DEVICE" of=/dev/null bs=1M status=progress && \\
echo "=== Completed {volume_id} ====" """


def build_initialization_commands(volume_list: List[Dict[str, Any]], method: str, 
                                parallel: bool = True) -> List[str]:
    """
    Build complete initialization command list for volumes.
    
    Args:
        volume_list: List of volume information dictionaries
        method: Initialization method ('fio' or 'dd')
        parallel: Whether to run volumes in parallel
        
    Returns:
        List of shell command strings
    """
    commands = []
    
    # Add shebang
    commands.append("#!/bin/bash")
    
    # Add package installation if needed
    install_cmd = get_install_command(method)
    if install_cmd:
        commands.append(install_cmd)
    
    # Add device mapping script
    commands.append(DEVICE_MAPPING_SCRIPT + '\\necho "Device mapping function ready"')
    
    if parallel and len(volume_list) > 1:
        # Create parallel commands
        parallel_commands = []
        for volume in volume_list:
            if method == 'fio':
                cmd = create_fio_command(volume['volume_id'], volume['device'], volume['size_gb'])
            else:
                cmd = create_dd_command(volume['volume_id'], volume['device'], volume['size_gb'])
            parallel_commands.append(cmd)
        
        # Create final parallel script
        parallel_script = f"""
# Start all volume initializations in parallel
{chr(10).join(parallel_commands)}

# Wait for all background jobs to complete
echo "=== Waiting for all {len(parallel_commands)} volume initializations to complete ==="
wait

echo "=== All volume initializations completed ==="
"""
        commands.append(parallel_script)
    
    else:
        # Create sequential commands for single volume or when parallel is disabled
        for volume in volume_list:
            cmd = create_single_volume_command(volume['volume_id'], volume['device'], 
                                             volume['size_gb'], method)
            commands.append(cmd)
    
    return commands


def create_process_cleanup_commands() -> List[str]:
    """
    Create commands to clean up initialization processes.
    
    Returns:
        List of cleanup command strings
    """
    return [
        "#!/bin/bash",
        "echo '=== Killing fio processes ==='",
        "kill -9 `ps -ef | grep 'fio --filename' | grep -v grep | awk '{print $2}'` 2>/dev/null || echo 'No fio processes found'",
        "echo '=== Killing dd processes ==='", 
        "kill -9 `ps -ef | grep 'dd if=' | grep -v grep | awk '{print $2}'` 2>/dev/null || echo 'No dd processes found'",
        "echo '=== Process cleanup completed ==='"
    ]