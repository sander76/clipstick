from dataclasses import dataclass
from types import UnionType
from typing import Any, Protocol, get_args
from pydantic.fields import FieldInfo

from pydantic import BaseModel


class Token(Protocol):
    key: str

    def match(self, values: list[str]) -> bool:
        ...


tokens: dict[Token, list[Token]] = {}


@dataclass(frozen=True)
class PositionalArg:
    key: str

    def match(self, values: list[str]) -> bool:
        if values[0].startswith("--"):
            return False
        return


@dataclass(frozen=True)
class Subcommand:
    key: str

    def match(self, values: list[str]) -> bool:
        return True


def _is_subcommand(attribute: str, field_info: FieldInfo) -> bool:
    if not isinstance(field_info.annotation, UnionType):
        return False
    args = get_args(field_info.annotation)
    if not all(issubclass(arg, BaseModel) for arg in args):
        return False
    if not field_info.is_required():
        raise ValueError("Should be required values.")
    return True


def tokenize(model: BaseModel, token_list: list[Token]) -> None:
    for key, value in model.model_fields.items():
        if _is_subcommand(key, value):
            for model in get_args(value.annotation):
                arg = Subcommand(key)
                token_list.append(arg)

                new_token_list = []
                tokens[arg] = new_token_list
                tokenize(model, new_token_list)
        elif isinstance(value.annotation, UnionType):
            pass
        elif value.is_required():
            # becomes a positional
            arg = PositionalArg(key)
            token_list.append(arg)


def traverse(
    args: list[str], available_tokens: dict[Token, list[Token]], token_list: list[Token]
):
    for token in available_tokens.values():
        pass


# Driver Code
print("Following is the Depth-First Search")


def parse(args: list[str]):
    dfs(visited, tokens, "main")
    for token in tokens:
        token.match(args)


val = {
    "main": [
        PositionalArg,
        [
            [
                Subcommand,
                PositionalArg,
                PositionalArg,
            ],
            [
                Subcommand,
                PositionalArg,
                [
                    [Subcommand, PositionalArg],
                    [Subcommand, PositionalArg],
                ],
            ],
        ],
    ]
}
