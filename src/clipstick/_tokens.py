from __future__ import annotations

import sys
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError
from pydantic.alias_generators import to_snake
from pydantic.fields import FieldInfo

from clipstick import _exceptions, _help
from clipstick._annotations import Short

TTokenType = TypeVar("TTokenType")
TPydanticModel = TypeVar("TPydanticModel", bound=BaseModel)


def _to_false_key(key: str) -> str:
    return f"--no-{key.replace('_','-')}"


def _to_key(key: str) -> str:
    return f"--{key.replace('_','-')}"


def _to_short(key: str) -> str:
    return f"-{key}"


def _to_false_short(key: str) -> str:
    return f"-no-{key}"


@dataclass
class Token(Generic[TTokenType]):
    """Represents either a pydantic model or a pydantic field.

    A token is used to interpret provided arguments (check if there is a match) and
    if so, consume a part of provided arguments (during parsing.)
    """

    key: str

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        """Try to match a (range of) value(s) starting from an index.

        Matching logic is implemented depending on argument type (like positional, optional etc.)

        If a match is found it will be added to the list of tokens which are used for final parsing.
        The token stores the indices of the provided argument list to later parse the arguments.

        Returns:
            A boolean indicating the match was a success.
                For a positional (required) argument this means an explicit match.
                For an optional both an exact match will return True, but also no match will return True.
                The latter is a signal for the match to continue.
            A new index indicating the starting point for the next token match.
        """
        raise NotImplementedError()

    def parse(self, values: list[str]) -> dict[str, TTokenType]:
        """Parse data from the provided values based on the match logic implemented in this class."""
        raise NotImplementedError()

    @property
    def user_keys(self) -> list[str]:
        """Argument keys (like --verbose or --value) provided by a user to indicate a keyword or flag.

        Many times this is a list of normalized pydantic fields or provided shorthand names.
        """
        raise NotImplementedError()


@dataclass
class PositionalArg(Token[str]):
    key: str
    field_info: FieldInfo
    indices: slice | None = None

    @cached_property
    def keys(self) -> list[str]:
        return [(self.key.replace("_", "-"))]

    @property
    def user_keys(self) -> list[str]:
        return self.keys

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        if len(values) <= idx:
            # we need this positional argument to match.
            # if not, it indicates the user has not provided it.
            raise _exceptions.MissingPositional("/".join(self.user_keys), idx, values)
        self.indices = slice(idx, idx + 1)
        return True, idx + 1

    def parse(self, values: list[str]) -> dict[str, str]:
        if self.indices:
            return {self.key: values[self.indices][0]}
        raise ValueError("Expecting a slice object. Got None.")


@dataclass
class OptionalKeyArgs(Token[str]):
    key: str
    field_info: FieldInfo
    indices: slice | None = None

    @cached_property
    def short_keys(self) -> list[str]:
        return [
            _to_short(short.short)
            for short in self.field_info.metadata
            if isinstance(short, Short)
        ]

    @cached_property
    def keys(self) -> list[str]:
        return [_to_key(self.key)]

    @cached_property
    def user_keys(self) -> list[str]:
        return self.keys + self.short_keys

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        try:
            if values[idx] not in self.user_keys:
                # As this is an optional, we are returning true to continue matching.
                return True, idx
        except IndexError:
            # As this is an optional, we are returning true to continue matching.
            return True, idx

        # consume next two values
        self.indices = slice(idx, idx + 2)
        return True, idx + 2

    def parse(self, values: list[str]) -> dict[str, str]:
        if self.indices:
            return {self.key: values[self.indices][-1]}
        return {}


@dataclass
class BooleanFlag(Token[bool]):
    """A positional (required) boolean flag value."""

    key: str
    """A pydantic field key/name"""
    field_info: FieldInfo
    indices: slice | None = None

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
        return [_to_key(self.key)]

    @cached_property
    def _false_keys(self) -> list[str]:
        """Return a list of negated argument keys."""
        return [_to_false_key(self.key)]

    @cached_property
    def short_keys(self) -> list[str]:
        return self._short_false_keys + self._short_true_keys

    @cached_property
    def keys(self) -> list[str]:
        return self._true_keys + self._false_keys

    @property
    def user_keys(self) -> list[str]:
        return self.short_keys + self.keys

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        if len(values) <= idx:
            return False, idx

        if values[idx] in self.user_keys:
            self.indices = slice(idx, idx + 1)
            return True, idx + 1
        return False, idx

    def parse(self, values: list[str]) -> dict[str, bool]:
        if self.indices:
            val = values[self.indices][0] in self._true_keys + self._short_true_keys
            return {self.key: val}
        return {}


