from __future__ import annotations

import sys
from copy import copy
from functools import cached_property
from itertools import chain
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError
from pydantic.alias_generators import to_snake
from pydantic.fields import FieldInfo

from clipstick import _exceptions, _help
from clipstick._annotations import Short

TPydanticModel = TypeVar("TPydanticModel", bound=BaseModel)


def _to_false_key(field: str) -> str:
    return f"--no-{field.replace('_','-')}"


def _to_key(field: str) -> str:
    return f"--{field.replace('_','-')}"


def _to_short(field: str) -> str:
    return f"-{field}"


def _to_false_short(field: str) -> str:
    return f"-no-{field}"


class PositionalArg:
    """Positional/required argument token.

    A token is generated based on the pydantic field definition and used
    for matching and parsing a provided list of arguments.
    """

    def __init__(self, field: str, field_info: FieldInfo):
        """Init.

        Args:
            field: field name as defined in the class (a class attribute)
            field_info: Pydantic fieldinfo
        """
        self.field = field
        self.field_info = field_info
        self.used_arg: str | None = None
        self._match: dict[str, str] | None = None

    @cached_property
    def user_keys(self) -> list[str]:
        """Argument keys (like --verbose or --value) provided by a user to indicate a keyword or flag.

        Many times this is a list of normalized pydantic fields or provided shorthand names.
        """
        return [(self.field.replace("_", "-"))]

    def match(self, idx: int, arguments: list[str]) -> tuple[bool, int]:
        """Check if this token is a match given the list of arguments."""
        if len(arguments) <= idx:
            # we need this positional argument to match.
            # if not, it indicates the user has not provided it.
            raise _exceptions.MissingPositional(
                "/".join(self.user_keys), idx, arguments
            )
        if arguments[idx].startswith("-"):
            return False, idx
        self.used_arg = arguments[idx]
        self._match = {self.field: arguments[idx]}
        return True, idx + 1

    def parse(self) -> dict[str, str]:
        """Return the token data in a parseable way.

        This mean returning a (partial) dict with a key, value pair
        which is to be consumed by pydantic.
        """
        return self._match if self._match else {}


class OptionalKeyArgs:
    """Optional/keyworded argument token.

    A token is generated based on the pydantic field definition and used
    for matching and parsing a provided list of arguments.
    """

    def __init__(self, field: str, field_info: FieldInfo):
        """Init.

        Args:
            field: field name as defined in the class (a class attribute)
            field_info: Pydantic fieldinfo
        """
        self.field = field
        self.field_info = field_info
        self.used_arg: str | None = None
        self._match: dict[str, str] = {}

    @cached_property
    def short_keys(self) -> list[str]:
        return [
            _to_short(short.short)
            for short in self.field_info.metadata
            if isinstance(short, Short)
        ]

    @cached_property
    def keys(self) -> list[str]:
        return [_to_key(self.field)]

    @cached_property
    def user_keys(self) -> list[str]:
        """Argument keys (like --verbose or --value) provided by a user to indicate a keyword or flag.

        Many times this is a list of normalized pydantic fields or provided shorthand names.
        """
        return self.keys + self.short_keys

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        try:
            if values[idx] not in self.user_keys:
                return False, idx
        except IndexError:
            # As this is an optional, we are returning true to continue matching.
            return False, idx
        self.used_arg = values[idx]
        self._match[self.field] = values[idx + 1]

        return True, idx + 2

    def parse(self) -> dict[str, str]:
        """Return the token data in a parseable way.

        This mean returning a (partial) dict with a key, value pair
        which is to be consumed by pydantic.
        """
        return self._match


class BooleanFlag:
    """A positional (required) boolean flag value."""

    def __init__(self, field: str, field_info: FieldInfo):
        """Init.

        Args:
            field: field name as defined in the class (a class attribute)
            field_info: Pydantic fieldinfo
        """
        self.field = field
        self.field_info = field_info
        self.used_arg: str | None = None
        self._match: dict[str, bool] = {}

    @cached_property
    def _short_true_keys(self) -> list[str]:
        """Return a list of 'shorts' to a list of short hand arguments.

        Example:
            ['a','b'] --> ['-a','-b']
        """
        return [_to_short(short.short) for short in self.field_info.metadata]

    @cached_property
    def _short_false_keys(self) -> list[str]:
        """Return a list of 'shorts' to a list of negated short hand arguments.

        Example:
            ['a','b'] --> ['--no-a','no-b']
        """
        return [_to_false_short(short.short) for short in self.field_info.metadata]

    @cached_property
    def _true_keys(self) -> list[str]:
        """Return a list of argument keys."""
        return [_to_key(self.field)]

    @cached_property
    def _false_keys(self) -> list[str]:
        """Return a list of negated argument keys."""
        return [_to_false_key(self.field)]

    @cached_property
    def short_keys(self) -> list[str]:
        return self._short_false_keys + self._short_true_keys

    @cached_property
    def keys(self) -> list[str]:
        return self._true_keys + self._false_keys

    @cached_property
    def user_keys(self) -> list[str]:
        """Argument keys (like --verbose or --value) provided by a user to indicate a keyword or flag.

        Many times this is a list of normalized pydantic fields or provided shorthand names.
        """
        return self.short_keys + self.keys

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        if len(values) <= idx:
            return False, idx

        if values[idx] in self.user_keys:
            self.used_arg = values[idx]
            self._match[self.field] = (
                values[idx] in self._true_keys + self._short_true_keys
            )
            return True, idx + 1
        return False, idx

    def parse(self) -> dict[str, bool]:
        """Return the token data in a parseable way.

        This mean returning a (partial) dict with a key, value pair
        which is to be consumed by pydantic.
        """
        return self._match


