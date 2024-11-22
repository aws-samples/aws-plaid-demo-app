#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from typing import Dict, Any, List, Union

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
import plaid
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.investments_transactions_get_request_options import (
    InvestmentsTransactionsGetRequestOptions,
)
from plaid.model.investments_transactions_get_response import InvestmentsTransactionsGetResponse
from plaid.model.investment_transaction import InvestmentTransaction
from plaid.model.account_base import AccountBase
from plaid.model.security import Security

from app import constants, exceptions, utils, datastore

__all__ = ["InvestmentsTransactions"]

logger = Logger(child=True)
metrics = Metrics()


class InvestmentsTransactions:
    def build_message(
        self,
        user_id: str,
        item_id: str,
        entity: Union[AccountBase, Security, InvestmentTransaction],
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

        elif isinstance(entity, InvestmentTransaction):
            message["MessageAttributes"]["InvestmentTransactionId"] = {
                "StringValue": entity.investment_transaction_id,
                "DataType": "String",
            }

            body: Dict[str, Any] = entity.to_dict()
            body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
            body["sk"] = f"INVESTMENT_TRANSACTION#{entity.investment_transaction_id}"
            body["plaid_type"] = type(entity).__name__
            body["updated_at"] = utils.now_iso8601()
            message["MessageBody"] = utils.json_dumps(body)

        else:
            return None

        return message

    def get_transactions(
        self,
        user_id: str,
        item_id: str,
        start_date: str,
        end_date: str,
        account_ids: List[str] = None,
    ) -> None:
        logger.debug("Begin investments transactions get")

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
            name="PlaidInvestmentsTransactionsGetRequest", unit=MetricUnit.Count, value=1
        )

        options = InvestmentsTransactionsGetRequestOptions(
            count=constants.PLAID_INVESTMENTS_TRANSACTIONS_COUNT_MAX, account_ids=account_ids
        )

        params = {
            "access_token": access_token,
            "secret": secret,
            "client_id": client_id,
            "start_date": start_date,
            "end_date": end_date,
            "options": options,
        }

        request = InvestmentsTransactionsGetRequest(**params)

        try:
            response: InvestmentsTransactionsGetResponse = self.client.investments_transactions_get(
                request
            )
        except plaid.ApiException:
            logger.exception("Failed to call investments transactions get")
            raise

        transactions: List[InvestmentTransaction] = response.investment_transactions
        total_transactions: int = response.total_investment_transactions

        while len(transactions) < total_transactions:
            request = InvestmentsTransactionsGetRequest(
                access_token=access_token,
                secret=secret,
                client_id=client_id,
                start_date=start_date,
                end_date=end_date,
                options=InvestmentsTransactionsGetRequestOptions(
                    count=constants.PLAID_INVESTMENTS_TRANSACTIONS_COUNT_MAX,
                    offset=len(transactions),
                ),
            )

            try:
                response: InvestmentsTransactionsGetResponse = (
                    self.client.investments_transactions_get(request)
                )
            except plaid.ApiException:
                logger.exception("Failed to call investments transactions get")
                raise

            transactions.extend(response.investment_transactions)

        messages: List[Dict[str, Any]] = []

        accounts: List[AccountBase] = response.accounts
        if accounts:
            messages += [
                self.build_message(user_id, item_id, entity=account) for account in accounts
            ]

        securities: List[Security] = response.securities
        if securities:
            messages += [
                self.build_message(user_id, item_id, entity=security) for security in securities
            ]

        if transactions:
            messages += [
                self.build_message(user_id, item_id, entity=transaction)
                for transaction in transactions
            ]

        self.send_messages(messages)

    def handle_webhook(
        self, user_id: str, item_id: str, webhook_code: str, payload: Dict[str, Any]
    ) -> None:
        """
        Handle investments transactions webhooks
        """

        # https://plaid.com/docs/api/products/investments/#investments_transactions-default_update
        if webhook_code == constants.PLAID_WEBHOOK_CODE_DEFAULT_UPDATE:
            new_investments_transactions: int = payload.get("new_investments_transactions", 0)
            canceled_investments_transactions: int = payload.get(
                "canceled_investments_transactions", 0
            )

            logger.info(
                f"{webhook_code}, new_investments_transactions={new_investments_transactions}, canceled_investments_transactions={canceled_investments_transactions}"
            )

            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=730)

            self.get_transactions(user_id, item_id, start_date=start_date, end_date=end_date)

        else:
            logger.warning(f"Unsupported webhook code: {webhook_code}")
            metrics.add_metric(name="UnknownWebhookCode", unit=MetricUnit.Count, value=1)
