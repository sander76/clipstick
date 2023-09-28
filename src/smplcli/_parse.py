from pydantic.fields import FieldInfo
from types import UnionType
from smplcli._docstring import set_undefined_field_descriptions_from_var_docstrings
from smplcli._tokens import HelpArg, OptionalKeyArgs, PositionalArg, Subcommand


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


def tokenize(model: type[BaseModel], sub_command: Subcommand) -> None:
    # todo: move this somewhere else.
    set_undefined_field_descriptions_from_var_docstrings(model)

    sub_command.help_args.append(HelpArg("help", sub_command))
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
            sub_command.args.append(OptionalKeyArgs(key))
