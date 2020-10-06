from aws_cdk import core
from vmd_core_constructs.vmd_core_constructs import VMDCoreS3


class AwsCdkPocStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_stack(self):

        self.bucket = VMDCoreS3(self, id='test-s3-bucket', bucket_name='test-s3-bucket')
