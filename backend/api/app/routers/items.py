#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from operator import itemgetter
from typing import Dict, Any, List, Union

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler.api_gateway import Router, Response
from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.event_handler.exceptions import InternalServerError
import boto3
import botocore
from mypy_boto3_dynamodb import DynamoDBServiceResource, DynamoDBClient
from mypy_boto3_dynamodb.paginator import QueryPaginator
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_sqs.client import SQSClient

from app import constants, datastore, utils

__all__ = ["router"]

TABLE_NAME = os.getenv("TABLE_NAME")
WEBHOOK_QUEUE_URL = os.getenv("WEBHOOK_QUEUE_URL")

tracer = Tracer()
logger = Logger()
metrics = Metrics()
router = Router()

dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb", config=constants.BOTO3_CONFIG)
table: Table = dynamodb.Table(TABLE_NAME)
dynamodb_client: DynamoDBClient = dynamodb.meta.client
sqs: SQSClient = boto3.client("sqs", config=constants.BOTO3_CONFIG)


@router.get("/")
@tracer.capture_method(capture_response=False)
def get_items(limit: int = 10, cursor: Union[str, None] = None) -> Dict[str, Any]:
    user_id: str = utils.authorize_request(router)

    tracer.put_annotation(key="UserId", value=user_id)

    params = {
        "Select": "SPECIFIC_ATTRIBUTES",
        "KeyConditionExpression": "#pk = :pk",
        "ProjectionExpression": "#sk, #id, #name",
        "ExpressionAttributeNames": {
            "#pk": "pk",
            "#sk": "sk",
            "#id": "institution_id",
            "#name": "institution_name",
        },
        "ExpressionAttributeValues": {
            ":pk": f"USER#{user_id}#ITEMS",
        },
    }
    if cursor:
        params["ExclusiveStartKey"] = json.loads(utils.decode_data(cursor))

    if limit > constants.MAX_LIMIT:
        limit = constants.MAX_LIMIT
    elif limit < 1:
        limit = 1

    params["Limit"] = int(limit)

    logger.debug(params)

    response = table.query(**params)

    cursor = response.get("LastEvaluatedKey")
    if cursor:
        cursor = utils.encode_data(utils.json_dumps(cursor))

    data = {"cursor": cursor, "items": []}

    for item in response.get("Items", []):
        item["item_id"] = item["sk"].split("#").pop()
        del item["sk"]

        data["items"].append(item)

    return data


@router.get("/<item_id>/accounts")
@tracer.capture_method(capture_response=False)
def get_balances(item_id: str) -> Dict[str, Any]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(item_id=item_id, user_id=user_id)
    tracer.put_annotation(key="ItemId", value=item_id)
    tracer.put_annotation(key="UserId", value=user_id)

    params = {
        "TableName": TABLE_NAME,
        "Select": "ALL_ATTRIBUTES",
        "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
        "ExpressionAttributeNames": {
            "#pk": "pk",
            "#sk": "sk",
        },
        "ExpressionAttributeValues": {
            ":pk": f"USER#{user_id}#ITEM#{item_id}",
            ":sk": "ACCOUNT#",
        },
    }
    logger.debug(params)

    accounts = []

    paginator: QueryPaginator = dynamodb_client.get_paginator("query")
    page_iterator = paginator.paginate(**params)
    for page in page_iterator:
        items: List[Dict[str, Any]] = page.get("Items", [])
        for item in items:
            del item["pk"]
            del item["sk"]
            accounts.append(item)

    data = sorted(accounts, key=itemgetter("name"))

    response = {"accounts": data}

    return response


@router.get("/<item_id>/transactions")
@tracer.capture_method(capture_response=False)
def get_transactions(item_id: str) -> Dict[str, Any]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(item_id=item_id, user_id=user_id)
    tracer.put_annotation(key="ItemId", value=item_id)
    tracer.put_annotation(key="UserId", value=user_id)

    try:
        limit = int(router.current_event.get_query_string_value(name="limit", default_value="10"))
    except ValueError:
        limit = 10

    cursor = router.current_event.get_query_string_value(name="cursor")

    params = {
        "Select": "ALL_ATTRIBUTES",
        "KeyConditionExpression": "#pk = :pk AND begins_with(#sk, :sk)",
         "ExpressionAttributeNames": {
            "#pk": "pk",
            "#sk": "sk",
        },
        "ExpressionAttributeValues": {
            ":pk": f"USER#{user_id}#ITEM#{item_id}",
            ":sk": "TRANSACTION#"
        },
    }
    if cursor:
        params["ExclusiveStartKey"] = json.loads(utils.decode_data(cursor))

    if limit > constants.MAX_LIMIT:
        limit = constants.MAX_LIMIT
    elif limit < 1:
        limit = 1

    params["Limit"] = limit

    logger.debug(params)

    response = table.query(**params)

    cursor = response.get("LastEvaluatedKey")
    if cursor:
        cursor = utils.encode_data(utils.json_dumps(cursor))

    data = {"cursor": cursor, "transactions": []}

    for item in response.get("Items", []):
        del item["pk"]
        del item["sk"]

        data["transactions"].append(item)

    return data


