from __future__ import annotations

from inspect import cleandoc
from typing import TYPE_CHECKING, Iterator

from rich.console import Console
from rich.table import Table
from rich.text import Text

from clipstick._exceptions import ClipStickError
from clipstick._style import ARGUMENT_HEADER, ARGUMENTS_STYLE, DOCSTRING, ERROR

console = Console()
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
            tbl.add_column()
            tbl.add_row("", arg.help_arguments, arg.help_text, arg.help_type)
            console.print(tbl)
    if options:
        tbl = Table.grid(collapse_padding=True, padding=(0, 1))
        tbl.add_column(width=indent)  # empty column
        tbl.add_column(min_width=min_args_width)  # keys
        tbl.add_column()  # description
        tbl.add_column()  # type
        tbl.add_column()  # default

        console.print("")
        console.print("Options:", style=ARGUMENT_HEADER)
        for kwarg in options:
            tbl.add_row(
                "",
                kwarg.help_arguments,
                kwarg.help_text,
                kwarg.help_type,
                kwarg.help_default,
            )
        console.print(tbl)
    if command.sub_commands:
        tbl = Table.grid(collapse_padding=True, padding=(0, 1))
        tbl.add_column(width=indent)  # empty column
        tbl.add_column(min_width=min_args_width)  # commands
        tbl.add_column()  # description

        console.print("")
        console.print("Subcommands:", style=ARGUMENT_HEADER)

        for sub_command in command.sub_commands:
            tbl.add_row("", sub_command.help_arguments, sub_command.cls.__doc__)
        console.print(tbl)


def call_stack_from_tokens(
    token: Command | Subcommand,
) -> Iterator[Command | Subcommand]:
    """Return the sequence of subcommands the user provided to reach this specific subcommand."""
    yield token
    if token.parent is None:
        return
    yield from call_stack_from_tokens(token.parent)
