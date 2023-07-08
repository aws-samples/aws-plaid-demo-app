#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import Python Dependencies
import os
from typing import Dict, Union
import uuid

# Import AWS Power Tools

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler.api_gateway import Router
from aws_lambda_powertools.event_handler.exceptions import (
    InternalServerError,
    BadRequestError,
)

# Import Plaid

import plaid
from plaid.model.user_create_request import UserCreateRequest
from plaid.model.user_create_response import UserCreateResponse
from plaid.model.link_token_create_response import LinkTokenCreateResponse
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_create_request_income_verification import LinkTokenCreateRequestIncomeVerification
from plaid.model.income_verification_source_type import IncomeVerificationSourceType
from plaid.model.link_token_create_request_income_verification_payroll_income import LinkTokenCreateRequestIncomeVerificationPayrollIncome
from plaid.model.income_verification_payroll_flow_type import IncomeVerificationPayrollFlowType
from plaid.model.payroll_item import PayrollItem
from plaid.model.credit_payroll_income_get_request import CreditPayrollIncomeGetRequest
from plaid.model.credit_payroll_income_get_response import CreditPayrollIncomeGetResponse
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Import Modules
from app import utils, constants, datastore, exceptions, send

__all__ = ["router"]

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

tracer = Tracer()
logger = Logger(child=True)
metrics = Metrics()
router = Router()


@ router.get("/user")
@ tracer.capture_method(capture_response=False)
def create_user_token() -> Dict[str, str]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(user_id=user_id)
    tracer.put_annotation(key="UserId", value=user_id)

    client_user_id: str = uuid.uuid4()

    request = UserCreateRequest(client_user_id=client_user_id)

    client = utils.get_plaid_client()

    logger.info('Creating user for ' + client_user_id)

    try:
        response: UserCreateResponse = client.user_create(request)
    except plaid.ApiException:
        logger.exception("Unable to create user")
        raise InternalServerError("Failed to create user")

    return {
        "client_user_id": client_user_id,
        "user_token": response.user_token,
        "user_id": response.user_id,
        "request_id": response.request_id
    }


@ router.post("/link-payroll")
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


@ router.post("/link-employment")
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
        products=[Products("employment")],
        client_name="plaidaws",
        country_codes=[CountryCode("US")],
        language="en",
        webhook=WEBHOOK_URL,
        user=LinkTokenCreateRequestUser(client_user_id=client_user_id),
        user_token=user_token
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

    client = utils.get_plaid_client()

    # Handle payroll information.
    logger.info('Getting payroll info for ' + user_id)
    payroll_request = CreditPayrollIncomeGetRequest(user_token=user_token)
    try:
        payroll_response: CreditPayrollIncomeGetResponse = client.credit_payroll_income_get(
            payroll_request)
    except plaid.ApiException:
        logger.exception("Unable to get payroll information")
        logger.exception(plaid.ApiException)
        raise InternalServerError("Unable to get payroll information")

    logger.info('Payroll Data: ', payroll_response)

    send.send_email('eric@caseswift.io', 'eric@caseswift.io',
                    payroll_response)

    return {
        "response": "true"
    }
