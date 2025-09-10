# AWS CDK Public Listener Role

A CDK construct for creating Application Load Balancer (ALB) listener rules that route traffic based on host headers to target groups.

## Overview

This module provides a reusable CDK construct (`AlbListenerRuleStack`) that creates ALB listener rules for routing HTTP/HTTPS traffic to specific target groups based on host header conditions.

## Features

- Creates ALB listener rules with host-based routing
- Configurable priority for rule evaluation order
- Integrates with existing ALB listeners via CloudFormation exports
- Outputs rule ARN and priority for cross-stack references

## Usage

```python
from alb_listener_rule.alb_listener_rule_stack import AlbListenerRuleStack

# Create listener rule in your CDK stack
listener_rule = AlbListenerRuleStack(
    self, "MyListenerRule",
    target_group_arn="arn:aws:elasticloadbalancing:region:account:targetgroup/my-tg/1234567890",
    ecs_stack_name="my-ecs-stack",
    listener_priority=100,
    host_name="api.example.com"
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_group_arn` | str | ARN of the target group to forward traffic to |
| `ecs_stack_name` | str | Name of the ECS stack that exports the ALB listener ARN |
| `listener_priority` | int | Priority for the listener rule (1-50000, lower = higher priority) |
| `host_name` | str | Host header value to match for routing |

## Prerequisites

- An existing ALB with HTTPS listener that exports its ARN as `${ECSStackName}-ALBListenerHTTPS`
- A target group (e.g., ECS service target group) to route traffic to

## Outputs

The construct exports the following CloudFormation outputs:

- `${StackName}-AlbListenerRuleArn`: ARN of the created listener rule
- `${StackName}-AlbListenerRulePriority`: Priority of the created listener rule

## Example Scenario

This construct is useful when you have:
1. An ECS cluster with an ALB
2. Multiple services that need different routing rules
3. Requirements to route traffic based on domain/subdomain

## File Structure

```
aws_cdk-public-listener-role/
├── README.md
└── alb_listener_rule/