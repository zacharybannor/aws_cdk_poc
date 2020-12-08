#!/usr/bin/env python3
from pathlib import Path  # python3 only
import os
from dotenv import load_dotenv
from aws_cdk import core
from aws_cdk_poc.cdk_airflow_stack import InfutorAirflowStack


env_path = Path('.') / '.stack_env'
load_dotenv(dotenv_path=env_path)


app = core.App()
# stack = AwsCdkPocStack(app, id=os.getenv('stack_name'))
stack = InfutorAirflowStack(app, id=os.getenv('airflow_stack_name'))

stack.create_stack()

app.synth()
