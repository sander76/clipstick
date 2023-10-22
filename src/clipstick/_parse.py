from inspect import isclass
from itertools import chain
from pydantic.fields import FieldInfo
from types import UnionType
from clipstick._docstring import set_undefined_field_descriptions_from_var_docstrings
from clipstick._annotations import Short
from clipstick._tokens import (
    OptionalKeyArgs,
    PositionalArg,
    Subcommand,
    Command,
    BooleanFlag,
    OptionalBooleanFlag,
)
from clipstick._exceptions import (
    TooManyShortsException,
    InvalidTypesInUnion,
    NoDefaultAllowedForSubcommand,
    TooManySubcommands,
)

from pydantic import BaseModel


from typing import Iterator, get_args


def _is_subcommand(attribute: str, field_info: FieldInfo) -> bool:
    """Check if the field annotated as a subcommand."""
    if not isinstance(field_info.annotation, UnionType):
        return False
    args = get_args(field_info.annotation)
    if not all(issubclass(arg, BaseModel) for arg in args):
        raise InvalidTypesInUnion()
    if not field_info.is_required():
        raise NoDefaultAllowedForSubcommand()
    return True


def _is_boolean_type(field_info: FieldInfo) -> bool:
    anno = field_info.annotation
    if anno is bool:
        return True
    return False


def tokenize(model: type[BaseModel], sub_command: Subcommand | Command) -> None:
    # todo: move this somewhere else.
    set_undefined_field_descriptions_from_var_docstrings(model)
    _sub_command_found: bool = False
    for key, value in model.model_fields.items():
        if _is_subcommand(key, value):
            if _sub_command_found:
                raise TooManySubcommands()
            _sub_command_found = True
            # each result of the get_args call is a type[BaseModel]
            # which is processed as a subcommand.
            for annotated_model in get_args(value.annotation):
                new_sub_command = Subcommand(
                    key=key, cls=annotated_model, parent=sub_command
                )

                sub_command.sub_commands.append(new_sub_command)
                tokenize(annotated_model, new_sub_command)
        elif _is_boolean_type(value):
            if value.is_required():
                sub_command.args.append(BooleanFlag(key, field_info=value))
            else:
                sub_command.optional_kwargs.append(
                    OptionalBooleanFlag(key, field_info=value)
                )
        elif value.is_required():
            # becomes a positional
            sub_command.args.append(PositionalArg(key, field_info=value))
        else:
            sub_command.optional_kwargs.append(OptionalKeyArgs(key, field_info=value))


def validate_model(model: type[BaseModel]) -> None:
    """Before anything we validate the input model to see it is
    useful for cli generation.
    """
    # todo: validate only one subcommand.

    # todo: validate no model as field value.

    # check shorthands per model to be unique.
    _validate_shorts(model)


def _validate_shorts(model: type[BaseModel]) -> None:
    """Iterate over the complete cli model and validate each model of short-hand uniqueness.

    Returns:
        None if all ok

    Raises:
        ValueError when validation has failed.
    """
    for model in iter_over_model(model):
        _validate_shorts_in_model(model)


def _validate_shorts_in_model(model: type[BaseModel]):
    shorts = [
        short.short
        for short in chain(*(field.metadata for field in model.model_fields.values()))
        if isinstance(short, Short)
    ]

    unique_shorts = set(shorts)

    if len(shorts) == len(unique_shorts):
        return
    raise TooManyShortsException(model, shorts)


def iter_over_model(model: type[BaseModel]) -> Iterator[type[BaseModel]]:
    """Return all BaseModels within a provided BaseModel."""
    yield model

    for item in model.model_fields.values():
        if isclass(item.annotation) and issubclass(item.annotation, BaseModel):
            yield from iter_over_model(item.annotation)
        else:
            args = get_args(item.annotation)
            for arg in args:
                if isclass(arg) and issubclass(arg, BaseModel):
                    yield from iter_over_model(arg)
