from typing import Callable

from dyngle.error import DyngleError
from dyngle.safe_path import SafePath

from datetime import datetime as datetime, date, timedelta
import math
import json
import re
import yaml


def formatted_datetime(dt: datetime, format_string=None) -> str:
    """Safe datetime formatting using string operations"""
    if format_string is None:
        format_string = "{year:04d}{month:02d}{day:02d}"
    components = {
        'year': dt.year,
        'month': dt.month,
        'day': dt.day,
        'hour': dt.hour,
        'minute': dt.minute,
        'second': dt.second,
        'microsecond': dt.microsecond,
        'weekday': dt.weekday(),  # Monday is 0
    }
    return format_string.format(**components)


GLOBALS = {
    "__builtins__": {
        # Basic data types and conversions
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,

        # Essential functions
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
    },

    # Mathematical operations
    "math": math,

    # Date and time handling
    "datetime": datetime,
    "date": date,
    "timedelta": timedelta,
    "formatted": formatted_datetime,

    # Data parsing and manipulation
    "json": json,
    "yaml": yaml,
    "re": re,

    # Safe Path-like operations (within cwd)
    "Path": SafePath
}


def _evaluate(expression: str, data: dict) -> str:
    try:
        result = eval(expression, GLOBALS, data)
    except KeyError:
        raise DyngleError(f"The following expression contains " +
                          f"at least one invalid name: {expression}")
    result = result[-1] if isinstance(result, tuple) else result
    return str(result)


def expression(text: str) -> Callable[[dict], str]:
    def evaluate(data: dict) -> str:
        return _evaluate(text, data)
    return evaluate
