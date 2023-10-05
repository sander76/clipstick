from clipstick._parse import tokenize
from clipstick._tokens import Command, TPydanticModel
import sys


def parse(model: type[TPydanticModel], args: list[str] | None = None) -> TPydanticModel:
    if args is None:
        args = sys.argv[1:]

    root_node = Command("__main_entry__", model.__name__, model)
    tokenize(model=model, sub_command=root_node)

    success, idx = root_node.match(0, args)
    if not idx == len(args):
        raise ValueError("Unable to consume all args")
    if success:
        parsed = root_node.parse(args)
    else:
        raise ValueError("No matching pattern found.")
    return parsed["__main_entry__"]
