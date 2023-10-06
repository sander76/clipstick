from __future__ import annotations
from pydantic.fields import FieldInfo
from typing import Iterator, Literal, get_args, TYPE_CHECKING

from pydantic_core import PydanticUndefined

if TYPE_CHECKING:
    from clipstick._tokens import Command, Subcommand


def help(command: Command | Subcommand) -> None:
    print("")
    call_stack = list(call_stack_from_tokens(command))

    entry_point = " ".join(
        (user_keys(token.user_key) for token in reversed(call_stack))
    )

    _args_string = " ".join(user_keys(_arg.user_key) for _arg in command.args)
    _kwargs_string = " ".join(
        f"[{user_keys(_kwarg.user_key)}]" for _kwarg in command.optional_kwargs
    )
    _subcommands = ""
    if command.sub_commands:
        _subcommands = (
            "{" + ", ".join(sub.user_key[0] for sub in command.sub_commands) + "}"
        )
    _all = " ".join(
        (arg for arg in (_args_string, _kwargs_string, _subcommands) if arg)
    )
    print(f"usage: {entry_point} [-h] {_all}")
    print("")
    print(command.cls.__doc__)
    if command.args:
        print("")
        print("positional arguments:")
        for arg in command.args:
            print(
                f"    {user_keys(arg.user_key):<25}{field_description(arg.field_info)}"
            )
    if command.optional_kwargs:
        print("")
        print("optional keyword arguments:")
        for kwarg in command.optional_kwargs:
            print(
                f"    {user_keys(kwarg.user_key):<25}{field_description(kwarg.field_info)}"
            )
    if command.sub_commands:
        print("")
        print("subcommands:")
        for sub_command in command.sub_commands:
            print(f"    {user_keys(sub_command.user_key):<25}{sub_command.cls.__doc__}")


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

    if field_info.default is not PydanticUndefined:
        _type = _type + f"[default={field_info.default}]"
    return f"{d} {_type}"


def user_keys(user_keys: list[str]) -> str:
    return "/".join(user_keys)
