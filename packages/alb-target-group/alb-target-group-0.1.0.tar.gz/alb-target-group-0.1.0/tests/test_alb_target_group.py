import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template, Match
from alb_target_group.alb_target_group_stack import TargetGroupStack

class TestTargetGroupStack:
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.app = App()
        self.stack = Stack(self.app, "TestStack")
        
    def test_target_group_creation_with_default_values(self):
        """Test target group creation with default configuration"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="test-ecs-stack",
            health_check_path="/health",
            channel="prod",
            port=80,
            protocol="HTTP",
            max_request_duration=300,
            health_threshold_count=3,
            health_check_timeout_seconds=5,
            health_check_interval_seconds=30
        )
        
        template = Template.from_stack(self.stack)
        template.has_resource_properties("AWS::ElasticLoadBalancingV2::TargetGroup", {
            "Port": 80,
            "Protocol": "HTTP",
            "HealthCheckPath": "/health",
            "HealthCheckIntervalSeconds": 30,
            "HealthCheckTimeoutSeconds": 5,
            "HealthyThresholdCount": 3
        })
        
    def test_target_group_with_dev_channel(self):
        """Test target group with dev channel sets deregistration delay to 0"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="test-ecs-stack",
            health_check_path="/health",
            channel="dev",
            port=8080,
            protocol="HTTP",
            max_request_duration=300,
            health_threshold_count=2,
            health_check_timeout_seconds=10,
            health_check_interval_seconds=60
        )
        
        template = Template.from_stack(self.stack)
        # Check that the target group has the conditional deregistration delay
        template.has_resource_properties("AWS::ElasticLoadBalancingV2::TargetGroup", {
            "TargetGroupAttributes": [
                {
                    "Key": "deregistration_delay.timeout_seconds",
                    "Value": {
                        "Fn::If": [
                            Match.any_value(),  # Accept any condition name
                            "0",
                            "300"
                        ]
                    }
                }
            ]
        })
        
    def test_target_group_with_https_protocol(self):
        """Test target group with HTTPS protocol"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="test-ecs-stack",
            health_check_path="/api/health",
            channel="staging",
            port=443,
            protocol="HTTPS",
            max_request_duration=600,
            health_threshold_count=5,
            health_check_timeout_seconds=15,
            health_check_interval_seconds=45
        )
        
        template = Template.from_stack(self.stack)
        template.has_resource_properties("AWS::ElasticLoadBalancingV2::TargetGroup", {
            "Port": 443,
            "Protocol": "HTTPS",
            "HealthCheckProtocol": "HTTPS"
        })
        
    def test_target_group_exports_arn(self):
        """Test that target group ARN is exported"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="test-ecs-stack",
            health_check_path="/health",
            channel="prod",
            port=80,
            protocol="HTTP",
            max_request_duration=300,
            health_threshold_count=3,
            health_check_timeout_seconds=5,
            health_check_interval_seconds=30
        )
        
        template = Template.from_stack(self.stack)
        # Check that an output exists with the correct export name pattern
        template_json = template.to_json()
        outputs = template_json.get("Outputs", {})
        
        # Find an output with the expected export name
        export_found = False
        for output_id, output_config in outputs.items():
            if ("Export" in output_config and 
                "Name" in output_config["Export"] and 
                "TestStack-TargetGroupArn" in output_config["Export"]["Name"]):
                export_found = True
                break
        
        assert export_found, f"No output found with export name containing 'TestStack-TargetGroupArn'. Available outputs: {outputs}"
        
    def test_vpc_import_from_ecs_stack(self):
        """Test that VPC ID is imported from ECS stack"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="my-ecs-stack",
            health_check_path="/health",
            channel="prod",
            port=80,
            protocol="HTTP",
            max_request_duration=300,
            health_threshold_count=3,
            health_check_timeout_seconds=5,
            health_check_interval_seconds=30
        )
        
        template = Template.from_stack(self.stack)
        # Verify that Fn::ImportValue is used with correct stack name
        template.has_resource_properties("AWS::ElasticLoadBalancingV2::TargetGroup", {
            "VpcId": {
                "Fn::ImportValue": {
                    "Fn::Sub": ["${ECSStackName}-VPC", {"ECSStackName": "my-ecs-stack"}]
                }
            }
        })
        
    def test_health_check_matcher_configuration(self):
        """Test health check matcher is set to 200-299"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="test-ecs-stack",
            health_check_path="/health",
            channel="prod",
            port=80,
            protocol="HTTP",
            max_request_duration=300,
            health_threshold_count=3,
            health_check_timeout_seconds=5,
            health_check_interval_seconds=30
        )
        
        template = Template.from_stack(self.stack)
        template.has_resource_properties("AWS::ElasticLoadBalancingV2::TargetGroup", {
            "Matcher": {
                "HttpCode": "200-299"
            }
        })
        
    def test_target_group_attributes_non_dev_channel(self):
        """Test target group attributes for non-dev channels"""
        target_group = TargetGroupStack(
            self.stack, "TestTargetGroup",
            ecs_stack_name="test-ecs-stack",
            health_check_path="/health",
            channel="prod",
            port=80,
            protocol="HTTP",
            max_request_duration=600,
            health_threshold_count=3,
            health_check_timeout_seconds=5,
            health_check_interval_seconds=30
        )
        
        template = Template.from_stack(self.stack)
        template.has_resource_properties("AWS::ElasticLoadBalancingV2::TargetGroup", {
            "TargetGroupAttributes": [
                {
                    "Key": "deregistration_delay.timeout_seconds",
                    "Value": {
                        "Fn::If": [
                            Match.any_value(),  # Accept any condition name
                            "0",
                            "600"
                        ]
                    }
                }
            ]
        })