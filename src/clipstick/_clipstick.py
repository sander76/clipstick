from clipstick._parse import tokenize, validate_model
from clipstick._tokens import Command, TPydanticModel
import sys


def parse(model: type[TPydanticModel], args: list[str] | None = None) -> TPydanticModel:
    validate_model(model)
    if args is None:
        entry_point, args = sys.argv[0], sys.argv[1:]
    else:
        # Normally the first item in your sys.argv is the command/entrypoint you've entered.
        # During testing you don't provide that (only the actual arguments you enter after that).
        entry_point = "dummy-entrypoint"

    root_node = Command(key=entry_point, cls=model, parent=None)
    tokenize(model=model, sub_command=root_node)

    success, idx = root_node.match(0, args)
    if not idx == len(args):
        raise ValueError("Unable to consume all args")
    if success:
        parsed = root_node.parse(args)
    else:
        raise ValueError("No matching pattern found.")
    return parsed[entry_point]
