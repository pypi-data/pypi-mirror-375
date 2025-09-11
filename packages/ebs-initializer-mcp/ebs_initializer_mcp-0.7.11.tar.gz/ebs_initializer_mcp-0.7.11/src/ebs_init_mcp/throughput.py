"""
EBS Throughput Calculation Module

This module handles EBS throughput calculations for different instance types,
including special handling for t2 instances by mapping them to t3 equivalents.
"""

import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from aws_clients import get_ec2_client, DEFAULT_REGION

logger = logging.getLogger(__name__)


def get_instance_ebs_throughput(instance_type: str, region: str = DEFAULT_REGION) -> float:
    """
    Get maximum EBS throughput for an instance type using boto3 API.
    
    Args:
        instance_type: EC2 instance type (e.g., 't2.large', 'm5.xlarge')
        region: AWS region name
        
    Returns:
        Maximum EBS throughput in MB/s, or 0.0 if unable to determine
    """
    try:
        ec2 = get_ec2_client(region)
        
        # Map t2 instance types to t3 equivalents (same EBS throughput)
        # t2 instances don't appear in describe_instance_types API responses
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


def get_volume_throughput(volume_info: dict, default: float = 1000.0) -> float:
    """
    Get volume throughput from volume information.
    
    Args:
        volume_info: Volume information dictionary from AWS API
        default: Default throughput if not available
        
    Returns:
        Volume throughput in MB/s
    """
    return volume_info.get('Throughput', default)


def calculate_effective_throughput(volume_throughput: float, instance_throughput: float, 
                                  parallel_count: int = 1) -> float:
    """
    Calculate effective throughput considering volume, instance, and parallelism constraints.
    
    Args:
        volume_throughput: Volume maximum throughput in MB/s
        instance_throughput: Instance maximum throughput in MB/s
        parallel_count: Number of volumes being processed in parallel
        
    Returns:
        Effective throughput per volume in MB/s
    """
    if parallel_count <= 0:
        return 0.0
        
    # Limited by either volume's max throughput or instance throughput divided by parallel count
    return min(volume_throughput, instance_throughput / parallel_count)