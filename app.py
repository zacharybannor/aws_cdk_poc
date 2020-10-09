#!/usr/bin/env python3
from pathlib import Path  # python3 only
import os
from dotenv import load_dotenv
from aws_cdk import core
from aws_cdk_poc.aws_cdk_poc_stack import AwsCdkPocStack
from aws_cdk_poc.aws_cdk_cfn_poc_stack import AwsCdkPocCfnStack

env_path = Path('.') / '.stack_env'
load_dotenv(dotenv_path=env_path)


app = core.App()
# stack = AwsCdkPocStack(app, id=os.getenv('stack_name'))
stack = AwsCdkPocCfnStack(app, id=os.getenv('cfn_stack_name'))

stack.create_stack()

app.synth()
