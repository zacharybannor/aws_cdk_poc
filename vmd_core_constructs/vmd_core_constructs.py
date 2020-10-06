from aws_cdk import(
  core,
  aws_s3 as _s3,
  aws_lambda_event_sources as _events,
  aws_lambda_destinations as _destinations,
  aws_lambda as _lambda,
  aws_iam as _iam,
  aws_glue as _glue,
  aws_sagemaker as _sm,
  aws_codecommit as _code,
  aws_sqs as _sqs,
  aws_ssm as _ssm,
  aws_logs as _logs,
  aws_ecr as _ecr)
from datetime import datetime
import os

class VMDCoreS3(core.Construct):
  def __init__(self, scope: core.Construct, id: str, bucket_name: str, *, removal_policy='destroy',
               access_control=_s3.BucketAccessControl.PRIVATE, block_public_access=_s3.BlockPublicAccess.BLOCK_ALL,
               encryption=_s3.BucketEncryption.S3_MANAGED, **kwargs) -> None:
      super().__init__(scope, id)

      self.bucket_name = bucket_name
      self.removal_policy = removal_policy
      self.id = id
      self.access_control = access_control
      self.block_public_access = block_public_access
      self.encryption = encryption
      for k,v in kwargs.items():
          setattr(self, k, v)

      if not removal_policy.lower() == 'destroy':
        rp = core.RemovalPolicy.RETAIN
      else:
        rp = core.RemovalPolicy.DESTROY

      _s3.Bucket(self, id=id, bucket_name=bucket_name, removal_policy=rp, access_control=access_control,
                  block_public_access=block_public_access, encryption=encryption, **kwargs)