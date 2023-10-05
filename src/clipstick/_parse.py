from pydantic.fields import FieldInfo
from types import UnionType
from clipstick._docstring import set_undefined_field_descriptions_from_var_docstrings
from clipstick._tokens import (
    OptionalKeyArgs,
    PositionalArg,
    Subcommand,
    Command,
    BooleanFlag,
    OptionalBooleanFlag,
)


from pydantic import BaseModel


from typing import get_args


def _is_subcommand(attribute: str, field_info: FieldInfo) -> bool:
    if not isinstance(field_info.annotation, UnionType):
        return False
    args = get_args(field_info.annotation)
    if not all(issubclass(arg, BaseModel) for arg in args):
        return False
    if not field_info.is_required():
        raise ValueError("Should be required values.")
    return True


def _is_boolean_type(field_info: FieldInfo) -> bool:
    anno = field_info.annotation
    if anno is bool:
        return True
    return False


def tokenize(model: type[BaseModel], sub_command: Subcommand | Command) -> None:
    # todo: move this somewhere else.
    set_undefined_field_descriptions_from_var_docstrings(model)

    for key, value in model.model_fields.items():
        if _is_subcommand(key, value):
            for annotated_model in get_args(value.annotation):
                new_sub_command = Subcommand(
                    key, annotated_model.__name__, cls=annotated_model
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
