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

