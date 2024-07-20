from constructs import Construct
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

class UserInfoStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # configure the lambda role
        _user_info_role_policy = iam.PolicyStatement(
            actions=[
                'lambda:AWSLambdaBasicExecutionRole'
            ],
            resources=['*']
        )
        user_info_role = iam.Role(
            self, 'user_info_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        user_info_role.add_to_policy(_user_info_role_policy)

        user_info_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        user_info_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        
        # add user info lambda
        user_info_layer = _lambda.LayerVersion(
          self, 'IRLambdaLayer',
          code=_lambda.Code.from_asset('../lambda/lambda_layer_folder'),
          compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
          description='IR Library'
        )
        
        function_name = 'get_user_info'
        user_info_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=user_info_role,
            layers=[user_info_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=100
        )

        qa_api = apigw.RestApi(self, 'get-user-info-api',
                               default_cors_preflight_options=apigw.CorsOptions(
                                   allow_origins=apigw.Cors.ALL_ORIGINS,
                                   allow_methods=apigw.Cors.ALL_METHODS
                               ),
                               endpoint_types=[apigw.EndpointType.REGIONAL]
                               )
                               
        user_info_integration = apigw.LambdaIntegration(
            user_info_function,
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

        user_info_resource = qa_api.root.add_resource(
            'user_info',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        user_info_resource.add_method(
            'GET',
            user_info_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
