from aws_cdk import(
  core,
  aws_s3 as _s3,
  aws_ec2 as _ec2,
  aws_iam as _iam,
  aws_s3_assets as _assets)
from datetime import datetime
import os

class InfutorCoreS3(core.Construct):
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


class InfutorCoreVPC(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, max_azs: int=3, cidr=_ec2.Vpc.DEFAULT_CIDR_RANGE,
                 default_instance_tenancy=_ec2.DefaultInstanceTenancy.DEFAULT,
                 nat_gateways: int=0, subnet_config: str='public', **kwargs):
        super().__init__(scope, id)

        self.id = id
        self.max_azs = max_azs
        self.cidr = cidr
        self.default_instance_tenancy = default_instance_tenancy
        self.nat_gateways = nat_gateways

        if subnet_config.lower() == 'public':
            sub_conf = _ec2.SubnetType.PUBLIC
        elif subnet_config.lower() == 'isolated':
            sub_conf = _ec2.SubnetType.ISOLATED
        else:
            sub_conf = _ec2.SubnetType.PRIVATE

        self.subnet_config = sub_conf

        for k,v in kwargs.items():
            setattr(self, k, v)

        self.vpc = _ec2.Vpc(self, id=id, cidr=cidr, default_instance_tenancy=default_instance_tenancy,
                            nat_gateways=nat_gateways,
                            subnet_configuration=[_ec2.SubnetConfiguration(name='infutor_public',
                                                                           subnet_type=self.subnet_config)], **kwargs)


class InfutorCoreEc2(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, bucket: InfutorCoreS3, vpc_id: str=f'{id}_vpc',
                 role_id: str=f'{id}_role', instance_type: str='t3.nano', nat_gateways: int=0, subnet_config: str='public',
                 **kwargs):
        super().__init__(scope, id)

        self.bucket = bucket
        self.instance_type = instance_type
        self.nat_gateways = nat_gateways

        if subnet_config.lower() == 'public':
            sub_conf = _ec2.SubnetType.PUBLIC
        elif subnet_config.lower() == 'isolated':
            sub_conf = _ec2.SubnetType.ISOLATED
        else:
            sub_conf = _ec2.SubnetType.PRIVATE

        self.subnet_config = sub_conf

        for k,v in kwargs.items():
            setattr(self, k, v)


        #create the vpc
        vpc = _ec2.Vpc(self, id=vpc_id, nat_gateways=nat_gateways,
                            subnet_configuration=[_ec2.SubnetConfiguration(name='infutor_public',
                                                                           subnet_type=self.subnet_config)], **kwargs)

        #define ami
        linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            storage=_ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            virtualization=_ec2.AmazonLinuxVirt.HVM,
            edition=_ec2.AmazonLinuxEdition.STANDARD
        )

        #create ssm role and add to policy
        role = _iam.Role(self, id=role_id, role_name='InfutorSSMQuickStart',
                              assumed_by=_iam.ServicePrincipal('ec2.amazonaws.com'))

        role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonEC2RoleforSSM'))

        #create the ec2 instance
        instance_type = _ec2.InstanceType(instance_type)
        security_group = _ec2.SecurityGroup(self, id=f'{id}_sg', vpc=vpc,
                                            description='allow ssh to ec2 instance',
                                            security_group_name='not_at_all_secure_security_group',
                                            allow_all_outbound=True)
        security_group.add_ingress_rule(peer=_ec2.Peer.any_ipv4(), connection=_ec2.Port.tcp(22),
                                        description='ssh from anywhere')

        self.instance = _ec2.Instance(self, id=id, instance_name='InfutorAirflowEC2',
                                      instance_type=instance_type,
                                      machine_image=linux_ami,
                                      vpc=vpc,
                                      security_group=security_group
                                      )







