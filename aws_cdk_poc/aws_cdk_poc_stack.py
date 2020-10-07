from aws_cdk import core
from vmd_core_constructs.vmd_core_constructs import VMDCoreS3, VMDCoreVPC, VMDCoreFargateService
import os
from datetime import datetime


class AwsCdkPocStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_stack(self):

        self.bucket = VMDCoreS3(self, id=os.getenv('s3_id'),
                                bucket_name=os.getenv('s3_name') + datetime.now().strftime('%S'))

        self.vpc = VMDCoreVPC(self, id=os.getenv('vpc_id'))

        self.fargate_service = VMDCoreFargateService(self, id=os.getenv('fargate_id'),
                                                     image=os.getenv('fargate_image'),
                                                     ecs_cluster=None, vpc=self.vpc)


