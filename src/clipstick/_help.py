from __future__ import annotations
from pydantic.fields import FieldInfo
from typing import Iterator, Literal, get_args, TYPE_CHECKING
from rich.text import Text
from rich.console import Console
from rich.table import Table

console = Console()
if TYPE_CHECKING:
    from clipstick._tokens import Command, Subcommand


def help(command: Command | Subcommand) -> None:
    indent = 2
    min_args_width = 20
    call_stack = list(call_stack_from_tokens(command))

    entry_point = " ".join(
        ("/".join(token.user_keys) for token in reversed(call_stack))
    )

    usage_line = Text()
    usage_line.append("Usage: ", style="magenta")
    usage_line.append(entry_point)
    if command.args:
        usage_line.append(" [Arguments]")
    if command.optional_kwargs:
        usage_line.append(" [Options]")
    if command.sub_commands:
        usage_line.append(" [Subcommands]")
    console.print(usage_line)
    console.print("")
    console.print(command.cls.__doc__)

    if command.args:
        tbl = Table.grid(collapse_padding=True, padding=(0, 1))
        tbl.add_column(width=indent)  # empty column
        tbl.add_column(min_width=min_args_width)
        tbl.add_column()
        tbl.add_column()

        console.print("")
        console.print("Arguments:", style="bold")
        for arg in command.args:
            tbl.add_row(
                "",
                user_keys(arg.user_keys),
                field_description(arg.field_info),
                Text(f"[{type_from_annotation(arg.field_info)}]"),
            )
        console.print(tbl)
    if command.optional_kwargs:
        tbl = Table.grid(collapse_padding=True, padding=(0, 1))
        tbl.add_column(width=indent)  # empty column
        tbl.add_column(min_width=0)  # for the shorthands.
        tbl.add_column(min_width=min_args_width)  # keys
        tbl.add_column()  # description
        tbl.add_column()  # type
        tbl.add_column()  # default

        console.print("")
        console.print("Options:", style="bold")
        for kwarg in command.optional_kwargs:
            tbl.add_row(
                "",
                user_keys(kwarg.short_keys),
                user_keys(kwarg.keys),
                field_description(kwarg.field_info),
                Text(f"[{type_from_annotation(kwarg.field_info)}]"),
                Text(f"[default = {add_default(kwarg.field_info)}]"),
            )
        console.print(tbl)
    if command.sub_commands:
        tbl = Table.grid(collapse_padding=True, padding=(0, 1))
        tbl.add_column(width=indent)  # empty column
        tbl.add_column(min_width=min_args_width)  # commands
        tbl.add_column()  # description

        console.print("")
        console.print("Subcommands:", style="bold")

        for sub_command in command.sub_commands:
            tbl.add_row("", user_keys(sub_command.user_keys), sub_command.cls.__doc__)
        console.print(tbl)


# def _help(command: Command | Subcommand) -> None:
#     call_stack = list(call_stack_from_tokens(command))

#     entry_point = " ".join(
#         (user_keys(token.user_key) for token in reversed(call_stack))
#     )

#     usage_line = ["Usage:"]
#     usage_line.append(entry_point)
#     if command.args:
#         usage_line.append("[Arguments]")
#     if command.optional_kwargs:
#         usage_line.append("[Options]")
#     if command.sub_commands:
#         usage_line.append("[Subcommands]")

#     print(" ".join(usage_line))
#     print("")
#     print(command.cls.__doc__)
#     if command.args:
#         print("")
#         print("Arguments:")
#         for arg in command.args:
#             print(
#                 f"    {user_keys(arg.user_key):<25}{field_description(arg.field_info)}"
#             )
#     if command.optional_kwargs:
#         print("")
#         print("Options:")
#         for kwarg in command.optional_kwargs:
#             print(
#                 f"    {user_keys(kwarg.user_key):<25}{field_description(kwarg.field_info)}"
#             )
#     if command.sub_commands:
#         print("")
#         print("Subcommands:")
#         for sub_command in command.sub_commands:
#             print(f"    {user_keys(sub_command.user_key):<25}{sub_command.cls.__doc__}")


def call_stack_from_tokens(
    token: Command | Subcommand,
) -> Iterator[Command | Subcommand]:
    yield token
    if token.parent is None:
        return
    yield from call_stack_from_tokens(token.parent)


def is_literal(field_info: FieldInfo) -> bool:
    return getattr(field_info.annotation, "__origin__", None) == Literal


def type_from_annotation(field_info: FieldInfo) -> str:
    if not field_info.annotation:
        return "unknown"
    if is_literal(field_info):
        options = get_args(field_info.annotation)
        return f"allowed values: {', '.join(options)}"
    return field_info.annotation.__name__


def field_description(field_info: FieldInfo) -> str:
    """Return a description for a pydantic field."""

    d = field_info.description
    if d is None:
        return ""
    return d


def add_default(field_info: FieldInfo) -> str:
    return field_info.default


def user_keys(user_keys: list[str]) -> Text:
    return Text("/".join(user_keys), style="magenta")
