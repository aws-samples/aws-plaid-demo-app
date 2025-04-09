#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Union

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
import plaid
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
from plaid.model.liabilities_get_response import LiabilitiesGetResponse
from plaid.model.liabilities_get_request_options import LiabilitiesGetRequestOptions
from plaid.model.account_base import AccountBase
from plaid.model.liabilities_object import LiabilitiesObject
from plaid.model.credit_card_liability import CreditCardLiability
from plaid.model.mortgage_liability import MortgageLiability
from plaid.model.student_loan import StudentLoan

from app import utils, exceptions, constants
from app.products import AbstractProduct

__all__ = ["Liabilities"]

logger = Logger(child=True)
metrics = Metrics()


class Liabilities(AbstractProduct):
    def build_message(
        self,
        user_id: str,
        item_id: str,
        entity: Union[AccountBase, CreditCardLiability, MortgageLiability, StudentLoan],
    ) -> Union[Dict[str, Any], None]:
        """
        Build an SQS message from a Plaid Account
        """

        message = {
            "DelaySeconds": 0,
            "Id": utils.generate_id(),
            "MessageAttributes": {
                "ItemId": {
                    "StringValue": item_id,
                    "DataType": "String",
                },
                "UserId": {
                    "StringValue": user_id,
                    "DataType": "String",
                },
                "EventName": {
                    "StringValue": "INSERT",
                    "DataType": "String",
                },
            },
        }

        if isinstance(entity, AccountBase):
            message["MessageAttributes"]["AccountId"] = {
                "StringValue": entity.account_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"ACCOUNT#{entity.account_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        elif isinstance(entity, CreditCardLiability):
            message["MessageAttributes"]["AccountId"] = {
                "StringValue": entity.account_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"CREDITCARD#{entity.account_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        elif isinstance(entity, MortgageLiability):
            message["MessageAttributes"]["AccountId"] = {
                "StringValue": entity.account_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"MORTGAGE#{entity.account_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        elif isinstance(entity, StudentLoan):
            message["MessageAttributes"]["AccountId"] = {
                "StringValue": entity.account_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"STUDENTLOAN#{entity.account_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        else:
            return None

        return message

    def get_liabilities(self, user_id: str, item_id: str, account_ids: List[str] = None) -> None:
        logger.debug("Begin liabilities get")

        try:
            item = self.get_item(user_id, item_id)
        except exceptions.ItemNotFoundException:
            logger.exception(f"Item {item_id} not found in DynamoDB")
            metrics.add_metric(name="ItemNotFound", unit=MetricUnit.Count, value=1)
            return

        client_id: str = self.client.api_client.configuration.api_key["clientId"]
        secret: str = self.client.api_client.configuration.api_key["secret"]
        access_token: str = item[constants.TOKEN_ATTRIBUTE_NAME]

        metrics.add_metric(name="PlaidLiabilitiesGetRequest", unit=MetricUnit.Count, value=1)

        params = {
            "access_token": access_token,
            "secret": secret,
            "client_id": client_id,
        }
        if account_ids:
            params["options"] = LiabilitiesGetRequestOptions(account_ids=account_ids)
        request = LiabilitiesGetRequest(**params)

        try:
            response: LiabilitiesGetResponse = self.client.liabilities_get(request)
        except plaid.ApiException:
            logger.exception("Failed to call liabilities get")
            raise

        messages: List[Dict[str, Any]] = []

        accounts: List[AccountBase] = response.accounts
        if accounts:
            messages += [
                self.build_message(user_id, item_id, entity=account) for account in accounts
            ]

        liabilities: LiabilitiesObject = response.liabilities

        credits: List[CreditCardLiability] = liabilities.credit
        if credits:
            messages += [self.build_message(user_id, item_id, entity=credit) for credit in credits]

        mortgages: List[MortgageLiability] = liabilities.mortgage
        if mortgages:
            messages += [
                self.build_message(user_id, item_id, entity=mortgage) for mortgage in mortgages
            ]

        student_loans: List[StudentLoan] = liabilities.student
        if student_loans:
            messages += [
                self.build_message(user_id, item_id, entity=loan) for loan in student_loans
            ]

        self.send_messages(messages)

        logger.debug("End liabilities get")

    def handle_webhook(
        self, user_id: str, item_id: str, webhook_code: str, payload: Dict[str, Any]
    ) -> None:
        """
        Handle liabilities webhooks
        """

        # https://plaid.com/docs/api/products/liabilities/#default_update
        if webhook_code == constants.PLAID_WEBHOOK_CODE_DEFAULT_UPDATE:
            account_ids_with_new_liabilities: List[str] = payload.get(
                "account_ids_with_new_liabilities", []
            )
            account_ids_with_updated_liabilities: Dict[str, str] = payload.get(
                "account_ids_with_updated_liabilities", {}
            )

            logger.info(
                f"{webhook_code}, account_ids_with_new_liabilities={account_ids_with_new_liabilities}, account_ids_with_updated_liabilities={account_ids_with_updated_liabilities}"
            )

            account_ids: List[str] = (
                account_ids_with_new_liabilities + account_ids_with_updated_liabilities.keys()
            )

            self.get_liabilities(user_id, item_id, account_ids)
        else:
            logger.warning(f"Unsupported webhook code: {webhook_code}")
            metrics.add_metric(name="UnknownWebhookCode", unit=MetricUnit.Count, value=1)
