from __future__ import annotations
from pydantic.fields import FieldInfo
from typing import Iterator, Literal, get_args, TYPE_CHECKING

if TYPE_CHECKING:
    from clipstick._tokens import Command, Subcommand


def call_stack_from_tokens(
    token: Command | Subcommand,
) -> Iterator[Command | Subcommand]:
    yield token
    if token.parent is None:
        return
    yield from call_stack_from_tokens(token.parent)


def is_literal(field_info: FieldInfo) -> bool:
    return getattr(field_info.annotation, "__origin__", None) == Literal


def name_from_annotation(field_info: FieldInfo) -> str:
    if not field_info.annotation:
        return "[unknown]"
    return field_info.annotation.__name__


def field_description(field_info: FieldInfo) -> str:
    """Return a description for a pydantic field.

    Consider a field a model property.
    """
    d = field_info.description
    if is_literal(field_info):
        options = get_args(field_info.annotation)
        _type = f"[allowed values: {', '.join(options)}]"
    else:
        _type = f"[{name_from_annotation(field_info)}]"

    return f"{d} {_type}"


def user_keys(user_keys: list[str]) -> str:
    return "/".join(user_keys)
