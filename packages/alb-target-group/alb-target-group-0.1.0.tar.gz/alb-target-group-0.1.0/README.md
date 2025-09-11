# AWS CDK Target Group

An AWS CDK construct for creating Application Load Balancer (ALB) Target Groups with health checks and conditional deregistration delays.

## Overview

This CDK construct creates an Elastic Load Balancing V2 Target Group with the following features:

- **VPC Integration**: Imports VPC from an existing ECS stack
- **Health Checks**: Configurable HTTP health checks with custom paths
- **Conditional Logic**: Different deregistration delays for dev vs production environments
- **Flexible Configuration**: Parameterized port, protocol, and health check settings

## Features

- ✅ HTTP/HTTPS protocol support
- ✅ Customizable health check endpoints
- ✅ Environment-specific deregistration delays (0s for dev, configurable for prod)
- ✅ Health check status codes 200-299
- ✅ Configurable health check intervals and timeouts
- ✅ CloudFormation outputs for target group ARN

## Usage

```python
from aws_cdk import Stack
from constructs import Construct
from alb_target_group import TargetGroupStack

class MyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        target_group = TargetGroupStack(
            self, "MyTargetGroup",
            ecs_stack_name="my-ecs-stack",
            health_check_path="/api/health",
            channel="prod",  # or "dev"
            port=80,
            protocol="HTTP",
            max_request_duration=300,
            health_threshold_count=2,
            health_check_timeout_seconds=5,
            health_check_interval_seconds=10
        )
```

## Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ecs_stack_name` | string | Name of the ECS stack to import VPC from |
| `health_check_path` | string | Path for health check endpoint (e.g., `/api/health`) |
| `channel` | string | Environment channel (`dev` or `prod`) |
| `port` | int | Target group port (e.g., 80, 443) |
| `protocol` | string | Protocol (`HTTP` or `HTTPS`) |
| `max_request_duration` | int | Max request duration in seconds (used for non-dev deregistration delay) |
| `health_threshold_count` | int | Number of consecutive successful health checks required |
| `health_check_timeout_seconds` | int | Health check timeout in seconds |
| `health_check_interval_seconds` | int | Health check interval in seconds |

## Environment Behavior

- **Dev Environment** (`channel="dev"`): Deregistration delay is set to 0 seconds for faster deployments
- **Production Environment** (any other channel): Deregistration delay uses the `max_request_duration` value

## Outputs

The construct exports:
- `TargetGroupArn`: The ARN of the created target group

## Requirements

- AWS CDK v2
- Python 3.7+