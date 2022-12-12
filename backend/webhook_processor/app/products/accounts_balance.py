#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from typing import Dict, Any, List

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
import plaid
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_balance_get_request_options import AccountsBalanceGetRequestOptions
from plaid.model.accounts_get_response import AccountsGetResponse
from plaid.model.account_base import AccountBase

from app import utils, exceptions, datastore, constants
from app.products import AbstractProduct

__all__ = ["AccountsBalance"]

logger = Logger(child=True)
metrics = Metrics()


class AccountsBalance(AbstractProduct):
    def build_message(
        self, user_id: str, item_id: str, account: AccountBase, today: str = None
    ) -> Dict[str, Any]:
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
                "AccountId": {
                    "StringValue": account.account_id,
                    "DataType": "String",
                },
                "EventName": {
                    "StringValue": "INSERT",
                    "DataType": "String",
                },
            },
        }

        body: Dict[str, Any] = account.to_dict()
        body["pk"] = f"USER#{user_id}#ITEM#{item_id}"
        body["plaid_type"] = type(account).__name__

        if today:
            body["sk"] = f"BALANCE#{account.account_id}#{today}"
        else:
            body["sk"] = f"ACCOUNT#{account.account_id}"

        body["updated_at"] = utils.now_iso8601()
        message["MessageBody"] = utils.json_dumps(body)

        return message

    def get_balances(self, user_id: str, item_id: str) -> None:
        logger.debug("Begin accounts balance get")

        try:
            item = datastore.get_item(user_id, item_id)
        except exceptions.ItemNotFoundException:
            logger.exception(f"Item {item_id} not found in DynamoDB")
            metrics.add_metric(name="ItemNotFound", unit=MetricUnit.Count, value=1)
            return

        client_id: str = self.client.api_client.configuration.api_key["clientId"]
        secret: str = self.client.api_client.configuration.api_key["secret"]
        access_token: str = item[constants.TOKEN_ATTRIBUTE_NAME]

        metrics.add_metric(name="PlaidAccountsBalanceGetRequest", unit=MetricUnit.Count, value=1)

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        params = {
            "access_token": access_token,
            "secret": secret,
            "client_id": client_id,
            "options": AccountsBalanceGetRequestOptions(min_last_updated_datetime=now),
        }

        request = AccountsBalanceGetRequest(**params)

        try:
            response: AccountsGetResponse = self.client.accounts_balance_get(request)
        except plaid.ApiException:
            logger.exception("Failed to call accounts balance get")
            raise

        accounts: List[AccountBase] = response.accounts
        if accounts:
            messages = []
            today = utils.today()

            for account in accounts:
                messages.append(self.build_message(user_id, item_id, account))
                messages.append(self.build_message(user_id, item_id, account, today=today))

            self.send_messages(messages)

        logger.debug("End accounts balance get")
