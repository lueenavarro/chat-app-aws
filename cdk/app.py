#!/usr/bin/env python3
import os

from aws_cdk import (core)

from cdk.chat_app_stack import ChatAppStack


app = core.App()
ChatAppStack(app, "ChatAppStack")

app.synth()
