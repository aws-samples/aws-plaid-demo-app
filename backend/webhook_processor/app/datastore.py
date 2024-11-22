#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import Union, Dict, Any, TYPE_CHECKING

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
import boto3
from boto3.dynamodb.conditions import Key
import botocore
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import AwsKmsCryptographicMaterialsProvider
from dynamodb_encryption_sdk.structures import AttributeActions

if TYPE_CHECKING:
    from mypy_boto3_dynamodb import DynamoDBServiceResource
    from mypy_boto3_dynamodb.service_resource import Table

from app import constants, exceptions

__all__ = ["get_user_by_item", "get_item"]


TABLE_NAME = os.getenv("TABLE_NAME")
KEY_ARN = os.getenv("KEY_ARN")

logger = Logger(child=True)
metrics = Metrics()

dynamodb: "DynamoDBServiceResource" = boto3.resource("dynamodb", config=constants.BOTO3_CONFIG)
table: "Table" = dynamodb.Table(TABLE_NAME)
aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=KEY_ARN)
actions = AttributeActions(
    default_action=CryptoAction.DO_NOTHING,
    attribute_actions={constants.TOKEN_ATTRIBUTE_NAME: CryptoAction.ENCRYPT_AND_SIGN},
)
encrypted_table = EncryptedTable(
    table=table,
    materials_provider=aws_kms_cmp,
    attribute_actions=actions,
)


def get_user_by_item(item_id: str) -> Union[str, None]:
    """
    Return the user ID for a given item ID
    """
    params = {
        "ExpressionAttributeNames": {
            "#sk": "sk",
        },
        "KeyConditionExpression": Key("pk").eq(f"ITEM#{item_id}"),
        "Limit": 1,
        "ProjectionExpression": "#sk",
        "Select": "SPECIFIC_ATTRIBUTES",
    }
    logger.debug(params)

    try:
        response = table.query(**params)
    except botocore.exceptions.ClientError:
        logger.exception("Unable to get item from DynamoDB")
        raise

    for item in response.get("Items", []):
        return item["sk"].replace("USER#", "")

    return None


def get_item(user_id: str, item_id: str) -> Dict[str, Any]:
    """
    Get the item from DynamoDB
    """

    params = {
        "Key": {
            "pk": f"USER#{user_id}#ITEM#{item_id}",
            "sk": "v0",
        },
        "ConsistentRead": True,
    }
    logger.debug(params)

    try:
        response = encrypted_table.get_item(**params)
        metrics.add_metric(name="GetItemSuccess", unit=MetricUnit.Count, value=1)
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            raise exceptions.ItemNotFoundException(f"Item {item_id} not found in DynamoDB")

        logger.exception("Failed to get item from DynamoDB")
        metrics.add_metric(name="GetItemFailed", unit=MetricUnit.Count, value=1)
        raise

    item = response.get("Item", {})
    if not item:
        raise exceptions.ItemNotFoundException(f"Item {item_id} not found in DynamoDB")

    item = {
        k: v
        for k, v in item.items()
        if k in [constants.TOKEN_ATTRIBUTE_NAME, constants.CURSOR_ATTRIBUTE_NAME]
    }

    return item
