#!/usr/bin/env python
# -*- coding: utf-8 -*-

from botocore.config import Config

__all__ = [
    "BOTO3_CONFIG",
]

BOTO3_CONFIG = Config(
    retries={
        "max_attempts": 10,
        "mode": "standard",
    }
)
