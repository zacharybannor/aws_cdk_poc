from aws_cdk import core
from vmd_core_constructs.core_constructs import InfutorCoreS3, InfutorCoreEc2
from datetime import datetime
import os


class InfutorAirflowStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_stack(self):

        bucket = InfutorCoreS3(self, id=os.getenv('s3_id'),
                               bucket_name=os.getenv('s3_name') + '-' + datetime.now().strftime('%S'))

        InfutorCoreEc2(self, id=os.getenv('ec2_id'), bucket=bucket)


