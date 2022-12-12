#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import Dict, Any

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, CORSConfig

from app import routers

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

tracer = Tracer()
logger = Logger()
metrics = Metrics()
metrics.set_default_dimensions(environment=ENVIRONMENT)

cors_config = CORSConfig()
resolver = APIGatewayHttpResolver(cors=CORSConfig())
resolver.include_router(routers.items_router, prefix="/v1/items")
resolver.include_router(routers.tokens_router, prefix="/v1/tokens")
resolver.include_router(routers.webhook_router, prefix="/v1/webhook")


@metrics.log_metrics(capture_cold_start_metric=True)
@tracer.capture_lambda_handler
@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_HTTP, log_event=True
)
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    return resolver.resolve(event, context)
