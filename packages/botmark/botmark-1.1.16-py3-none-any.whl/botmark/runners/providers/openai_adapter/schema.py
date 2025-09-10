from __future__ import annotations
import json
from typing import Any, Dict, Optional

try:
    from jsonschema import Draft202012Validator
    _HAS_JSONSCHEMA = True
except Exception:
    Draft202012Validator = None  # type: ignore
    _HAS_JSONSCHEMA = False

class JsonSchemaOutputValidator:
    def __init__(self, schema: Dict[str, Any], strict: bool = True):
        self._schema = schema
        self._validator = Draft202012Validator(schema) if (_HAS_JSONSCHEMA and strict) else None

    def validate(self, json_str: str) -> Any:
        try:
            obj = json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Model did not return valid JSON: {e}")
        if self._validator:
            errors = list(self._validator.iter_errors(obj))
            if errors:
                err = errors[0]
                path = list(err.absolute_path)
                raise ValueError(f"JSON did not match schema at {path}: {err.message}")
        return obj
