#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import hmac
import os
import time
from typing import Dict, Any, TYPE_CHECKING

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.event_handler.exceptions import BadRequestError
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.utilities.validation.exceptions import SchemaValidationError
import boto3
import botocore
from jose import jwt
import requests

if TYPE_CHECKING:
    from mypy_boto3_sqs.client import SQSClient

from app import constants, schemas

__all__ = ["router"]

PLAID_SECRET_ARN = os.getenv("PLAID_SECRET_ARN")
WEBHOOK_QUEUE_URL = os.getenv("WEBHOOK_QUEUE_URL")

tracer = Tracer()
logger = Logger(child=True)
metrics = Metrics()
router = Router()


# Cache for webhook validation keys.
KEY_CACHE = {}

# Plaid client credentials
CREDENTIALS = {}

secrets_provider = parameters.SecretsProvider(boto_config=constants.BOTO3_CONFIG)
sqs: "SQSClient" = boto3.client("sqs", config=constants.BOTO3_CONFIG)


def get_credentials() -> Dict[str, str]:
    global CREDENTIALS

    if CREDENTIALS:
        return CREDENTIALS

    metrics.add_metric(name="FetchSecret", unit=MetricUnit.Count, value=1)

    try:
        CREDENTIALS = secrets_provider.get(PLAID_SECRET_ARN, transform="json")
        metrics.add_metric(name="FetchSecretSuccess", unit=MetricUnit.Count, value=1)
    except Exception:
        logger.exception(f"Unable to get secret value from {PLAID_SECRET_ARN}")
        metrics.add_metric(name="FetchSecretFailed", unit=MetricUnit.Count, value=1)
        raise

    return CREDENTIALS


def verify(body: str, signed_jwt: str) -> bool:
    current_key_id = jwt.get_unverified_header(signed_jwt)["kid"]

    credentials = get_credentials()

    # If the key is not in the cache, update all non-expired keys.
    if current_key_id not in KEY_CACHE:
        keys_ids_to_update = [
            key_id for key_id, key in KEY_CACHE.items() if key["expired_at"] is None
        ]
        keys_ids_to_update.append(current_key_id)

        for key_id in keys_ids_to_update:
            r = requests.post(
                credentials["endpoint"] + "/webhook_verification_key/get",
                json={
                    "client_id": credentials["client_id"],
                    "secret": credentials["client_secret"],
                    "key_id": key_id,
                },
            )

            # If this is the case, the key ID may be invalid.
            if r.status_code != 200:
                logger.debug(f"Key response: {r}")
                continue

            response = r.json()
            key = response["key"]
            KEY_CACHE[key_id] = key

    # If the key ID is not in the cache, the key ID may be invalid.
    if current_key_id not in KEY_CACHE:
        metrics.add_metric(name="JWTKeyInvalid", unit=MetricUnit.Count, value=1)
        logger.warning(f"Key {current_key_id} is invalid")
        return False

    # Fetch the current key from the cache.
    key = KEY_CACHE[current_key_id]

    # Reject expired keys.
    if key["expired_at"] is not None:
        metrics.add_metric(name="JWTKeyExpired", unit=MetricUnit.Count, value=1)
        logger.warning(f"Key {current_key_id} has expired")
        return False

    # Validate the signature and extract the claims.
    try:
        claims = jwt.decode(signed_jwt, key, algorithms=["ES256"])
    except jwt.JWTError:
        metrics.add_metric(name="JWTDecodeError", unit=MetricUnit.Count, value=1)
        logger.warning(f"Failed to decode JWT: {signed_jwt}")
        return False

    # Ensure that the token is not expired.
    if claims["iat"] < time.time() - constants.TOKEN_EXPIRATION:
        metrics.add_metric(name="JWTKeyExpired", unit=MetricUnit.Count, value=1)
        logger.warning(f"Key {current_key_id} has expired")
        return False

    # Compute the hash of the body.
    m = hashlib.sha256()
    m.update(body.encode())
    body_hash = m.hexdigest()

    # Ensure that the hash of the body matches the claim.
    # Use constant time comparison to prevent timing attacks.
    return hmac.compare_digest(body_hash, claims["request_body_sha256"])


@router.post("/")
@tracer.capture_method(capture_response=False)
def post_webhook() -> Response:
    body = router.current_event.body
    if not body:
        raise BadRequestError("No body found in request")

    json_body: Dict[str, Any] = router.current_event.json_body
    plaid_verification = router.current_event.get_header_value("Plaid-Verification")

    if not plaid_verification:
        metrics.add_metric(name="HeaderMissing", unit=MetricUnit.Count, value=1)
        raise BadRequestError("Missing Plaid-Verification Header")

    if not verify(body, plaid_verification):
        metrics.add_metric(name="VerificationFailed", unit=MetricUnit.Count, value=1)
        raise BadRequestError("Failed to verify request from Plaid")

    try:
        validate(event=json_body, schema=schemas.WEBHOOK_SCHEMA)
    except SchemaValidationError:
        logger.exception(f"Failed to validate webhook payload: {json_body}")
        metrics.add_metric(name="ValidationFailed", unit=MetricUnit.Count, value=1)
        raise BadRequestError("Failed to validate request from Plaid")

    item_id: str = json_body["item_id"]

    logger.append_keys(item_id=item_id)
    tracer.put_annotation(key="ItemId", value=item_id)

    params = {
        "QueueUrl": WEBHOOK_QUEUE_URL,
        "DelaySeconds": 0,
        "MessageAttributes": {
            "WebhookType": {
                "DataType": "String",
                "StringValue": json_body["webhook_type"],
            },
            "WebhookCode": {
                "DataType": "String",
                "StringValue": json_body["webhook_code"],
            },
            "ItemId": {
                "DataType": "String",
                "StringValue": item_id,
            },
        },
        "MessageBody": body,
        "MessageDeduplicationId": "{}_{}".format(
            json_body["webhook_type"], json_body["webhook_code"]
        ),
        "MessageGroupId": item_id,
    }

    metrics.add_metric(name="SendCount", unit=MetricUnit.Count, value=1)
    logger.debug(f"Sending message to SQS: {params}")

    try:
        sqs.send_message(**params)
        logger.debug("Sent message to SQS")
        metrics.add_metric(name="SendSuccess", unit=MetricUnit.Count, value=1)
    except botocore.exceptions.ClientError:
        logger.exception("Failed to send message to SQS")
        metrics.add_metric(name="SendFailed", unit=MetricUnit.Count, value=1)
        raise

    response = Response(status_code=200, content_type=content_types.APPLICATION_JSON, body="")

    return response
