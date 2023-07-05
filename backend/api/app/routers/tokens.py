#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
import os
from typing import Dict, Union

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.event_handler.exceptions import (
    InternalServerError,
    BadRequestError,
)
import boto3
import botocore
from dynamodb_encryption_sdk.encrypted.client import EncryptedClient
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions
from dynamodb_encryption_sdk.internal.utils import encrypt_put_item
from mypy_boto3_dynamodb import DynamoDBServiceResource, DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table
import plaid
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_create_response import LinkTokenCreateResponse
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_public_token_exchange_response import ItemPublicTokenExchangeResponse
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

from app import utils, constants, datastore, exceptions

__all__ = ["router"]

TABLE_NAME = os.getenv("TABLE_NAME")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
KEY_ARN = os.getenv("KEY_ARN")

tracer = Tracer()
logger = Logger(child=True)
metrics = Metrics()
router = Router()

dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb", config=constants.BOTO3_CONFIG)


@router.get("/")
@tracer.capture_method(capture_response=False)
def create_link_token() -> Dict[str, str]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(user_id=user_id)
    tracer.put_annotation(key="UserId", value=user_id)

    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="plaidaws",
        country_codes=[CountryCode("US")],
        language="en",
        webhook=WEBHOOK_URL,
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
    )

    client = utils.get_plaid_client()

    try:
        response: LinkTokenCreateResponse = client.link_token_create(request)
    except plaid.ApiException:
        logger.exception("Unable to create link token")
        raise InternalServerError("Failed to create link token")

    return {"link_token": response.link_token}


@router.post("/")
@tracer.capture_method(capture_response=False)
def exchange_token() -> Response:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(user_id=user_id)
    tracer.put_annotation(key="UserId", value=user_id)

    # TODO: validate against METADATA_SCHEMA

    public_token: Union[None, str] = router.current_event.json_body.get("public_token")
    if not public_token:
        raise BadRequestError("Public token not found in request")

    metadata: Dict[str, str] = router.current_event.json_body.get("metadata", {})
    if not metadata:
        raise BadRequestError("Metadata not found in request")

    institution = metadata.get("institution", {})
    institution_id = institution.get("institution_id")
    if not institution_id:
        raise BadRequestError("Institution ID not found in request")

    if datastore.check_institution(user_id, institution_id):
        raise exceptions.ConflictError("User has already linked to this institution")

    request = ItemPublicTokenExchangeRequest(public_token=public_token)

    client = utils.get_plaid_client()

    try:
        response: ItemPublicTokenExchangeResponse = client.item_public_token_exchange(request)
    except plaid.ApiException:
        logger.exception("Unable to exchange public token")
        raise InternalServerError("Failed to exchange public token")

    item_id: str = response.item_id
    access_token: str = response.access_token

    
    headers = {"Location": f"/v1/items/{item_id}"}

    response = Response(
        status_code=202, content_type=content_types.APPLICATION_JSON, body="", headers=headers
    )

    return response
