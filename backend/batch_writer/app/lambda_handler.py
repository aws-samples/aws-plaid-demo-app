#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any, List, Union, TYPE_CHECKING

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
import boto3

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBServiceResource
    from mypy_boto3_dynamodb.service_resource import Table

from app import constants, utils

TABLE_NAME = os.getenv("TABLE_NAME")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

tracer = Tracer()
logger = Logger(use_rfc3339=True, utc=True)
metrics = Metrics()
metrics.set_default_dimensions(environment=ENVIRONMENT)

dynamodb: "DynamoDBServiceResource" = boto3.resource("dynamodb", config=constants.BOTO3_CONFIG)
table: "Table" = dynamodb.Table(TABLE_NAME)


@metrics.log_metrics(capture_cold_start_metric=False)
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=False)
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = event.get("Records", [])
    if not records:
        metrics.add_metric(name="EmptyRecords", unit=MetricUnit.Count, value=1)
        return

    record_count = len(records)
    metrics.add_metric(name="RecordCount", unit=MetricUnit.Count, value=record_count)
    logger.info(f"Received {record_count} records")

    delete_count = 0
    put_count = 0

    with table.batch_writer(overwrite_by_pkeys=["pk", "sk"]) as batch:
        for record in records:
            item: Dict[str, Any] = json.loads(record["body"])
            event_name: Union[str, None] = (
                record.get("messageAttributes", {}).get("EventName", {}).get("stringValue")
            )

            if event_name == "DELETE":
                key = {
                    "pk": item["pk"],
                    "sk": item["sk"],
                }
                batch.delete_item(Key=key)
                delete_count += 1
            else:
                item = utils.floats_to_decimal(item)
                batch.put_item(Item=item)
                put_count += 1

    metrics.add_metric(name="PutItemCount", unit=MetricUnit.Count, value=put_count)
    metrics.add_metric(name="DeleteItemCount", unit=MetricUnit.Count, value=delete_count)

    put_percent = "{:.2%}".format(put_count / record_count)
    delete_percent = "{:.2%}".format(delete_count / record_count)

    logger.info(
        f"total = {record_count}, put = {put_count} ({put_percent}), delete = {delete_count} ({delete_percent})"
    )
