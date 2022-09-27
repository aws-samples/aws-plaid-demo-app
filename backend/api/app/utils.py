#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import datetime
import decimal
import json
import os
from typing import Any
import uuid

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.utilities.data_classes.api_gateway_proxy_event import (
    RequestContextV2Authorizer,
)
from aws_lambda_powertools.event_handler.exceptions import UnauthorizedError
from aws_lambda_powertools.utilities import parameters
import plaid
from plaid.api import plaid_api

from .constants import BOTO3_CONFIG

__all__ = [
    "get_plaid_client",
    "now_iso8601",
    "authorize_request",
    "encode_data",
    "decode_data",
    "json_dumps",
    "generate_id",
]

PLAID_SECRET_ARN = os.getenv("PLAID_SECRET_ARN")

logger = Logger(child=True)
metrics = Metrics()
secrets_provider = parameters.SecretsProvider(config=BOTO3_CONFIG)


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


def now_iso8601() -> str:
    """
    Return the current date/time as a ISO8601 timestamp
    """
    return (
        datetime.datetime.now(tz=datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def authorize_request(router: Router) -> str:
    """
    Authorize a request and return the logged in user ID
    """
    user_id = None
    authorizer: RequestContextV2Authorizer = router.current_event.request_context.authorizer
    if authorizer:
        user_id = authorizer.jwt_claim.get("sub")

    if not user_id:
        raise UnauthorizedError("User not found in request")

    return user_id


def encode_data(data: str) -> str:
    encoded_bytes = base64.urlsafe_b64encode(data.encode("utf-8"))
    return str(encoded_bytes, "utf-8")


def decode_data(data: str) -> str:
    decoded_bytes = base64.urlsafe_b64decode(data)
    return str(decoded_bytes, "utf-8")


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


def json_dumps(obj: Any) -> str:
    """
    Compact JSON encoder
    """
    return json.dumps(obj, indent=None, separators=(",", ":"), sort_keys=True, cls=Encoder)


def generate_id() -> str:
    """
    Return a unique ID
    """
    return str(uuid.uuid4())
