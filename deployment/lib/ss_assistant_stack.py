from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    Duration

)
import os

class AssistantStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # llm_endpoint_name = self.node.try_get_context("llm_endpoint_name")
        # language = self.node.try_get_context("language")
        
        # configure the lambda role
        _assistant_role_policy = iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'lambda:AWSLambdaBasicExecutionRole',
                'lambda:InvokeFunction',
                's3:AmazonS3FullAccess',
                'bedrock:*'
            ],
            resources=['*']
        )
        assistant_role = iam.Role(
            self, 'assistant_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        assistant_role.add_to_policy(_assistant_role_policy)

        assistant_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )


        
        # add intelligent recommendation lambda
        assistant_layer = _lambda.LayerVersion(
          self, 'IRLambdaLayer',
          code=_lambda.Code.from_asset('../lambda/lambda_layer_folder'),
          compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
          description='IR Library'
        )
        
        function_name = 'assistant'
        assistant_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=assistant_role,
            layers=[assistant_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=100
        )

        # assistant_function.add_environment("language", language)
        # assistant_function.add_environment("llm_endpoint_name", llm_endpoint_name)


        assistant_api = apigw.RestApi(self, 'assistant-api',
                               default_cors_preflight_options=apigw.CorsOptions(
                                   allow_origins=apigw.Cors.ALL_ORIGINS,
                                   allow_methods=apigw.Cors.ALL_METHODS
                               ),
                               endpoint_types=[apigw.EndpointType.REGIONAL]
                               )
                               
        assistant_integration = apigw.LambdaIntegration(
            assistant_function,
            proxy=True,
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )

        assistant_resource = assistant_api.root.add_resource(
            'assistant',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        assistant_resource.add_method(
            'GET',
            assistant_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )