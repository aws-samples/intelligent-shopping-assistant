from constructs import Construct
import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnParameter,
    Aws,
    Duration,
    aws_secretsmanager,
    aws_sagemaker as _sagemaker,
    aws_iam as _iam
)
import sagemaker
import boto3
import json
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer


region = os.getenv('AWS_REGION', '')

class NotebookStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str,search_engine_key: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # get value from opensearch stack
          
        host_url =  "https://"+search_engine_key+"/"
        
        # pass host to secret manager for notebook
        host_url_secret = aws_secretsmanager.Secret(self, "OpenSearchHostURLSecret",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
            secret_string_template=json.dumps({"host": host_url}),
            generate_string_key="urlkey",
        ),
        secret_name = "opensearch-host-url"
        )
        #get index from context
        index_name = self.node.try_get_context("index")
        #generate secret of index name for notebook
        index_name_secret = aws_secretsmanager.Secret(self, "OpenSearchIndexNameSecret", 
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
            secret_string_template=json.dumps({"index": index_name}),
            generate_string_key="indexkey",
        ),
        secret_name = "opensearch-index-name"
        )                                                      
        # set role for sagemaker notebook       
        self.notebook_job_role =  _iam.Role(
            self,'ShoppingGuideNotebookRole',
            assumed_by=_iam.ServicePrincipal('sagemaker.amazonaws.com'),
            description =' IAM role for notebook job',
        )
        self.notebook_job_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        self.notebook_job_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSageMakerFullAccess'))
        self.notebook_job_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('SecretsManagerReadWrite'))
        self.notebook_job_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'))
        self.notebook_job_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonPersonalizeFullAccess'))
        self.notebook_job_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('IAMFullAccess'))

        print('Deploying SageMaker via Notebook...')
        self.createNotebookInstanceByCDK()         

    def createNotebookInstanceByCDK(self):
        notebook_lifecycle = _sagemaker.CfnNotebookInstanceLifecycleConfig(
            self, f'SmartSearch-LifeCycleConfig',
            notebook_instance_lifecycle_config_name='ss-config',
            on_create=[_sagemaker.CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty(
                content=cdk.Fn.base64(f"""
                    #!/bin/bash
                    cd home/ec2-user/SageMaker
                    git clone -b jupyter --single-branch https://github.com/paulhebo/intelligent_shopping_guide.git
                    chmod -R 777 ./

                """)
            )]
        )
        cfn_notebook_instance = _sagemaker.CfnNotebookInstance(self,"ShoppingGuideNotebook",
        notebook_instance_name="ShoppingGuideNotebook",
        role_arn=self.notebook_job_role.role_arn,
        instance_type="ml.t3.xlarge",
        lifecycle_config_name='ss-config',
        volume_size_in_gb=100)



    