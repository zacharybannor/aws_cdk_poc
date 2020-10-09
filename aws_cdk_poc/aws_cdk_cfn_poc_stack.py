import os
from datetime import datetime
from aws_cdk import core
from vmd_core_constructs.vmd_core_cfn_constructs import VMDCoreCfnBucket


class AwsCdkPocCfnStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_stack(self):

        now = datetime.now().strftime('%Y-%m-%d %S')
        VMDCoreCfnBucket(self, id=os.getenv('cfn_s3_id'), bucket_name=os.getenv('cfn_s3_name') + now)