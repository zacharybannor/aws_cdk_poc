#!/usr/bin/env python3
from pathlib import Path  # python3 only
import os
from datetime import datetime
from dotenv import load_dotenv
from aws_cdk import core
from aws_cdk_poc.cdk_airflow_stack import InfutorAirflowStack


def _add_tags(stack: core.Stack, more_tags: dict=None)-> None:
    tags = {
        'CreatedOn': datetime.now().strftime('%Y-%d-%m'),
        'CreatedBy': os.getenv('user')
    }

    if more_tags is not None:
        tags.update(more_tags)

    for k,v in tags.items():
        core.Tag.add(stack, k, v)


env_path = Path('.') / '.stack_env'
load_dotenv(dotenv_path=env_path)


app = core.App()

stack = InfutorAirflowStack(app, id=os.getenv('airflow_stack_name'))

_add_tags(stack)

stack.create_stack()

app.synth()
