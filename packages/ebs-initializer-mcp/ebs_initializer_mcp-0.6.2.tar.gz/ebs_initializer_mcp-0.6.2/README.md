# EBS Initialization MCP Server

A Model Context Protocol (MCP) server for automating AWS EBS volume initialization. This server provides tools to initialize EBS volumes attached to EC2 instances using AWS Systems Manager.

## Features

- 🔍 **Volume Discovery**: Automatically discover all EBS volumes attached to an EC2 instance
- 🚀 **Automated Initialization**: Initialize volumes using `fio` (recommended) or `dd`
- ⏱️ **Smart Time Estimation**: Predict completion time with parallel processing simulation
- 📊 **Progress Monitoring**: Check initialization status and view detailed logs
- ❌ **Cancellation Support**: Cancel ongoing initialization with process cleanup
- 🌐 **Multi-Region Support**: Works across all AWS regions
- 🔒 **Secure Execution**: Uses AWS Systems Manager for secure remote execution

## Installation

### Using uvx (Recommended)

```bash
# Run directly without installation (latest version)
uvx ebs-initializer-mcp@latest

# Or run specific version
uvx ebs-initializer-mcp==0.6.0

# Install globally
uv tool install ebs-initializer-mcp

# Upgrade to latest version
uvx --upgrade ebs-initializer-mcp
```

### From GitHub

```bash
uvx --from git+https://github.com/username/ebs-init-mcp.git ebs-mcp-server
```

## Usage

### As MCP Server

Add to your MCP configuration (`mcp_config.json`):

```json
{
  "mcpServers": {
    "ebs-initializer": {
      "command": "uvx",
      "args": ["ebs-initializer-mcp@latest"],
      "env": {
        "AWS_REGION": "us-west-2"
      }
    }
  }
}
```

### Available Tools

1. **get_instance_volumes**: Get all EBS volumes attached to an instance
2. **initialize_all_volumes**: Initialize all volumes on an instance (parallel processing with time estimation)
3. **initialize_volume_by_id**: Initialize a specific volume by its volume ID
4. **check_initialization_status**: Monitor initialization progress and view detailed logs
5. **cancel_initialization**: Cancel ongoing initialization with complete process cleanup

### Example Usage with Claude Code

```
"Initialize all EBS volumes for instance i-1234567890abcdef0 using fio"
"Initialize volume vol-1234567890abcdef0 using fio"
"Check the status of the newly attached volume vol-abcdef1234567890"
"Cancel the initialization command 12345678-1234-1234-1234-123456789012"
```

The MCP server will:
1. Discover all attached EBS volumes and calculate estimated completion time
2. Install fio on the target instance
3. Run initialization commands in parallel with real-time throughput optimization
4. Provide detailed status updates with progress logs
5. Allow cancellation with complete process cleanup if needed

## Prerequisites

- AWS CLI configured with appropriate permissions
- EC2 instances must have Systems Manager agent installed
- **Supported Operating Systems:**
  - Amazon Linux 2
  - Amazon Linux 2023
  - Red Hat Enterprise Linux (RHEL)
  - Ubuntu (18.04, 20.04, 22.04, 24.04)
  - SUSE Linux Enterprise Server (SLES)
- Required IAM permissions:
  - `ec2:DescribeVolumes`
  - `ssm:SendCommand`
  - `ssm:GetCommandInvocation`

## AWS IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVolumes",
                "ssm:SendCommand",
                "ssm:GetCommandInvocation"
            ],
            "Resource": "*"
        }
    ]
}
```

## Configuration

### Environment Variables

The server automatically detects AWS region from environment variables:

```bash
# Option 1: AWS_DEFAULT_REGION (preferred)
export AWS_DEFAULT_REGION=ap-northeast-2

# Option 2: AWS_REGION (also supported)  
export AWS_REGION=ap-northeast-2
```

**Priority order:**
1. `AWS_DEFAULT_REGION` environment variable
2. `AWS_REGION` environment variable  
3. Fallback to `us-east-1`

### MCP Configuration

```json
{
  "mcpServers": {
    "ebs-initializer": {
      "command": "uvx",
      "args": ["ebs-initializer-mcp@latest"],
      "env": {
        "AWS_DEFAULT_REGION": "ap-northeast-2"
      }
    }
  }
}
```

## Development

```bash
git clone <repository>
cd ebs-init-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## License

MIT License
