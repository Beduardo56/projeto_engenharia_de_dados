#!/usr/bin/env python3

from aws_cdk import core

from common_stack import CommonStack


app = core.App()
common_stack = CommonStack(app)
app.synth()