@router.post("/<item_id>/refresh")
@tracer.capture_method(capture_response=False)
def post_refresh(item_id: str) -> Dict[str, Any]:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(item_id=item_id, user_id=user_id)
    tracer.put_annotation(key="ItemId", value=item_id)
    tracer.put_annotation(key="UserId", value=user_id)

    params = {
        "QueueUrl": WEBHOOK_QUEUE_URL,
        "DelaySeconds": 0,
        "MessageAttributes": {
            "WebhookType": {
                "DataType": "String",
                "StringValue": "BALANCE",
            },
            "WebhookCode": {
                "DataType": "String",
                "StringValue": "DEFAULT_UPDATE",
            },
            "ItemId": {
                "DataType": "String",
                "StringValue": item_id,
            },
            "UserId": {
                "DataType": "String",
                "StringValue": user_id,
            },
        },
        "MessageBody": "{}",  # needs to be an empty JSON body
        "MessageDeduplicationId": "BALANCE_DEFAULT_UPDATE",
        "MessageGroupId": item_id,
    }

    metrics.add_metric(name="SendCount", unit=MetricUnit.Count, value=1)
    logger.debug(f"Sending message to SQS: {params}")

    try:
        sqs.send_message(**params)
        logger.debug("Sent message to SQS")
        metrics.add_metric(name="SendSuccess", unit=MetricUnit.Count, value=1)
    except botocore.exceptions.ClientError:
        logger.exception("Failed to send message to SQS")
        metrics.add_metric(name="SendFailed", unit=MetricUnit.Count, value=1)
        raise

    response = Response(status_code=202, content_type=content_types.APPLICATION_JSON, body="")

    return response


@router.delete("/<item_id>")
@tracer.capture_method(capture_response=False)
def delete_item(item_id: str) -> Response:
    user_id: str = utils.authorize_request(router)

    logger.append_keys(item_id=item_id, user_id=user_id)
    tracer.put_annotation(key="ItemId", value=item_id)
    tracer.put_annotation(key="UserId", value=user_id)

    params = {
        "Key": {
            "pk": f"USER#{user_id}#ITEM#{item_id}",
            "sk": "v0",
        },
        "ProjectionExpression": "#i",
        "ExpressionAttributeNames": {
            "#i": "institution_id",
        },
    }
    logger.debug(params)

    try:
        response = table.get_item(**params)
    except botocore.exceptions.ClientError:
        logger.exception("Unable to get item")
        raise InternalServerError("Unable to get item")

    institution_id: Union[str, None] = response.get("Item", {}).get("institution_id")

    items = [
        {
            "Delete": {
                "TableName": TABLE_NAME,
                "Key": {
                    "pk": f"USER#{user_id}#ITEM#{item_id}",
                    "sk": "v0",
                },
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        },
        {
            "Delete": {
                "TableName": TABLE_NAME,
                "Key": {
                    "pk": f"USER#{user_id}#INSTITUTIONS",
                    "sk": f"INSTITUTION#{institution_id}",
                },
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        },
        {
            "Delete": {
                "TableName": TABLE_NAME,
                "Key": {
                    "pk": f"USER#{user_id}#ITEMS",
                    "sk": f"ITEM#{item_id}",
                },
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        },
        {
            "Delete": {
                "TableName": TABLE_NAME,
                "Key": {
                    "pk": "ITEMS",
                    "sk": f"USER#{user_id}#ITEM#{item_id}",
                },
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        },
        {
            "Delete": {
                "TableName": TABLE_NAME,
                "Key": {
                    "pk": f"ITEM#{item_id}",
                    "sk": f"USER#{user_id}",
                },
                "ConditionExpression": "attribute_exists(pk) AND attribute_exists(sk)",
            }
        },
    ]

    metrics.add_metric(name="DeleteItem", unit=MetricUnit.Count, value=1)
    logger.debug(f"Deleting items to DynamoDB: {items}")

    try:
        dynamodb_client.transact_write_items(TransactItems=items)
        logger.debug("Deleted items to DynamoDB")
        metrics.add_metric(name="DeleteItemSuccess", unit=MetricUnit.Count, value=1)
    except botocore.exceptions.ClientError:
        logger.exception("Failed to delete items to DynamoDB")
        metrics.add_metric(name="DeleteItemFailed", unit=MetricUnit.Count, value=1)
        # raise

    datastore.delete_items(user_id, item_id)

    response = Response(status_code=204, content_type=content_types.APPLICATION_JSON, body="")

    return response
