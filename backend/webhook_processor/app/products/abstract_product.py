#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC
from itertools import batched
import os
from typing import Dict, Any, List, TYPE_CHECKING

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
import boto3
import botocore
from plaid.api import plaid_api

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBServiceResource
    from mypy_boto3_dynamodb.service_resource import Table
    from mypy_boto3_sqs import SQSClient

from app import utils, constants

__all__ = ["AbstractProduct"]

QUEUE_URL = os.getenv("QUEUE_URL")
TABLE_NAME = os.getenv("TABLE_NAME")

logger = Logger(child=True)
metrics = Metrics()


class AbstractProduct(ABC):
    def __init__(self, client: plaid_api.PlaidApi = None, session: boto3.Session = None):
        if not session:
            session = boto3._get_default_session()
        if not client:
            client = utils.get_plaid_client()

        self.client = client

        dynamodb: "DynamoDBServiceResource" = session.resource(
            "dynamodb", config=constants.BOTO3_CONFIG
        )
        self.dynamodb: "Table" = dynamodb.Table(TABLE_NAME)
        self.sqs: "SQSClient" = session.client("sqs", config=constants.BOTO3_CONFIG)

    def send_messages(self, messages: List[Dict[str, Any]]) -> None:
        # remove any messages that are None
        messages = list(filter(None, messages))

        if not messages:
            metrics.add_metric(name="SQSEmptyBatch", unit=MetricUnit.Count, value=1)
            logger.warning("Not sending empty batch of messages")
            return

        for batch in batched(messages, constants.SQS_SEND_MESSAGE_BATCH_MAX):
            self._send_messages(batch)

    def _send_messages(self, messages: List[Dict[str, Any]]) -> None:
        """
        Batch send a list of messages to SQS
        """

        message_count = len(messages)
        if not message_count:
            metrics.add_metric(name="SQSEmptyBatch", unit=MetricUnit.Count, value=1)
            logger.warning("Not sending empty batch of messages")
            return

        if message_count > constants.SQS_SEND_MESSAGE_BATCH_MAX:
            metrics.add_metric(name="SQSBatchTooLarge", unit=MetricUnit.Count, value=1)
            raise Exception(
                f"Too many messages in SQS batch: {message_count} > {constants.SQS_SEND_MESSAGE_BATCH_MAX}"
            )

        logger.debug(f"Sending {len(messages)} messages to SQS")

        params = {
            "QueueUrl": QUEUE_URL,
            "Entries": messages,
        }

        try:
            response = self.sqs.send_message_batch(**params)
        except botocore.exceptions.ClientError:
            logger.exception("Failed to send messages to SQS")
            metrics.add_metric(name="SQSSendException", unit=MetricUnit.Count, value=1)
            raise

        successful = response.get("Successful", [])
        if successful:
            metrics.add_metric(name="SQSSendSuccess", unit=MetricUnit.Count, value=len(successful))

        failed = response.get("Failed", [])
        if failed:
            metrics.add_metric(name="SQSSendFailed", unit=MetricUnit.Count, value=len(failed))
            logger.error(failed)
