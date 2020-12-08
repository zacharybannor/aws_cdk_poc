from aws_cdk import(
  core,
  aws_s3 as _s3)


class DemoS3(core.Construct):
    def __init__(self, scope: core.Construct, id: str, bucket_name: str, *, **kwargs):
