#!/usr/bin/env python
# -*- coding: utf-8 -*-

from plaid.model.link_token_create_response import LinkTokenCreateResponse
from functools import partial
import os
import json
from json import JSONEncoder
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
from botocore.exceptions import ClientError
from dynamodb_encryption_sdk.encrypted.client import EncryptedClient
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions
from dynamodb_encryption_sdk.internal.utils import encrypt_put_item
from mypy_boto3_dynamodb import DynamoDBServiceResource, DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table
import plaid
from plaid.model.user_create_request import UserCreateRequest
from plaid.model.user_create_response import UserCreateResponse
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_create_request_income_verification import LinkTokenCreateRequestIncomeVerification
from plaid.model.income_verification_source_type import IncomeVerificationSourceType
from plaid.model.link_token_create_request_income_verification_payroll_income import LinkTokenCreateRequestIncomeVerificationPayrollIncome
from plaid.model.income_verification_payroll_flow_type import IncomeVerificationPayrollFlowType
from plaid.model.payroll_item import PayrollItem
from plaid.model.payroll_income_account_data import PayrollIncomeAccountData
from plaid.model.payroll_income_object import PayrollIncomeObject
from plaid.model.payroll_income_rate_of_pay import PayrollIncomeRateOfPay

from plaid.model.credit_payroll_income_get_request import CreditPayrollIncomeGetRequest
from plaid.model.credit_payroll_income_get_response import CreditPayrollIncomeGetResponse
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

dynamodb: DynamoDBServiceResource = boto3.resource(
    "dynamodb", config=constants.BOTO3_CONFIG)


@ router.post("/user")
@ tracer.capture_method(capture_response=False)
def create_user_token() -> Dict[str, str]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(user_id=user_id)
    tracer.put_annotation(key="UserId", value=user_id)

    client_user_id: Union[None, str] = router.current_event.json_body.get(
        "client_user_id")
    client_user_id = "test24"

    if not client_user_id:
        raise BadRequestError("client user ID not found in request")

    request = UserCreateRequest(client_user_id=client_user_id)

    client = utils.get_plaid_client()

    logger.info('Creating user for ' + client_user_id)

    try:
        response: UserCreateResponse = client.user_create(request)
    except plaid.ApiException:
        logger.exception("Unable to create user")
        raise InternalServerError("Failed to create user")

    return {
        "user_token": response.user_token,
        "user_id": response.user_id,
        "request_id": response.request_id
    }


@ router.post("/link")
@ tracer.capture_method(capture_response=False)
def create_link_token() -> Dict[str, str]:

    user_id: str = utils.authorize_request(router)

    logger.append_keys(user_id=user_id)
    tracer.put_annotation(key="UserId", value=user_id)

    client_user_id: Union[None, str] = router.current_event.json_body.get(
        "client_user_id")
    client_user_id = "test24"

    user_token: Union[None, str] = router.current_event.json_body.get(
        "user_token")

    request = LinkTokenCreateRequest(
        products=[Products("income_verification")],
        client_name="plaidaws",
        country_codes=[CountryCode("US")],
        language="en",
        webhook=WEBHOOK_URL,
        user=LinkTokenCreateRequestUser(client_user_id=client_user_id),
        user_token=user_token,
        income_verification=LinkTokenCreateRequestIncomeVerification(
            income_source_types=[IncomeVerificationSourceType('payroll')],
            payroll_income=LinkTokenCreateRequestIncomeVerificationPayrollIncome(
                flow_types=[IncomeVerificationPayrollFlowType(
                    'payroll_digital_income')]
            ))
    )

    client = utils.get_plaid_client()

    try:
        response: LinkTokenCreateResponse = client.link_token_create(request)
    except plaid.ApiException:
        logger.exception("Unable to create link token")
        raise InternalServerError("Failed to create link token")

    return {"link_token": response.link_token}


@ router.post("/payroll")
@ tracer.capture_method(capture_response=False)
def get_payroll_income() -> Dict[str, PayrollItem]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(user_id=user_id)
    tracer.put_annotation(key="UserId", value=user_id)

    user_token: Union[None, str] = router.current_event.json_body.get(
        "user_token")
    if not user_token:
        raise BadRequestError("Public token not found in request")

    logger.info('User token: ' + user_token)
    request = CreditPayrollIncomeGetRequest(user_token=user_token)
    logger.info('Request created')

    client = utils.get_plaid_client()

    logger.info('Getting payroll info for ' + user_id)

    try:
        response: CreditPayrollIncomeGetResponse = client.credit_payroll_income_get(
            request)
    except plaid.ApiException:
        logger.exception("Unable to get payroll information")
        logger.exception(plaid.ApiException)
        raise InternalServerError("Unable to get payroll information")

    send_email('eric@caseswift.io', 'eric@caseswift.io',
               response.items[0].institution_name)
    return {
        "response": "true"
    }


def send_email(sender, recipient, text):
    # Try to send the email.
    subject = text
    body_text = text
    CHARSET = "UTF-8"
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>CaseSwift: The GOAT PI Software</h1>
      <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a>
      </p>
    </body>
    </html>
    """

    client = boto3.client('ses', region_name="us-east-2")
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender
        )

    # Display an error if something goes wrong.
    except ClientError as e:
        logger.info("error sending email" + e.response['Error']['Message'])
    else:
        logger.info("Email sent!  Message ID: " + response["MessageId"])
