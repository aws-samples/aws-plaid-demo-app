#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import List, Dict, Any, TYPE_CHECKING

from aws_lambda_powertools import Logger
import boto3
import botocore

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBServiceResource, DynamoDBClient
    from mypy_boto3_dynamodb.paginator import QueryPaginator
    from mypy_boto3_dynamodb.service_resource import Table

from app import constants

__all__ = ["check_institution", "delete_transactions"]


TABLE_NAME = os.getenv("TABLE_NAME")

logger = Logger(child=True)

dynamodb: "DynamoDBServiceResource" = boto3.resource("dynamodb", config=constants.BOTO3_CONFIG)
table: "Table" = dynamodb.Table(TABLE_NAME)
dynamodb_client: "DynamoDBClient" = dynamodb.meta.client


def check_institution(user_id: str, institution_id: str) -> bool:
    """
    Check whether a given user has already linked to a specific institution ID
    """
    params = {
        "Key": {
            "pk": f"USER#{user_id}#INSTITUTIONS",
            "sk": f"INSTITUTION#{institution_id}",
        },
        "ProjectionExpression": "#pk, #sk",
        "ExpressionAttributeNames": {
            "#pk": "pk",
            "#sk": "sk",
        },
        "ConsistentRead": True,
    }

    try:
        response = table.get_item(**params)
    except botocore.exceptions.ClientError:
        logger.exception("Unable to get item from DynamoDB")
        raise

    return bool(response.get("Item", False))


def delete_items(user_id: str, item_id: str) -> None:
    params = {
        "TableName": TABLE_NAME,
        "Select": "SPECIFIC_ATTRIBUTES",
        "ProjectionExpression": "#pk, #sk",
        "KeyConditionExpression": "#pk = :pk",
        "ExpressionAttributeNames": {
            "#pk": "pk",
            "#sk": "sk",
        },
        "ExpressionAttributeValues": {
            ":pk": f"USER#{user_id}#ITEM#{item_id}",
        },
        "PaginationConfig": {
            "PageSize": 1000,
        },
    }
    paginator: QueryPaginator = dynamodb_client.get_paginator("query")
    page_iterator = paginator.paginate(**params)

    with table.batch_writer() as batch:
        for page in page_iterator:
            items: List[Dict[str, Any]] = page.get("Items", [])
            for item in items:
                key = {
                    "pk": item["pk"],
                    "sk": item["sk"],
                }
                batch.delete_item(Key=key)
