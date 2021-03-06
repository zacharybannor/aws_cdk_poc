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
  aws_ecr as _ecr,
  aws_ec2 as _ec2,
  aws_ecs as _ecs,
  aws_ecs_patterns as _ecs_patterns)
from datetime import datetime
import os


class VMDCoreCfnBucket(core.Construct):
    def __init__(self, scope: core.Construct, id: str, bucket_name: str, *, depends_on: list=None,
                 transfer_acceleration: bool=False, removal_policy: str='destroy', **kwargs):
        super().__init__(scope, id)

        self.id = id,
        self.bucket_name = bucket_name
        self.depends_on = depends_on
        for k,v in kwargs.items():
            setattr(self, k, v)

        access_control = str(_s3.BucketAccessControl.PRIVATE)
        self.access_control = access_control

        default_encryption_props = _s3.CfnBucket.ServerSideEncryptionByDefaultProperty(sse_algorithm='AES256')

        server_side_encryption_rule_props = [_s3.CfnBucket.ServerSideEncryptionRuleProperty(
            server_side_encryption_by_default=default_encryption_props)]

        encryption_props = _s3.CfnBucket.BucketEncryptionProperty(
            server_side_encryption_configuration=server_side_encryption_rule_props)

        self.encryption = encryption_props

        public_access_control_props = _s3.CfnBucket.PublicAccessBlockConfigurationProperty(block_public_acls=True,
                                                                                           block_public_policy=True,
                                                                                           ignore_public_acls=True,
                                                                                           restrict_public_buckets=True)
        self.block_public_acls = public_access_control_props.block_public_acls
        self.block_public_policy = public_access_control_props.block_public_policy
        self.ignore_public_acls = public_access_control_props.ignore_public_acls
        self.restrict_public_buckets = public_access_control_props.restrict_public_buckets

        if transfer_acceleration is False:
            acceleration_status = _s3.CfnBucket.AccelerateConfigurationProperty(acceleration_status='Suspended')
        else:
            acceleration_status = _s3.CfnBucket.AccelerateConfigurationProperty(acceleration_status='Enabled')

        self.acceleration_status = acceleration_status

        if not removal_policy.lower() == 'destroy':
            rp = core.RemovalPolicy.RETAIN
        else:
            rp = core.RemovalPolicy.DESTROY

        self.removal_policy = rp

        self.bucket = _s3.CfnBucket(self, id=id, bucket_name=bucket_name, access_control=self.access_control,
                                    public_access_block_configuration=public_access_control_props,
                                    bucket_encryption=encryption_props, **kwargs)

        if depends_on is not None:
            for d in depends_on:
                self.bucket.add_depends_on(d)

        self.bucket.apply_removal_policy(rp)
