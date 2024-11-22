#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import decimal
import json
from typing import Any
import os
import uuid

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities import parameters
import plaid
from plaid.api import plaid_api

from app import constants

__all__ = ["get_plaid_client", "json_dumps", "now_iso8601", "today", "generate_id"]

PLAID_SECRET_ARN = os.getenv("PLAID_SECRET_ARN")

logger = Logger(child=True)
metrics = Metrics()
secrets_provider = parameters.SecretsProvider(boto_config=constants.BOTO3_CONFIG)


class Encoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.
    """

    def default(self, obj):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(obj, datetime.datetime):
            return obj.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, (decimal.Decimal, uuid.UUID)):
            return str(obj)
        else:
            return super().default(obj)


def get_plaid_client() -> plaid_api.PlaidApi:
    try:
        credentials = secrets_provider.get(PLAID_SECRET_ARN, transform="json")
        metrics.add_metric(name="FetchSecretSuccess", unit=MetricUnit.Count, value=1)
    except Exception:
        logger.exception(f"Unable to get secret value from {PLAID_SECRET_ARN}")
        metrics.add_metric(name="FetchSecretFailed", unit=MetricUnit.Count, value=1)
        raise

    configuration = plaid.Configuration(
        host=credentials["endpoint"],
        api_key={
            "clientId": credentials["client_id"],
            "secret": credentials["client_secret"],
        },
    )
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    return client


def json_dumps(obj: Any) -> str:
    """
    Compact JSON encoder
    """
    return json.dumps(obj, indent=None, separators=(",", ":"), sort_keys=True, cls=Encoder)


def now_iso8601() -> str:
    """
    Return the current date/time as a ISO8601 timestamp (YYYY-MM-DDTHH:MI:SSZ)
    """
    return (
        datetime.datetime.now(tz=datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def today() -> str:
    """
    Return the current date as YYYY-MM-DD
    """
    return datetime.date.today().isoformat()


def generate_id() -> str:
    """
    Return a unique ID
    """
    return str(uuid.uuid4())