@dataclass
class OptionalBooleanFlag(BooleanFlag):
    key: str
    field_info: FieldInfo
    indices: slice | None = None

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
        if self.field_info.default is False:
            return self._true_keys + self._short_true_keys
        else:
            return self._false_keys + self._short_false_keys

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        if len(values) <= idx:
            return True, idx

        if values[idx] in self.user_keys:
            self.indices = slice(idx, idx + 1)
            return True, idx + 1
        return True, idx


@dataclass
class Command(Token[TPydanticModel]):
    """The main/base class of your CLI.

    There will be only one of this in your CLI.
    """

    key: str
    """Reference to the key in the pydantic model."""

    cls: type[TPydanticModel]
    """Pydantic class. Used for instantiating this command."""

    parent: "Command" | "Subcommand" | None
    """The full command that got you here."""

    indices: slice | None = None
    """The indices which are consumed of the provided arguments."""

    args: list[PositionalArg | BooleanFlag] = field(default_factory=list)
    """Collection of required arguments associated with this command."""

    optional_kwargs: list[OptionalKeyArgs | OptionalBooleanFlag] = field(
        default_factory=list
    )
    """Collection of optional keyword arguments associated with this command."""

    sub_commands: list["Subcommand"] = field(default_factory=list)

    @property
    def user_keys(self) -> list[str]:
        """Return the name of the main command that started this cli tool.

        This name is most of times a full path to the python entrypoint.
        We are only interested in the last item of this call."""
        keys = (self.key.split("/")[-1]).split("\\")[-1]
        return [keys]

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
        start_idx = idx

        if _is_help_key(idx, values):
            _help.help(self)
            sys.exit(0)
        for arg in chain(self.args, self.optional_kwargs):
            success, idx = arg.match(idx, values)
            if not success:
                return False, start_idx

        if len(self.sub_commands) == 0:
            return True, idx

        subcommands: list[tuple[bool, int, Subcommand]] = []
        for sub_command in self.sub_commands:
            sub_command_start_idx = idx
            result = sub_command.match(sub_command_start_idx, values)
            subcommands.append((*result, sub_command))

        succesfull_subcommands = [
            sub_command_structure
            for sub_command_structure in subcommands
            if sub_command_structure[0] is True
        ]

        if len(succesfull_subcommands) > 1:
            raise ValueError(
                "more than one solution-tree is found. Don't know what to do now."
            )
        if len(succesfull_subcommands) == 0:
            return False, start_idx
        _, new_idx, sub_commands = succesfull_subcommands[0]
        self.sub_commands = [sub_commands]

        return True, new_idx

    def parse(self, arguments: list[str]) -> dict[str, TPydanticModel]:
        """Populate all tokens with the provided arguments."""
        args: dict[str, str | bool] = {}
        [
            args.update(parsed.parse(arguments))
            for parsed in chain(self.args, self.optional_kwargs)
        ]
        sub_commands: dict[str, BaseModel] = {}
        assert len(self.sub_commands) <= 1
        [sub_commands.update(parsed.parse(arguments)) for parsed in self.sub_commands]

        try:
            model = self.cls(**args, **sub_commands)
        except ValidationError as err:
            raise _exceptions.FieldError(err, token=self, provided_args=arguments)

        return {self.key: model}


@dataclass
class Subcommand(Command):
    @property
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
        start_idx = idx
        try:
            if values[idx] not in self.user_keys:
                return False, start_idx
        except IndexError:
            return False, start_idx

        self.indices = slice(idx, idx + 1)

        idx += 1

        return super().match(idx, values)


def _is_help_key(idx, values: list[str]) -> bool:
    try:
        if values[idx] == "-h":
            return True
    except IndexError:
        return False
    return False
