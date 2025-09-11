"""
AWS Client Management Module

This module provides cached boto3 clients for EC2 and SSM services
to improve performance by avoiding repeated client initialization.
"""

import os
import boto3

# Get default region from environment variable
DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', os.getenv('AWS_REGION', 'us-east-1'))

# Client caches
_ec2_clients = {}
_ssm_clients = {}


def get_ec2_client(region: str = DEFAULT_REGION):
    """
    Get or create EC2 client for the specified region.
    
    Args:
        region: AWS region name
        
    Returns:
        boto3.client: EC2 client instance
    """
    if region not in _ec2_clients:
        _ec2_clients[region] = boto3.client('ec2', region_name=region)
    return _ec2_clients[region]


def get_ssm_client(region: str = DEFAULT_REGION):
    """
    Get or create SSM client for the specified region.
    
    Args:
        region: AWS region name
        
    Returns:
        boto3.client: SSM client instance
    """
    if region not in _ssm_clients:
        _ssm_clients[region] = boto3.client('ssm', region_name=region)
    return _ssm_clients[region]


def clear_client_cache():
    """Clear all cached clients (useful for testing)."""
    global _ec2_clients, _ssm_clients
    _ec2_clients.clear()
    _ssm_clients.clear()