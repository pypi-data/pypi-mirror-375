import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template, Match
from alb_listener_rule import AlbListenerRuleStack


def test_alb_listener_rule_creation():
    """Test that AlbListenerRuleStack can be created with required parameters."""
    app = App()
    stack = Stack(app, "TestStack")
    
    listener_rule = AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    # Test that the construct was created successfully
    assert listener_rule is not None
    assert listener_rule.node.id == "TestListenerRule"
    assert listener_rule.listener_rule is not None
    assert listener_rule.listener_rule.priority == 100


def test_alb_listener_rule_template():
    """Test that the CloudFormation template contains the expected resources."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    # Generate CloudFormation template
    template = Template.from_stack(stack)
    
    # Check that a listener rule is created
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 100,
        "Conditions": [
            {
                "Field": "host-header",
                "Values": ["api.example.com"]
            }
        ]
    })
    
    # Check that outputs are created (using pattern matching since logical IDs are auto-generated)
    template.has_output("*", {
        "Description": "ARN of the created ALB listener rule"
    })
    
    template.has_output("*", {
        "Description": "Priority of the created ALB listener rule"
    })


def test_alb_listener_rule_template_comprehensive():
    """Test the complete CloudFormation template structure."""
    app = App()
    stack = Stack(app, "TestStack")
    
    AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    template = Template.from_stack(stack)
    
    # Verify the listener rule has correct properties
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "ListenerArn": {
            "Fn::ImportValue": {
                "Fn::Sub": [
                    "${ECSStackName}-ALBListenerHTTPS",
                    {
                        "ECSStackName": "test-ecs-stack"
                    }
                ]
            }
        },
        "Priority": 100,
        "Conditions": [
            {
                "Field": "host-header",
                "Values": ["api.example.com"]
            }
        ],
        "Actions": [
            {
                "Type": "forward",
                "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890"
            }
        ]
    })
    
    # Count resources to ensure we have exactly what we expect
    template.resource_count_is("AWS::ElasticLoadBalancingV2::ListenerRule", 1)


def test_alb_listener_rule_with_different_host():
    """Test that the construct works with different host names."""
    app = App()
    stack = Stack(app, "TestStack")
    
    listener_rule = AlbListenerRuleStack(
        stack, "TestListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/test-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=200,
        host_name="www.example.com"
    )
    
    template = Template.from_stack(stack)
    
    # Verify the host header condition
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 200,
        "Conditions": [
            {
                "Field": "host-header",
                "Values": ["www.example.com"]
            }
        ]
    })


def test_multiple_listener_rules():
    """Test that multiple listener rules can be created in the same stack."""
    app = App()
    stack = Stack(app, "TestStack")
    
    # Create two different listener rules
    AlbListenerRuleStack(
        stack, "ApiListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=100,
        host_name="api.example.com"
    )
    
    AlbListenerRuleStack(
        stack, "WebListenerRule",
        target_group_arn="arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/1234567890",
        ecs_stack_name="test-ecs-stack",
        listener_priority=200,
        host_name="www.example.com"
    )
    
    template = Template.from_stack(stack)
    
    # Should have exactly 2 listener rules
    template.resource_count_is("AWS::ElasticLoadBalancingV2::ListenerRule", 2)
    
    # Verify both rules exist with different priorities
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 100
    })
    
    template.has_resource_properties("AWS::ElasticLoadBalancingV2::ListenerRule", {
        "Priority": 200
    })