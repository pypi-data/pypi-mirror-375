from argparse import ArgumentParser
from pathlib import Path

from argparse_schemas.jsonschema import argparse_to_json_schema


def test_empty_parser():
    parser = ArgumentParser()
    schema = argparse_to_json_schema(parser)
    assert schema == {
        "$schema": "https://json-schema.org/draft/2020-12/schema#",
        "properties": {},
        "required": [],
        "type": "object",
    }


def test_description():
    parser = ArgumentParser(description="A scientific program")
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "description": "A scientific program",
        }.items()
    )


def test_mandatory_arg():
    parser = ArgumentParser()
    parser.add_argument(
        "--mandatory", type=float, required=True, help="A required float"
    )
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "mandatory": {
                    "description": "A required float",
                    "type": "number",
                },
            },
            "required": ["mandatory"],
        }.items()
    )


def test_positional_nargs():
    parser = ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path, help="Required input file(s)")
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "files": {
                    "description": "Required input file(s)",
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
            },
            "required": ["files"],
        }.items()
    )


def test_optional_nargs_exact():
    parser = ArgumentParser()
    parser.add_argument("--values", type=int, nargs=3, help="Exactly three integers")
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "values": {
                    "description": "Exactly three integers",
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 3,
                    "maxItems": 3,
                },
            },
            "required": [],
        }.items()
    )


def test_optional_nargs_star():
    parser = ArgumentParser()
    parser.add_argument("--tags", type=str, nargs="*", help="Optional tags")
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "tags": {
                    "description": "Optional tags",
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 0,
                },
            },
            "required": [],
        }.items()
    )


def test_optional_nargs_plus():
    parser = ArgumentParser()
    parser.add_argument("--points", type=int, nargs="+", help="One or more integers")
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "points": {
                    "description": "One or more integers",
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 1,
                },
            },
            "required": [
                "points",
            ],
        }.items()
    )


def test_optional_nargs_question():
    parser = ArgumentParser()
    parser.add_argument("--maybe", nargs="?", help="Zero or one string")
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "maybe": {
                    "description": "Zero or one string",
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 0,
                    "maxItems": 1,
                },
            },
            "required": [],
        }.items()
    )


def test_choices():
    parser = ArgumentParser()
    parser.add_argument(
        "--mode", choices=["fast", "slow"], default="fast", help="Two choices"
    )
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "mode": {
                    "description": "Two choices",
                    "type": "string",
                    "enum": ["fast", "slow"],
                    "default": "fast",
                },
            },
            "required": [],
        }.items()
    )


def test_boolean_flags():
    parser = ArgumentParser()
    parser.add_argument(
        "--verbose", action="store_true", help="Boolean flag storing true"
    )
    parser.add_argument(
        "--quiet", action="store_false", help="Boolean flag storing false"
    )
    schema = argparse_to_json_schema(parser)
    assert (
        schema.items()
        >= {
            "type": "object",
            "properties": {
                "verbose": {
                    "description": "Boolean flag storing true",
                    "type": "boolean",
                    "default": False,
                },
                "quiet": {
                    "description": "Boolean flag storing false",
                    "type": "boolean",
                    "default": True,
                },
            },
            "required": [],
        }.items()
    )
