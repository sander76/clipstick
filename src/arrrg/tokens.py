from dataclasses import dataclass, field

from types import UnionType
from typing import Any, ForwardRef, Protocol, TypeAlias, Union, get_args
from pydantic.fields import FieldInfo

from pydantic import BaseModel


@dataclass
class Token:
    key: str

    def match(self, idx: int, values: list[str]) -> int:
        """Consume a list of values and return the new index for
        a next token to start consuming."""
        raise NotImplementedError()

    def parse(self, values: list[str]) -> dict[str, str]:
        raise NotImplementedError()


@dataclass
class Node:
    props: list[Token] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)


@dataclass
class PositionalArg(Token):
    key: str
    indices: slice | None = None

    def match(self, idx: int, values: list[str]) -> int:
        if values[idx].startswith("--"):
            # Not a positional. No match.
            return idx
        # would fit as a positional
        self.indices = slice(idx, idx + 1)
        return idx + 1

    def parse(self, values: list[str]) -> dict[str, str]:
        return {self.key: values[self.indices]}


@dataclass
class Subcommand(Token):
    key: str
    sub_command_name: str
    cls: type[BaseModel]
    indices: slice | None = None

    def match(self, idx: int, values: list[str]) -> int:
        if values[idx] == self.sub_command_name:
            self.indices = slice(idx, idx + 1)
            return idx + 1
        return idx

    def parse(self, values: list[str]) -> dict[str, str]:
        return {self.key: self.cls}


def _is_subcommand(attribute: str, field_info: FieldInfo) -> bool:
    if not isinstance(field_info.annotation, UnionType):
        return False
    args = get_args(field_info.annotation)
    if not all(issubclass(arg, BaseModel) for arg in args):
        return False
    if not field_info.is_required():
        raise ValueError("Should be required values.")
    return True


def tokenize(model: BaseModel, node: Node):
    for key, value in model.model_fields.items():
        if _is_subcommand(key, value):
            for annotated_model in get_args(value.annotation):
                sub_node = Node(
                    props=[
                        Subcommand(
                            key,
                            sub_command_name=annotated_model.__name__,
                            cls=annotated_model,
                        )
                    ]
                )
                node.children.append(sub_node)
                tokenize(annotated_model, sub_node)
        elif isinstance(value.annotation, UnionType):
            pass
        elif value.is_required():
            # becomes a positional
            node.props.append(PositionalArg(key))


def get_all_paths(node: Node):
    if len(node.children) == 0:
        return [node.props]

    return [
        node.props + path for child in node.children for path in get_all_paths(child)
    ]


def match(args: list[str], token_lists: list[list[Token]]):
    matches = []
    arg_count = len(args)
    for token_list in token_lists:
        idx = 0
        for token in token_list:
            new_idx = token.match(idx, args)
            if new_idx == idx:
                # no match. stop attempt and proceed to the next one.
                break
            idx = new_idx
        if idx == arg_count:
            matches.append(token_list)
    return matches


def populate(args: list[str], token_list: list[Token]):
    dct = {}
    for token in token_list:
        parsed = token.parse(args)

        if isinstance(token, Subcommand):
            new_dct = {}


# def all_paths(token: tk, previous: tk):
#     if isinstance(token, list):
#         return [previous + [all_paths(tk, previous)] for tk in token]

#     return previous


def parse(model: BaseModel, args: list[str]):
    root_node = Node()
    tokenize(model=model, node=root_node)

    pths = get_all_paths(root_node)
    matches = match(args, pths)
    print(matches)
    print(pths)
    # traverse(0, args, tokens, [])


# nd = Node(
#     props=[PositionalArg],
#     children=[
#         Node(props=[Subcommand, PositionalArg, PositionalArg]),
#         Node(props=[Subcommand, PositionalArg]),
#     ],
# )
