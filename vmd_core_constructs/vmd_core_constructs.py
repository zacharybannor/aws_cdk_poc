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

class VMDCoreS3(core.Construct):
  def __init__(self, scope: core.Construct, id: str, bucket_name: str, *, removal_policy: str='destroy',
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

      self.bucket = _s3.Bucket(self, id=id, bucket_name=bucket_name, removal_policy=rp, access_control=access_control,
                  block_public_access=block_public_access, encryption=encryption, **kwargs)


class VMDCoreVPC(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, max_azs=3, cidr=_ec2.Vpc.DEFAULT_CIDR_RANGE,
                 default_instance_tenancy=_ec2.DefaultInstanceTenancy.DEFAULT, **kwargs):
        super().__init__(scope, id)

        self.id = id
        self.max_azs = max_azs
        self.cidr = cidr
        self.default_instance_tenancy = default_instance_tenancy
        for k,v in kwargs.items():
            setattr(self, k, v)

        self.vpc = _ec2.Vpc(self, id=id, cidr=cidr, default_instance_tenancy=default_instance_tenancy, **kwargs)


class VMDCoreFargateService(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, vpc: VMDCoreVPC, image: str,
                 ecs_cluster: _ecs.Cluster, **kwargs):
        super().__init__(scope, id)

        self.id = id
        self.vpc = vpc
        self.image = image
        self.ecs_cluster = ecs_cluster
        for k,v in kwargs.items():
            setattr(self, k, v)

        task_image = _ecs.ContainerImage.from_registry(image)
        task_image_options = _ecs_patterns.ApplicationLoadBalancedTaskImageOptions(image=task_image)
        self.fargate_service = _ecs_patterns.ApplicationLoadBalancedFargateService(self, id=id, cluster=ecs_cluster,
                                                                                   desired_count=1, cpu=256,
                                                                                   task_image_options=task_image_options,
                                                                                   memory_limit_mib=512,
                                                                                   public_load_balancer=True,
                                                                                   )

