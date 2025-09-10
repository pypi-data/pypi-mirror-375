from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    Stack,
    Fn,
    CfnOutput,
)
from constructs import Construct


class AlbListenerRuleStack(Construct):
    """CDK Construct for creating ALB listener rules with host-based routing."""
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        *,
        target_group_arn: str,
        ecs_stack_name: str,
        listener_priority: int, 
        host_name: str,  
        **kwargs
    ):
        """
        Initialize ALB Listener Rule Stack.
        
        Args:
            scope: The scope in which to define this construct
            construct_id: The scoped construct ID
            target_group_arn: ARN of the target group to forward traffic to
            ecs_stack_name: Name of the ECS stack that exports the ALB listener ARN
            listener_priority: Priority for the listener rule (1-50000)
            host_name: Host header value to match for routing
        """
        super().__init__(scope, construct_id, **kwargs)

        listener_arn = Fn.import_value(
            Fn.sub("${ECSStackName}-ALBListenerHTTPS", {
                "ECSStackName": ecs_stack_name
            })
        )

        # Create the listener rule
        self.listener_rule = elbv2.CfnListenerRule(
            self, "AlbListenerRule",
            listener_arn=listener_arn,
            priority=listener_priority,
            conditions=[
                elbv2.CfnListenerRule.RuleConditionProperty(
                    field="host-header",
                    values=[host_name]
                )
            ],
            actions=[
                elbv2.CfnListenerRule.ActionProperty(
                    type="forward",
                    target_group_arn=target_group_arn
                )
            ],
        )
        
        # Outputs
        CfnOutput(
            self, "AlbListenerRuleArn",
            value=self.listener_rule.ref,
            export_name=f"{Stack.of(self).stack_name}-AlbListenerRuleArn",
            description="ARN of the created ALB listener rule"
        )
        CfnOutput(
            self, "AlbListenerRulePriority",
            value=str(self.listener_rule.priority),
            export_name=f"{Stack.of(self).stack_name}-AlbListenerRulePriority",
            description="Priority of the created ALB listener rule"
        )