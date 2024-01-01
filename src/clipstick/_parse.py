from itertools import chain
from types import UnionType
from typing import Iterator, Literal, get_args

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from clipstick._annotations import Short
from clipstick._docstring import set_undefined_field_descriptions_from_var_docstrings
from clipstick._exceptions import (
    InvalidTypesInUnion,
    NoDefaultAllowedForSubcommand,
    TooManyShortsException,
    TooManySubcommands,
)
from clipstick._tokens import (
    Boolean,
    Choice,
    Collection,
    Command,
    Optional,
    OptionalBoolean,
    OptionalChoice,
    OptionalCollection,
    Positional,
    Subcommand,
)


def _is_subcommand(attribute: str, field_info: FieldInfo) -> bool:
    """Check if the field annotated as a subcommand."""
    if not isinstance(field_info.annotation, UnionType):
        return False

    args = get_args(field_info.annotation)

    if not any(issubclass(arg, BaseModel) for arg in args):
        return False

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


def _is_collection_type(field_info: FieldInfo) -> bool:
    anno = field_info.annotation
    if anno and getattr(anno, "__origin__", None) in (list, set):
        return True
    return False


def _is_choice(field_info: FieldInfo) -> bool:
    anno = field_info.annotation
    if anno and getattr(anno, "__origin__", None) is Literal:
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
                    field=key, cls=annotated_model, parent=sub_command
                )

                sub_command.sub_commands.append(new_sub_command)
                tokenize(annotated_model, new_sub_command)
        elif _is_choice(value):
            if value.is_required():
                sub_command.tokens[key] = Choice(key, field_info=value)
                # sub_command.args.append(Choice(key, field_info=value))
            else:
                sub_command.tokens[key] = OptionalChoice(key, field_info=value)

        elif _is_boolean_type(value):
            if value.is_required():
                sub_command.tokens[key] = Boolean(key, field_info=value)
            else:
                sub_command.tokens[key] = OptionalBoolean(key, field_info=value)

        elif _is_collection_type(value):
            if value.is_required():
                sub_command.tokens[key] = Collection(key, field_info=value)
            else:
                sub_command.tokens[key] = OptionalCollection(key, field_info=value)
        elif value.is_required():
            # becomes a positional
            sub_command.tokens[key] = Positional(key, field_info=value)
        else:
            sub_command.tokens[key] = Optional(key, field_info=value)


def validate_model(model: type[BaseModel]) -> None:
    """Validate the input model to see it is useful for cli generation.

    Done before anything else.
    """
    # todo: validate only one subcommand.

    # todo: a subcommand must always be the last one defined.

    # todo: validate no pydantic model as field value.

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
    try:
        if issubclass(model, BaseModel):
            yield model
    except TypeError:
        # python version 3.10 cannot handle annotated types.
        # as soon as we drop support for 3.10 this call can be rewritten.
        pass

    if fields := getattr(model, "model_fields", None):
        for item in fields.values():
            yield from iter_over_model(item.annotation)
            for arg in get_args(item.annotation):
                yield from iter_over_model(arg)

    # for item in model.model_fields.values():
    #     if getattr(item.annotation, "__origin__", None):
    #         # __origin__ is used can be seen as a container type. like a union, but also as a list.
    #         # if we encounter this property we want to check the children of this container.
    #         args = get_args(item.annotation)
    #         for arg in args:
    #             if isclass(arg) and issubclass(arg, BaseModel):
    #                 yield from iter_over_model(arg)
    #     elif getattr(item.annotation, "__class__", None):
    #         if issubclass(item.annotation.__class__, BaseModel):
    #             yield from iter_over_model(item.annotation)
    #         args = get_args(item.annotation)
    #         for arg in args:
    #             if isclass(arg) and issubclass(arg, BaseModel):
    #                 yield from iter_over_model(arg)
    #     elif isclass(item.annotation) and issubclass(item.annotation, BaseModel):
    #         yield from iter_over_model(item.annotation)