class OptionalBooleanFlag(BooleanFlag):
    @cached_property
    def short_keys(self) -> list[str]:
        if self.field_info.default is False:
            return self._short_true_keys
        return self._short_false_keys

    @cached_property
    def keys(self) -> list[str]:
        if self.field_info.default is False:
            return self._true_keys
        return self._false_keys

    @cached_property
    def user_keys(self) -> list[str]:
        """Argument keys (like --verbose or --value) provided by a user to indicate a keyword or flag.

        Many times this is a list of normalized pydantic fields or provided shorthand names.
        """
        if self.field_info.default is False:
            return self._true_keys + self._short_true_keys
        else:
            return self._false_keys + self._short_false_keys


class Command(Generic[TPydanticModel]):
    """The main/base class of your CLI.

    There will be only one of this in your CLI.
    """

    def __init__(
        self,
        field: str,
        cls: type[TPydanticModel],
        parent: "Command" | "Subcommand" | None,
    ):
        self.field = field
        self.cls = cls
        self.parent = parent
        # self._indices: slice | None = None
        self._match: dict[str, str | bool] = {}

        self.args: list[PositionalArg | BooleanFlag] = []
        """Collection of required arguments associated with this command."""

        self.optional_kwargs: list[OptionalKeyArgs | OptionalBooleanFlag] = []
        """Collection of optional keyword arguments associated with this command."""

        self.sub_commands: list["Subcommand"] = []

    @cached_property
    def user_keys(self) -> list[str]:
        """Return the name of the main command that started this cli tool.

        This name is most of times a full path to the python entrypoint.
        We are only interested in the last item of this call.
        """
        keys = (self.field.split("/")[-1]).split("\\")[-1]
        return [keys]

    def match(self, idx: int, arguments: list[str]) -> tuple[bool, int]:
        """Check for token match.

        As a result the subcommand has been stripped down to a one-branch tree, meaning
        all sub_commands collections in all (nested)
        subcommands have only one or no children.


        Args:
            idx: arguments index to start the matching from.
            arguments: the list of provided arguments that need parsing

        Returns:
            tuple of bool and int.
                bool indicates whether to continue matching
                int indicates the new starting point for the next token to match.
        """
        start_idx = idx

        if _is_help_key(idx, arguments):
            _help.help(self)
            sys.exit(0)

        args = copy(self.args)

        def _check_arg_or_optional(_idx: int, values: list[str]) -> tuple[bool, int]:
            """Every arg in the values list must match one of the tokens in the model.

            They need to match either:
            - A positional argument in the correct order of the args list.
            - One of the optional arguments.
            """
            if args:
                arg = args[0]
                success, _idx = arg.match(_idx, values)
                if success:
                    args.pop(0)
                    return success, _idx
            for optional in self.optional_kwargs:
                success, _idx = optional.match(_idx, values)
                if success:
                    return success, _idx
            return False, _idx

        found_match = True
        while found_match:
            found_match, idx = _check_arg_or_optional(idx, arguments)

        # no more match is found. Now we need to check whether all postional (required) arguments
        # have been matched. If not, we have no match for this command.
        if args:
            return False, start_idx

        # We now need to check whether this command has any subcommands.
        # If no subcommands are inside this command we have a match.
        if len(self.sub_commands) == 0:
            return True, idx

        # This command has a subcommand.
        # We now try and match each subcommand with the remainder of the provided arguments.

        # We are going to parse all available subcommands. Only one can exist
        subcommand: Subcommand | None = None
        for sub_command in self.sub_commands:
            success, idx = sub_command.match(idx, arguments)
            if success:
                if subcommand:
                    raise ValueError(
                        "more than one solution-tree is found. Don't know what to do now."
                    )
                subcommand = sub_command

        if not subcommand:
            return False, start_idx

        self.sub_commands = [subcommand]

        return True, idx

    def parse(self) -> TPydanticModel:
        """Populate all tokens with the provided arguments."""
        [
            self._match.update(parsed.parse())
            for parsed in chain(self.args, self.optional_kwargs)
        ]

        if self.sub_commands:
            subcommand = self.sub_commands[0]
            self._match[subcommand.field] = subcommand.parse()
        try:
            return self.cls.model_validate(self._match)
        except ValidationError as err:
            raise _exceptions.FieldError(err, token=self)


class Subcommand(Command):
    @cached_property
    def user_keys(self) -> list[str]:
        snaked = to_snake(self.cls.__name__)
        return [snaked.replace("_", "-")]

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        """Check for token match.

        As a result the subcommand has been stripped down to a one-branch tree, meaning
        all sub_commands collections in all (nested)
        subcommands have only one or no children.


        Args:
            idx: values index to start the matching from.
            values: the list of provided arguments that need parsing

        Returns:
            tuple of bool and int.
                bool indicates whether to continue matching
                int indicates the new starting point for the next token to match.
        """
        try:
            if values[idx] not in self.user_keys:
                return False, idx
        except IndexError:
            return False, idx

        return super().match(idx + 1, values)


def _is_help_key(idx, values: list[str]) -> bool:
    try:
        if values[idx] == "-h":
            return True
    except IndexError:
        return False
    return False
