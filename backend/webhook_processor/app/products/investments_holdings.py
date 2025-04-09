#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Union

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
import plaid
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.investment_holdings_get_request_options import InvestmentHoldingsGetRequestOptions
from plaid.model.investments_holdings_get_response import InvestmentsHoldingsGetResponse
from plaid.model.account_base import AccountBase
from plaid.model.holding import Holding
from plaid.model.security import Security

from app import constants, exceptions, utils, datastore

__all__ = ["InvestmentsHoldings"]

logger = Logger(child=True)
metrics = Metrics()


class InvestmentsHoldings:
    def build_message(
        self,
        user_id: str,
        item_id: str,
        entity: Union[AccountBase, Holding, Security],
    ) -> Union[Dict[str, Any], None]:
        """
        Build an SQS message from a Plaid Account, Holding or Security
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

        elif isinstance(entity, Security):
            message["MessageAttributes"]["SecurityId"] = {
                "StringValue": entity.security_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"SECURITY#{entity.security_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        elif isinstance(entity, Holding):
            message["MessageAttributes"]["AccountId"] = {
                "StringValue": entity.account_id,
                "DataType": "String",
            }
            message["MessageAttributes"]["SecurityId"] = {
                "StringValue": entity.security_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"SECURITY#{entity.security_id}#ACCOUNT#{entity.account_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        else:
            return None

        return message

    def get_holdings(self, user_id: str, item_id: str, account_ids: List[str] = None):
        logger.debug("Begin investments holdings get")

        try:
            item = datastore.get_item(user_id, item_id)
        except exceptions.ItemNotFoundException:
            logger.exception(f"Item {item_id} not found in DynamoDB")
            metrics.add_metric(name="ItemNotFound", unit=MetricUnit.Count, value=1)
            return

        client_id: str = self.client.api_client.configuration.api_key["clientId"]
        secret: str = self.client.api_client.configuration.api_key["secret"]
        access_token: str = item[constants.TOKEN_ATTRIBUTE_NAME]

        metrics.add_metric(
            name="PlaidInvestmentsHoldingsGetRequest", unit=MetricUnit.Count, value=1
        )

        params = {
            "access_token": access_token,
            "secret": secret,
            "client_id": client_id,
        }
        if account_ids:
            params["options"] = InvestmentHoldingsGetRequestOptions(account_ids=account_ids)

        request = InvestmentsHoldingsGetRequest(**params)

        try:
            response: InvestmentsHoldingsGetResponse = self.client.investments_holdings_get(request)
        except plaid.ApiException:
            logger.exception("Failed to call investments holdings get")
            raise

        messages: List[Dict[str, Any]] = []

        accounts: List[AccountBase] = response.accounts
        if accounts:
            messages += [
                self.build_message(user_id, item_id, entity=account) for account in accounts
            ]

        holdings: List[Holding] = response.holdings
        if holdings:
            messages += [
                self.build_message(user_id, item_id, entity=holding) for holding in holdings
            ]

        securities: List[Security] = response.securities
        if securities:
            messages += [
                self.build_message(user_id, item_id, entity=security) for security in securities
            ]

        self.send_messages(messages)

        logger.debug("End investments holdings get")

    def handle_webhook(
        self, user_id: str, item_id: str, webhook_code: str, payload: Dict[str, Any]
    ) -> None:
        """
        Handle investments holdings webhooks
        """

        # https://plaid.com/docs/api/products/investments/#holdings-default_update
        if webhook_code == constants.PLAID_WEBHOOK_CODE_DEFAULT_UPDATE:
            new_holdings: int = payload.get("new_holdings", 0)
            updated_holdings: int = payload.get("updated_holdings", {})

            logger.info(
                f"{webhook_code}, new_holdings={new_holdings}, updated_holdings={updated_holdings}"
            )

            self.get_holdings(user_id, item_id)

        else:
            logger.warning(f"Unsupported webhook code: {webhook_code}")
            metrics.add_metric(name="UnknownWebhookCode", unit=MetricUnit.Count, value=1)
