from dataclasses import dataclass, field
import sys

from typing import Generic, TypeVar
from itertools import chain
from pydantic import BaseModel
from pydantic.alias_generators import to_snake

TTokenType = TypeVar("TTokenType")
TPydanticModel = TypeVar("TPydanticModel", bound=BaseModel)


@dataclass
class Token(Generic[TTokenType]):
    key: str

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        """Consume a list of values and return the new index for
        a next token to start consuming."""
        raise NotImplementedError()

    def parse(self, values: list[str]) -> dict[str, TTokenType]:
        raise NotImplementedError()

    @property
    def user_key(self) -> str:
        raise NotImplementedError()


@dataclass
class PositionalArg(Token[str]):
    key: str
    indices: slice | None = None

    @property
    def user_key(self) -> str:
        return self.key.replace("_", "-")

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        try:
            if values[idx].startswith("-"):
                # Not a positional. No match.
                return False, idx
        except IndexError:
            return False, idx
        # would fit as a positional
        self.indices = slice(idx, idx + 1)
        return True, idx + 1

    def parse(self, values: list[str]) -> dict[str, str]:
        if self.indices:
            return {self.key: values[self.indices][0]}
        raise ValueError("Expecting a slice object. Got None.")


@dataclass
class OptionalKeyArgs(Token[str]):
    key: str
    indices: slice | None = None

    @property
    def user_key(self) -> str:
        return f"--{self.key.replace('_','-')}"

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        try:
            if not values[idx] == self.user_key:
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
class Subcommand(Token[TPydanticModel]):
    key: str
    """Reference to the key in the pydantic model."""

    sub_command_name: str

    cls: type[TPydanticModel]
    """Pydantic class. Used for instantiating this command."""
    indices: slice | None = None
    """The indices which are consumed of the provided arguments."""

    args: list[Token] = field(default_factory=list)
    optional_kwargs: list[Token] = field(default_factory=list)

    sub_commands: list["Subcommand"] = field(default_factory=list)

    @property
    def user_key(self) -> str:
        snaked = to_snake(self.cls.__name__)
        return snaked.replace("_", "-")

    def tokens(self) -> list[list["Subcommand"]]:
        base = [self]

        if self.sub_commands:
            args = []
            for sub in self.sub_commands:
                for token in sub.tokens():
                    new_ = base + token
                    args.append(new_)
            return args
        return [base]

    def help(self):
        print("")
        _args_string = ", ".join(_arg.user_key for _arg in self.args)
        _kwargs_string = ", ".join(
            f"[{_kwarg.user_key}]" for _kwarg in self.optional_kwargs
        )
        _subcommands = ""
        if self.sub_commands:
            _subcommands = (
                "{" + ", ".join(sub.cls.__name__ for sub in self.sub_commands) + "}"
            )
        _all = " ".join(
            (arg for arg in (_args_string, _kwargs_string, _subcommands) if arg)
        )
        print(f"usage: <your entrypoint here> [-h] {_all}")
        print("")
        print(self.cls.__doc__)
        if self.args:
            print("")
            print("positional arguments:")
            for arg in self.args:
                field_info = self.cls.model_fields[arg.key]
                print(f"    {arg.user_key:<25}{field_info.description}")
        if self.optional_kwargs:
            print("")
            print("optional keyword arguments:")
            for kwarg in self.optional_kwargs:
                field_info = self.cls.model_fields[kwarg.key]
                print(f"    {kwarg.user_key:<25}{field_info.description}")
        if self.sub_commands:
            print("")
            print("subcommands:")
            for sub_command in self.sub_commands:
                print(f"    {sub_command.cls.__name__:<25}{sub_command.cls.__doc__}")

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
            if not values[idx] == self.cls.__name__:  # self.sub_command_name:
                return False, start_idx
        except IndexError:
            return False, start_idx

        self.indices = slice(idx, idx + 1)

        idx += 1

        if _is_help_key(idx, values):
            self.help()
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

        self.sub_commands = [succesfull_subcommands[0][2]]
        return True, idx + succesfull_subcommands[0][1]

    def parse(self, arguments: list[str]) -> dict[str, TPydanticModel]:
        """Populate all tokens with the provided arguments."""
        args: dict[str, str] = {}
        [
            args.update(parsed.parse(arguments))
            for parsed in chain(self.args, self.optional_kwargs)
        ]
        sub_commands: dict[str, BaseModel] = {}
        assert len(self.sub_commands) <= 1
        [sub_commands.update(parsed.parse(arguments)) for parsed in self.sub_commands]

        model = self.cls(**args, **sub_commands)

        return {self.key: model}


def _is_help_key(idx, values: list[str]) -> bool:
    try:
        if values[idx] == "-h":
            return True
    except IndexError:
        return False
    return False
