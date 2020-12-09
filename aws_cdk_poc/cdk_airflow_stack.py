from aws_cdk import core
from core_constructs.core_constructs import InfutorAirflowPipeline
from datetime import datetime
import os


class InfutorAirflowStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

    def create_stack(self):

        InfutorAirflowPipeline(self, id=os.getenv('stack_id'))

