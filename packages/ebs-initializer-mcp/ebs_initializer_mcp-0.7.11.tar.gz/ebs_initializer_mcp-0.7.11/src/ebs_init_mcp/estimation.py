"""
Initialization Time Estimation Module

This module provides functions to estimate EBS volume initialization times
based on volume sizes, throughput characteristics, and parallelization.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def estimate_parallel_initialization_time(volumes: List[Dict[str, Any]], 
                                        instance_max_throughput_mbps: float) -> float:
    """
    Calculate estimated completion time for parallel volume initialization.
    
    This function simulates the parallel initialization process by considering
    that each volume processes at its maximum throughput (up to instance limits).
    When volumes complete, the simulation continues with remaining volumes.
    
    Args:
        volumes: List of volumes with size_gb and max_throughput_mbps
        instance_max_throughput_mbps: Instance maximum EBS throughput in MB/s
    
    Returns:
        Estimated completion time in minutes
    """
    if not volumes or instance_max_throughput_mbps <= 0:
        return 0.0
    
    # Create list of remaining volumes with their current size and max throughput
    remaining_volumes = [(v['size_gb'], v.get('max_throughput_mbps', 1000)) for v in volumes]
    
    total_time_seconds = 0.0
    
    while remaining_volumes:
        # Check if total throughput demand exceeds instance limit
        total_throughput_demand = sum(throughput for _, throughput in remaining_volumes)
        
        if total_throughput_demand <= instance_max_throughput_mbps:
            # Each volume can use its maximum throughput
            volume_throughputs = [throughput for _, throughput in remaining_volumes]
        else:
            # AWS EBS allocation logic: smaller throughput volumes get priority
            n = len(remaining_volumes)
            fair_share = instance_max_throughput_mbps / n
            
            volume_throughputs = []
            remaining_instance_throughput = instance_max_throughput_mbps
            volumes_needing_fair_share = []
            
            # First pass: allocate full throughput to volumes smaller than fair share
            for i, (_, vol_throughput) in enumerate(remaining_volumes):
                if vol_throughput <= fair_share:
                    volume_throughputs.append(vol_throughput)
                    remaining_instance_throughput -= vol_throughput
                else:
                    volume_throughputs.append(0)  # Placeholder
                    volumes_needing_fair_share.append(i)
            
            # Second pass: distribute remaining throughput among larger volumes
            if volumes_needing_fair_share and remaining_instance_throughput > 0:
                throughput_per_large_volume = remaining_instance_throughput / len(volumes_needing_fair_share)
                for i in volumes_needing_fair_share:
                    volume_throughputs[i] = throughput_per_large_volume
            elif not volumes_needing_fair_share and remaining_instance_throughput > 0:
                # All volumes are smaller than fair share - they already got their full throughput
                pass
        
        # Calculate completion time for each volume at current throughput
        completion_times = []
        for i, (size_gb, _) in enumerate(remaining_volumes):
            size_mb = size_gb * 1024
            time_seconds = size_mb / volume_throughputs[i] if volume_throughputs[i] > 0 else float('inf')
            completion_times.append(time_seconds)
        
        # Find the shortest completion time (first volume to complete)
        min_completion_time = min(completion_times)
        
        # Update all volumes: subtract the amount processed during this time
        updated_volumes = []
        for i, (size_gb, max_throughput) in enumerate(remaining_volumes):
            processed_mb = volume_throughputs[i] * min_completion_time
            processed_gb = processed_mb / 1024
            remaining_size = size_gb - processed_gb
            
            # Keep volumes with more than 10MB remaining
            if remaining_size > 0.01:
                updated_volumes.append((remaining_size, max_throughput))
        
        remaining_volumes = updated_volumes
        total_time_seconds += min_completion_time
        
        logger.info(f"Debug - Parallel step: {len(remaining_volumes)} volumes remaining, "
                   f"step_time={min_completion_time/60:.1f}min, total_time={total_time_seconds/60:.1f}min")
    
    return total_time_seconds / 60  # Convert to minutes


def estimate_single_volume_time(size_gb: int, volume_throughput: float, 
                               instance_throughput: float) -> float:
    """
    Calculate estimated initialization time for a single volume.
    
    Args:
        size_gb: Volume size in gigabytes
        volume_throughput: Volume maximum throughput in MB/s
        instance_throughput: Instance maximum throughput in MB/s
        
    Returns:
        Estimated initialization time in minutes
    """
    if size_gb <= 0 or volume_throughput <= 0 or instance_throughput <= 0:
        return 0.0
        
    # Effective throughput is limited by the minimum of volume and instance throughput
    effective_throughput = min(volume_throughput, instance_throughput)
    
    # Calculate time: size_gb * 1024 MB/GB / throughput_mb_per_second / 60 seconds/minute
    estimated_minutes = (size_gb * 1024) / effective_throughput / 60
    
    logger.info(f"Debug - Single volume estimation: {size_gb}GB, "
                f"effective_throughput={effective_throughput}MB/s, "
                f"estimated={estimated_minutes:.1f}min")
    
    return estimated_minutes


def format_estimated_time(minutes: float) -> str:
    """
    Format estimated time into human-readable string.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Formatted time string (e.g., "5m", "1h 30m")
    """
    if minutes <= 0:
        return "Unable to calculate"
        
    if minutes < 60:
        return f"{int(minutes)}m"
    else:
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        return f"{hours}h {remaining_minutes}m"


def create_estimation_comment(volume_count: int, total_gb: int, 
                            estimated_minutes: float, method: str) -> str:
    """
    Create a compact comment for SSM command with estimation data.
    
    Args:
        volume_count: Number of volumes
        total_gb: Total size in GB
        estimated_minutes: Estimated time in minutes
        method: Initialization method (fio/dd)
        
    Returns:
        Formatted comment string (max 100 characters for AWS limit)
    """
    comment = f'EBS Init: {volume_count}vol {total_gb}GB est:{round(estimated_minutes, 0)}m {method}'
    return comment[:100]  # Ensure AWS 100 character limit