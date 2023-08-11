#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import List, Dict, Any, Union

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecord,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from app import constants, products, datastore

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

tracer = Tracer()
logger = Logger(use_rfc3339=True, utc=True)
metrics = Metrics()
metrics.set_default_dimensions(environment=ENVIRONMENT)
dynamodb_processor = BatchProcessor(event_type=EventType.DynamoDBStreams)
sqs_processor = BatchProcessor(event_type=EventType.SQS)

transactions = products.Transactions()
accounts_balance = products.AccountsBalance()
liabilities = products.Liabilities()
investments_transactions = products.InvestmentsTransactions()
investments_holdings = products.InvestmentsHoldings()


def record_handler(record: Union[DynamoDBRecord, SQSRecord]) -> None:
    # New items added to DynamoDB via API
    if isinstance(record, DynamoDBRecord):
        sk: str = record.dynamodb.new_image.get("sk", "")

        parts: List[str] = sk.split("#", 3)
        if len(parts) == 4:
            user_id = parts[1]
            item_id = parts[3]
        else:
            logger.error(f"Skipping invalid DynamoDB key: {sk}")
            return

        logger.append_keys(item_id=item_id, user_id=user_id)
        tracer.put_annotation(key="ItemId", value=item_id)
        tracer.put_annotation(key="UserId", value=user_id)
        transactions.sync(user_id, item_id)

    # Incoming Webhooks from SQS
    elif isinstance(record, SQSRecord):
        item_id: str = record.message_attributes["ItemId"].string_value
        logger.append_keys(item_id=item_id)
        tracer.put_annotation(key="ItemId", value=item_id)

        if "UserId" in record.message_attributes:
            user_id: str = record.message_attributes["UserId"].string_value
        else:
            user_id = datastore.get_user_by_item(item_id)
            if not user_id:
                logger.warn(f"Item {item_id} not found")
                return

        logger.append_keys(user_id=user_id)
        tracer.put_annotation(key="UserId", value=user_id)

        webhook_type: str = record.message_attributes["WebhookType"].string_value
        webhook_code: str = record.message_attributes["WebhookCode"].string_value

        logger.info(f"Processing webhook type: {webhook_type}, code: {webhook_code}")

        try:
            payload: Dict[str, Any] = json.loads(record.body)
        except ValueError:
            logger.exception(f"Webhook payload is invalid JSON: {record.body}")
            return

        # refresh all balances on the item
        accounts_balance.get_balances(user_id, item_id)

        # https://plaid.com/docs/api/products/transactions/#webhooks
        if webhook_type == constants.PLAID_WEBHOOK_TYPE_TRANSACTIONS:
            transactions.handle_webhook(user_id, item_id, webhook_code, payload)

        # https://plaid.com/docs/api/products/liabilities/#webhooks
        elif webhook_type == constants.PLAID_WEBHOOK_TYPE_LIABILITIES:
            liabilities.handle_webhook(user_id, item_id, webhook_code, payload)

        # https://plaid.com/docs/api/products/investments/#holdings-default_update
        elif webhook_type == constants.PLAID_WEBHOOK_TYPE_HOLDINGS:
            investments_holdings.handle_webhook(user_id, item_id, webhook_code, payload)

        # https://plaid.com/docs/api/products/investments/#investments_transactions-default_update
        elif webhook_type == constants.PLAID_WEBHOOK_TYPE_INVESTMENTS_TRANSACTIONS:
            investments_transactions.handle_webhook(user_id, item_id, webhook_code, payload)

        elif webhook_type == constants.PLAID_WEBHOOK_TYPE_BALANCE:
            pass

        else:
            logger.warn(f"Unsupported webhook type: {webhook_type}")
            metrics.add_metric(name="UnknownWebhookType", unit=MetricUnit.Count, value=1)

    else:
        logger.warn(f"Unsupported event source: {record.event_source}")
        metrics.add_metric(name="UnknownEventSource", unit=MetricUnit.Count, value=1)


@metrics.log_metrics(capture_cold_start_metric=False)
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = event.get("Records", [])
    if not records:
        metrics.add_metric(name="EmptyRecords", unit=MetricUnit.Count, value=1)
        return

    event_source: Union[None, str] = records[0].get("eventSource")

    if event_source == constants.DYNAMODB_EVENT_SOURCE:
        with dynamodb_processor(records=records, handler=record_handler):
            dynamodb_processor.process()

        return dynamodb_processor.response()
    elif event_source == constants.SQS_EVENT_SOURCE:
        with sqs_processor(records=records, handler=record_handler):
            sqs_processor.process()

        return sqs_processor.response()
