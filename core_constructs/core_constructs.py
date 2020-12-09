from aws_cdk import(
  core,
  aws_s3 as _s3,
  aws_ec2 as _ec2,
  aws_iam as _iam,
  aws_secretsmanager as _secrets,
  aws_rds as _rds,
  aws_ssm as _ssm,
  aws_s3_assets as _assets)
from datetime import datetime
import os
import json

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


class InfutorAirflowPipeline(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, bucket_id: str=f'{id}_bucket', vpc_id: str=f'{id}_vpc',
                 role_id: str=f'{id}_role', ec2_instance_type: str='t3.nano', nat_gateways: int=0,
                 subnet_config: str= 'public', **kwargs):
        super().__init__(scope, id)

        self.id = id
        self.bucket_id = bucket_id
        self.vpc_id = vpc_id
        self.role_id = role_id
        self.instance_type = ec2_instance_type
        self.nat_gateways = nat_gateways
        self.removal_policy = core.RemovalPolicy.DESTROY

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
        self.vpc = _ec2.Vpc(self, id=vpc_id, nat_gateways=nat_gateways,
                            subnet_configuration=[_ec2.SubnetConfiguration(name=f'infutor_{subnet_config.lower()}',
                                                                           subnet_type=self.subnet_config)], **kwargs)

        #create the bucket
        now = datetime.now().strftime('%S')
        access_control = _s3.BucketAccessControl.PUBLIC_READ_WRITE
        encryption = _s3.BucketEncryption.UNENCRYPTED
        block_public_access = None

        self.bucket = _s3.Bucket(self, id=self.bucket_id, bucket_name=os.getenv('s3_name') + '-' + now,
                                removal_policy=self.removal_policy, access_control=access_control,
                                block_public_access=block_public_access, encryption=encryption)


        #define ami
        self.linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            storage=_ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            virtualization=_ec2.AmazonLinuxVirt.HVM,
            edition=_ec2.AmazonLinuxEdition.STANDARD
        )

        #create ssm role and add to policy
        self.ec2_role = _iam.Role(self, id=role_id, role_name='InfutorSSMQuickStart',
                              assumed_by=_iam.ServicePrincipal('ec2.amazonaws.com'))

        self.ec2_role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonEC2RoleforSSM'))

        #create the ec2 instance
        ec2_instance_type = _ec2.InstanceType(ec2_instance_type)
        security_group = _ec2.SecurityGroup(self, id=f'{id}_sg', vpc=self.vpc,
                                            description='allow ssh to ec2 instance',
                                            security_group_name='not_at_all_secure_security_group',
                                            allow_all_outbound=True)
        security_group.add_ingress_rule(peer=_ec2.Peer.any_ipv4(), connection=_ec2.Port.tcp(22),
                                        description='ssh from anywhere')

        self.instance = _ec2.Instance(self, id=id, instance_name='InfutorAirflowEC2',
                                      instance_type=ec2_instance_type,
                                      machine_image=self.linux_ami,
                                      vpc=self.vpc,
                                      security_group=security_group
                                      )


        # create secrets for db access and store arn in ssm
        db_username = os.getenv('db_username')
        secret_str_generator = _secrets.SecretStringGenerator(
            secret_string_template=json.dumps({'username': db_username}), exclude_punctuation=True,
            include_space=False, generate_string_key='password')

        self.db_access_secret = _secrets.Secret(self, id=f'{id}_secret', secret_name='infutor_airflow_db_secret',
                                                generate_secret_string=secret_str_generator,
                                                removal_policy=self.removal_policy)

        self.ssm_db_secret = _ssm.StringParameter(self, id=f'{id}_secret_ssm_param',
                                                  parameter_name='infutor_airflow_db_ssm_secret',
                                                  string_value=self.db_access_secret.secret_arn)


        # create mysql rds
        db_credentials = _rds.Credentials.from_secret(secret=self.db_access_secret, username=db_username)
        db_engine = _rds.DatabaseInstanceEngine.MYSQL
        db_name = os.getenv('rds_name')
        rds_instance_type = _ec2.InstanceType('t2.micro')

        self.mysql_db = _rds.DatabaseInstance(self, id=f'{id}_mysql_db', credentials=db_credentials,
                                              engine=db_engine, database_name=db_name, instance_type=rds_instance_type,
                                              allow_major_version_upgrade=False, vpc=self.vpc,
                                              removal_policy=self.removal_policy, vpc_subnets=self.subnet_config,
                                              security_groups=[security_group],
                                              instance_identifier='infutor_airflow_mysql_instance')







