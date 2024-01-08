from __future__ import annotations

import os
from inspect import cleandoc
from typing import TYPE_CHECKING, Iterator

from rich.console import Console
from rich.table import Table
from rich.text import Text

from clipstick._exceptions import ClipStickError
from clipstick._style import ARGUMENT_HEADER, ARGUMENTS_STYLE, DOCSTRING, ERROR
from clipstick._tokens import THelp

# If you want to capture console output and set a width to properly word-wrap it,
# you can set this env variable.
# Have a look at `cogger.py (the capture function)` for an example.
record_width = os.getenv("CLIPSTICK_CONSOLE_WIDTH")

console = Console(width=int(record_width) if record_width else None)

if TYPE_CHECKING:  # pragma: no cover
    from clipstick._tokens import Command, Subcommand


def suggest_help():
    suggest_help = Text.assemble(
        "Use the", Text("-h", ARGUMENTS_STYLE), " argument to help"
    )
    console.print(suggest_help)


def error(message: Text | str | ClipStickError):
    console.print("ERROR: ", style=ERROR, end="")
    console.print(message)


def _help_from_token(help_info: THelp, short=False) -> tuple[Text, Text]:
    args = Text(help_info["arguments"], ARGUMENTS_STYLE)

    txt = Text()
    if desc := help_info["description"]:
        if short:
            txt.append(desc.split("\n")[0])
        else:
            txt.append(desc)
    if _type := help_info["type"]:
        txt.append(Text(f" [{_type}]"))
    if default := help_info["default"]:
        txt.append(Text(f" [{default}]"))

    return args, txt


def help(command: Command | Subcommand) -> None:
    indent = 2
    min_args_width = 20
    call_stack = list(call_stack_from_tokens(command))

    entry_point = " ".join(
        ("/".join(token.user_keys) for token in reversed(call_stack))
    )

    # print the first usage line
    # example: dummy-entrypoint second-level-model-one [Options] [Subcommands]
    console.print("")
    usage_line = Text.assemble(Text("Usage: ", style="bold"), entry_point)

    arguments = [token for token in command.tokens.values() if token.required]
    options = [token for token in command.tokens.values() if not token.required]
    if arguments:
        usage_line.append(" [Arguments]")
    if options:
        usage_line.append(" [Options]")
    if command.sub_commands:
        usage_line.append(" [Subcommands]")
    console.print(usage_line)

    # the class docstring as general help
    if command.cls.__doc__:
        console.print("")
        console.print(Text(cleandoc(command.cls.__doc__), style=DOCSTRING))

    if arguments:
        console.print("")
        console.print("Arguments:", style=ARGUMENT_HEADER)
        for arg in arguments:
            tbl = Table.grid(collapse_padding=True, padding=(0, 1))
            tbl.add_column(width=indent)  # empty column
            tbl.add_column(min_width=min_args_width)
            tbl.add_column()

            tbl.add_row("", *_help_from_token(arg.help()))
            console.print(tbl)
    if options:
        console.print("")
        console.print("Options:", style=ARGUMENT_HEADER)
        for kwarg in options:
            tbl = Table.grid(collapse_padding=True, padding=(0, 1))
            tbl.add_column(width=indent)  # empty column
            tbl.add_column(min_width=min_args_width)  # keys
            tbl.add_column()  # description
            tbl.add_row("", *_help_from_token(kwarg.help()))
            console.print(tbl)
    if command.sub_commands:
        console.print("")
        console.print("Subcommands:", style=ARGUMENT_HEADER)

        for sub_command in command.sub_commands:
            tbl = Table.grid(collapse_padding=True, padding=(0, 1))
            tbl.add_column(width=indent)  # empty column
            tbl.add_column(min_width=min_args_width)  # commands
            tbl.add_column()  # description

            tbl.add_row("", *_help_from_token(sub_command.help(), short=True))
            console.print(tbl)


def call_stack_from_tokens(
    token: Command | Subcommand,
) -> Iterator[Command | Subcommand]:
    """Return the sequence of subcommands the user provided to reach this specific subcommand."""
    yield token
    if token.parent is None:
        return
    yield from call_stack_from_tokens(token.parent)
