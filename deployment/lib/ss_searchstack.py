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

class ProductSearchStack(Stack):

    def __init__(self, scope: Construct, id: str,search_engine_key: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        index = self.node.try_get_context("index")
        embedding_endpoint_name = self.node.try_get_context("embedding_endpoint_name")
        language = self.node.try_get_context("language")
        host = search_engine_key
        
        # configure the lambda role
        _product_search_role_policy = iam.PolicyStatement(
            actions=[
                'sagemaker:InvokeEndpointAsync',
                'sagemaker:InvokeEndpoint',
                'sagemaker:ListEndpoints',
                'lambda:AWSLambdaBasicExecutionRole',
                'lambda:InvokeFunction',
                'secretsmanager:SecretsManagerReadWrite',
                'es:ESHttpPost',
                'bedrock:*',
                'execute-api:*'
            ],
            resources=['*']
        )
        product_search_role = iam.Role(
            self, 'product_search_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        product_search_role.add_to_policy(_product_search_role_policy)

        product_search_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )

        product_search_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
        )

        product_search_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        
        # add product search lambda
        product_search_layer = _lambda.LayerVersion(
          self, 'IRLambdaLayer',
          code=_lambda.Code.from_asset('../lambda/lambda_layer_folder'),
          compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
          description='IR Library'
        )
        
        function_name = 'product_search'
        product_search_function = _lambda.Function(
            self, function_name,
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_9,
            role=product_search_role,
            layers=[product_search_layer],
            code=_lambda.Code.from_asset('../lambda/' + function_name),
            handler='lambda_function' + '.lambda_handler',
            timeout=Duration.minutes(10),
            reserved_concurrent_executions=100
        )
        product_search_function.add_environment("host", host)
        product_search_function.add_environment("index", index)
        product_search_function.add_environment("language", language)
        product_search_function.add_environment("embedding_endpoint_name", embedding_endpoint_name)

        qa_api = apigw.RestApi(self, 'product-search-api',
                               default_cors_preflight_options=apigw.CorsOptions(
                                   allow_origins=apigw.Cors.ALL_ORIGINS,
                                   allow_methods=apigw.Cors.ALL_METHODS
                               ),
                               endpoint_types=[apigw.EndpointType.REGIONAL]
                               )
                               
        product_search_integration = apigw.LambdaIntegration(
            product_search_function,
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

        product_search_resource = qa_api.root.add_resource(
            'product_search',
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=apigw.Cors.ALL_ORIGINS)
        )

        product_search_resource.add_method(
            'GET',
            product_search_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
