#!/usr/bin/env python3

from aws_cdk import core

from aws_cdk_poc.aws_cdk_poc_stack import AwsCdkPocStack


app = core.App()
AwsCdkPocStack(app, "aws-cdk-poc")

app.synth()
