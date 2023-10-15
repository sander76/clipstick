from clipstick._parse import tokenize, validate_model
from clipstick._tokens import Command, TPydanticModel
from clipstick._exceptions import ClipStickError
import sys
from clipstick._help import console


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
        console.print("Unable to consume all provided arguments.")
        sys.exit(1)
    if not success:
        console.print("Unable to resolve the arguments into a usable command line.")
        sys.exit(1)

    try:
        parsed = root_node.parse(args)
    except ClipStickError as err:
        console.print(err)
        sys.exit(1)
    else:
        return parsed[entry_point]
