#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Union

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from boto3.dynamodb.conditions import Attr
import botocore
import plaid
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from plaid.model.transactions_sync_request_options import TransactionsSyncRequestOptions
from plaid.model.transaction import Transaction
from plaid.model.removed_transaction import RemovedTransaction

from app import utils, constants, exceptions, datastore
from app.products import AbstractProduct

__all__ = ["Transactions"]

logger = Logger(child=True)
metrics = Metrics()


class Transactions(AbstractProduct):
    def build_message(
        self,
        user_id: str,
        item_id: str,
        event_name: str,
        transaction: Union[Transaction, RemovedTransaction, str],
    ) -> Dict[str, Any]:
        """
        Build an SQS message from a Plaid Transaction
        """

        if isinstance(transaction, (Transaction, RemovedTransaction)):
            transaction_id: str = transaction.transaction_id
        else:
            transaction_id = transaction

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
                "TransactionId": {
                    "StringValue": transaction_id,
                    "DataType": "String",
                },
                "EventName": {
                    "StringValue": event_name,
                    "DataType": "String",
                },
            },
        }

        body = {
            "pk": f"USER#{user_id}#ITEM#{item_id}",
            "sk": f"TRANSACTION#{transaction_id}",
        }

        if event_name != "REMOVE" and isinstance(transaction, Transaction):
            body |= transaction.to_dict()
            body["plaid_type"] = type(transaction).__name__
            body["gsi1pk"] = f"USER#{user_id}#ITEM#{item_id}#TRANSACTIONS"
            body["gsi1sk"] = f"TRANSACTION#{transaction.date}#{transaction_id}"

        message["MessageBody"] = utils.json_dumps(body)

        return message

    def store_cursor(self, user_id: str, item_id: str, cursor: str) -> None:
        """
        Store the cursor value for the given item
        """

        now = utils.now_iso8601()
        params = {
            "Key": {
                "pk": f"USER#{user_id}#ITEM#{item_id}",
                "sk": "v0",
            },
            "UpdateExpression": "SET #c = :c, #ts = :ts",
            "ConditionExpression": Attr("pk").exists() & Attr("sk").exists(),
            "ExpressionAttributeNames": {
                "#c": constants.CURSOR_ATTRIBUTE_NAME,
                "#ts": "updated_at",
            },
            "ExpressionAttributeValues": {
                ":c": cursor,
                ":ts": now,
            },
            "ReturnValues": "NONE",
        }

        try:
            self.dynamodb.update_item(**params)
            logger.debug(f"Updated cursor to {cursor}")
            metrics.add_metric(name="UpdateCursorSuccess", unit=MetricUnit.Count, value=1)
        except botocore.exceptions.ClientError:
            logger.exception(f"Failed to update cursor to {cursor}")
            metrics.add_metric(name="UpdateCursorFailed", unit=MetricUnit.Count, value=1)

    def sync(self, user_id: str, item_id: str) -> None:
        logger.debug("Begin transaction sync")

        try:
            item = datastore.get_item(user_id, item_id)
        except exceptions.ItemNotFoundException:
            logger.exception(f"Item {item_id} not found in DynamoDB")
            metrics.add_metric(name="ItemNotFound", unit=MetricUnit.Count, value=1)
            return

        access_token: str = item[constants.TOKEN_ATTRIBUTE_NAME]
        cursor: Union[None, str] = item.get(constants.CURSOR_ATTRIBUTE_NAME)

        added = []
        modified = []
        removed = []  # Removed transaction ids
        has_more = True

        # Iterate through each page of new transaction updates for item
        while has_more:
            metrics.add_metric(name="PlaidTransactionSyncRequest", unit=MetricUnit.Count, value=1)

            params = {
                "access_token": access_token,
                "count": constants.PLAID_TRANSACTION_SYNC_COUNT_MAX,
                "options": TransactionsSyncRequestOptions(include_personal_finance_category=True),
            }
            if cursor:
                params["cursor"] = cursor

            request = TransactionsSyncRequest(**params)

            try:
                response: TransactionsSyncResponse = self.client.transactions_sync(request)
            except plaid.ApiException:
                logger.exception("Failed to call transactions sync")
                raise

            # Add this page of results
            added.extend(response["added"])
            modified.extend(response["modified"])
            removed.extend(response["removed"])
            has_more = response["has_more"]

            # Update cursor to the next cursor
            cursor = response["next_cursor"]

        added = [
            self.build_message(user_id, item_id, "INSERT", transaction) for transaction in added
        ]
        modified = [
            self.build_message(user_id, item_id, "MODIFY", transaction) for transaction in modified
        ]
        removed = [
            self.build_message(user_id, item_id, "REMOVE", transaction) for transaction in removed
        ]

        all_transactions = added + modified + removed
        if all_transactions:
            self.send_messages(all_transactions)

        self.store_cursor(user_id, item_id, cursor)

        logger.debug("End transaction sync")

    def handle_webhook(
        self, user_id: str, item_id: str, webhook_code: str, payload: Dict[str, Any]
    ) -> None:
        """
        Handle transaction webhooks
        """

        # https://plaid.com/docs/api/products/transactions/#initial_update
        # https://plaid.com/docs/api/products/transactions/#default_update
        # https://plaid.com/docs/api/products/transactions/#historical_update
        if webhook_code in (
            constants.PLAID_WEBHOOK_CODE_INITIAL_UPDATE,
            constants.PLAID_WEBHOOK_CODE_HISTORICAL_UPDATE,
            constants.PLAID_WEBHOOK_CODE_DEFAULT_UPDATE,
        ):
            # Note: Plaid has deprecated these webhooks in favor of SYNC_UPDATES_AVAILABLE

            new_transactions: int = payload.get("new_transactions", 0)
            logger.info(f"{webhook_code}, new_transactions={new_transactions}")
            metrics.add_metric(
                name="WebhookNewTransactions", unit=MetricUnit.Count, value=new_transactions
            )

            if new_transactions < 1:
                logger.info("No new transactions found in webhook, skipping sync")
                return

            self.sync(user_id, item_id)

        # https://plaid.com/docs/api/products/transactions/#sync_updates_available
        elif webhook_code == constants.PLAID_WEBHOOK_CODE_SYNC_UPDATES_AVAILABLE:
            initial_update_complete: bool = payload.get("initial_update_complete", False)
            historical_update_complete: bool = payload.get("historical_update_complete", False)

            logger.info(
                f"{webhook_code}, initial_update_complete={initial_update_complete}, historical_update_complete={historical_update_complete}"
            )
            metrics.add_metric(name="WebhookSyncUpdatesAvailable", unit=MetricUnit.Count, value=1)

            self.sync(user_id, item_id)

        # https://plaid.com/docs/api/products/transactions/#transactions_removed
        elif webhook_code == constants.PLAID_WEBHOOK_CODE_TRANSACTIONS_REMOVED:
            # Note: Plaid has deprecated this webhook in favor of SYNC_UPDATES_AVAILABLE

            removed_transactions: List[str] = payload.get("removed_transactions", [])
            logger.info(f"{webhook_code}, removed_transactions={len(removed_transactions)}")
            metrics.add_metric(
                name="WebhookRemovedTransactions",
                unit=MetricUnit.Count,
                value=len(removed_transactions),
            )
            if not removed_transactions:
                return

            messages = [
                self.build_message(user_id, item_id, "REMOVE", transaction_id)
                for transaction_id in removed_transactions
            ]
            self.send_messages(messages)

        else:
            logger.warn(f"Unsupported webhook code: {webhook_code}")
            metrics.add_metric(name="UnknownWebhookCode", unit=MetricUnit.Count, value=1)
