#!/usr/bin/env python
# -*- coding: utf-8 -*-

WEBHOOK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "properties": {
        "webhook_type": {"type": "string"},
        "webhook_code": {"type": "string"},
        "item_id": {"type": "string"},
    },
    "required": ["webhook_type", "webhook_code", "item_id"],
}

METADATA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "properties": {
        "institution": {
            "type": "object",
            "properties": {
                "institution_id": {
                    "type": "string",
                }
            },
            "required": ["institution_id"],
        },
    },
    "required": ["institution"],
}
