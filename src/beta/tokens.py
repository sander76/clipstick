from dataclasses import dataclass, field

from types import UnionType
from typing import Any, ForwardRef, Protocol, TypeAlias, Union, get_args
from pydantic.fields import FieldInfo

from pydantic import BaseModel


@dataclass
class Token:
    key: str

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        """Consume a list of values and return the new index for
        a next token to start consuming."""
        raise NotImplementedError()

    def parse(self, values: list[str]) -> dict[str, str]:
        raise NotImplementedError()


@dataclass
class PositionalArg(Token):
    key: str
    indices: slice | None = None

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        if values[idx].startswith("--"):
            # Not a positional. No match.
            return False, idx
        # would fit as a positional
        self.indices = slice(idx, idx + 1)
        return True, idx + 1

    def parse(self, values: list[str]) -> dict[str, str]:
        return {self.key: values[self.indices][0]}


@dataclass
class OptionalArg(Token):
    key: str
    indices: slice | None = None

    def match(self, idx: int, values: list[str]) -> tuple[bool, int]:
        if not values[idx] == f"--{self.key}":
            # As this is an optional, we are returning true to continue matching.
            return True, idx
        # consume next two values
        self.indices = slice(idx, idx + 2)
        return True, idx + 2

    def parse(self, values: list[str]) -> dict[str, str]:
        return {self.key: values[self.indices][-1]}


@dataclass
class Subcommand(Token):
    key: str
    sub_command_name: str
    cls: type[BaseModel]
    indices: slice | None = None

    args: list[Token] = field(default_factory=list)
    sub_commands: list["Subcommand"] = field(default_factory=list)

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
        print(self.cls.__fields__.__doc__)
        print("")
        for arg in self.args:
            arg.help()
        for sub_command in self.sub_commands:
            print(sub_command.__doc__)

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
        if not values[idx] == self.sub_command_name:
            return False, start_idx

        self.indices = slice(idx, idx + 1)

        idx += 1
        for arg in self.args:
            success, idx = arg.match(idx, values)
            if not success:
                return False, start_idx

        if len(self.sub_commands) == 0:
            return True, idx

        single_sub_command: Subcommand | None = None
        for sub_command in self.sub_commands:
            success, idx = sub_command.match(idx, values)
            if success:
                if single_sub_command is not None:
                    raise ValueError(
                        "two token-trees found which resolve to a solution. Don't know what to do"
                    )
                single_sub_command = sub_command
        if not success:
            return False, start_idx
        self.sub_commands = [single_sub_command]
        return True, idx

    def parse(self, arguments: list[str]) -> dict[str, BaseModel]:
        """Populate all tokens with the provided arguments."""
        args: dict[str, str] = {}
        [args.update(parsed.parse(arguments)) for parsed in self.args]
        sub_commands: dict[str, BaseModel] = {}
        assert len(self.sub_commands) <= 1
        [sub_commands.update(parsed.parse(arguments)) for parsed in self.sub_commands]

        model = self.cls(**args, **sub_commands)

        return {self.key: model}


def _is_subcommand(attribute: str, field_info: FieldInfo) -> bool:
    if not isinstance(field_info.annotation, UnionType):
        return False
    args = get_args(field_info.annotation)
    if not all(issubclass(arg, BaseModel) for arg in args):
        return False
    if not field_info.is_required():
        raise ValueError("Should be required values.")
    return True


def tokenize(model: type[BaseModel], sub_command: Subcommand) -> None:
    for key, value in model.model_fields.items():
        if _is_subcommand(key, value):
            for annotated_model in get_args(value.annotation):
                new_sub_command = Subcommand(
                    key, annotated_model.__name__, cls=annotated_model
                )

                sub_command.sub_commands.append(new_sub_command)
                tokenize(annotated_model, new_sub_command)

        elif value.is_required():
            # becomes a positional
            sub_command.args.append(PositionalArg(key))
        else:
            sub_command.args.append(OptionalArg(key))


def parse(model: type[BaseModel], args: list[str]) -> BaseModel:
    args = ["__main_entry__"] + args
    root_node = Subcommand("__main_entry__", "__main_entry__", model)
    tokenize(model=model, sub_command=root_node)

    root_node.match(0, args)
    parsed = root_node.parse(args)
    return parsed["__main_entry__"]
