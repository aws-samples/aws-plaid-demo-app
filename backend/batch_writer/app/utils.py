#!/usr/bin/env python
# -*- coding: utf-8 -*-

from decimal import Decimal
from typing import Any

__all__ = ["floats_to_decimal"]


def floats_to_decimal(obj: Any) -> Any:
    """
    Convert floats to Decimal
    """
    if isinstance(obj, float):
        obj = Decimal(str(obj))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = floats_to_decimal(value)
    elif isinstance(obj, list):
        obj = [floats_to_decimal(value) for value in obj]
    return obj
