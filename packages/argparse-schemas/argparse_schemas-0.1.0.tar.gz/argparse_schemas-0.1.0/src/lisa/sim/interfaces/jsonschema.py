from argparse import SUPPRESS, ArgumentParser
from dataclasses import dataclass
from typing import Any


@dataclass
class Property:
    schema: dict
    required: bool = False


def _action_to_json_schema_property(action: Any) -> Property:
    """Convert an argparse action to a JSON schema property."""
    # Base schema for this property
    prop: dict[str, Any] = {
        "description": action.help or "",
    }

    # Argument type
    base_type = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
    }.get(action.type or type(action.const), "string")

    # Handle nargs
    if action.nargs is None or action.nargs == 0:
        # single value
        prop["type"] = base_type
    else:
        # list of values
        prop["type"] = "array"
        prop["items"] = {"type": base_type}

        if isinstance(action.nargs, int):
            prop["minItems"] = action.nargs
            prop["maxItems"] = action.nargs
        elif action.nargs == "+":
            prop["minItems"] = 1
        elif action.nargs == "*":
            prop["minItems"] = 0
        elif action.nargs == "?":
            prop["minItems"] = 0
            prop["maxItems"] = 1

    # Default
    if action.default not in (None, SUPPRESS):
        prop["default"] = action.default

    # Choices
    if action.choices:
        if prop.get("type") == "array":
            prop["items"]["enum"] = list(action.choices)
        else:
            prop["enum"] = list(action.choices)

    # Optionality
    if action.required or action.nargs in ("+",):
        return Property(prop, True)
    return Property(prop)


def argparse_to_json_schema(parser: ArgumentParser) -> dict:
    """Get the JSON schema corresponding to an argument parser spec."""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema#",
        "type": "object",
        "properties": {},
        "required": [],
    }

    if parser.description is not None:
        schema["description"] = parser.description

    for action in parser._actions:
        # Skip help and suppressed args
        if action.dest in ("help", SUPPRESS):
            continue

        prop = _action_to_json_schema_property(action)
        schema["properties"][action.dest] = prop.schema
        if prop.required:
            schema["required"].append(action.dest)

    return schema
