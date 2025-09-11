from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    Stack,
    Fn,
    CfnCondition,
    CfnParameter,
    CfnOutput
)
from constructs import Construct


class TargetGroupStack(Construct):
    def __init__(
            self, scope: Construct, construct_id: str,  
            ecs_stack_name: str,
            health_check_path: str,
            channel: str,
            port: int,
            protocol: str,
            max_request_duration: int,
            health_threshold_count: int,
            health_check_timeout_seconds: int,
            health_check_interval_seconds: int,
            **kwargs
        ):
        super().__init__(scope, construct_id, **kwargs)

        # Import VPC ID from ECS stack exports
        target_vpc_id = Fn.import_value(
            Fn.sub("${ECSStackName}-VPC", {
                "ECSStackName": ecs_stack_name
            })
        )

        # Condition: if channel is dev
        if_dev_channel = CfnCondition(
            self, "IfDevChannel",
            expression=Fn.condition_equals(channel, "dev")
        )

        # Create Target Group
        target_group = elbv2.CfnTargetGroup(
            self, "TargetGroup",
            vpc_id=target_vpc_id,
            port=port,
            protocol=protocol,
            matcher=elbv2.CfnTargetGroup.MatcherProperty(
                http_code="200-299"
            ),
            health_check_interval_seconds=health_check_interval_seconds,
            health_check_path=health_check_path,
            health_check_protocol=protocol,
            health_check_timeout_seconds=health_check_timeout_seconds,
            healthy_threshold_count=health_threshold_count,
            target_group_attributes=[
                elbv2.CfnTargetGroup.TargetGroupAttributeProperty(
                    key="deregistration_delay.timeout_seconds",
                    value=Fn.condition_if(
                        if_dev_channel.logical_id,
                        "0",
                        str(max_request_duration)
                    ).to_string()
                )
            ]
        )
        CfnOutput(
            self, "TargetGroupArn",
            value=target_group.ref,
            export_name=f"{Stack.of(self).stack_name}-TargetGroupArn"
        )
        self.target_group_arn = target_group.ref