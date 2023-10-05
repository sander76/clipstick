from clipstick import parse
import io
from contextlib import redirect_stdout
import inspect
from pathlib import Path

base_path = Path(__file__).parent.parent


def get_source_path(item):
    source_file = Path(inspect.getfile(item))
    return source_file.relative_to(base_path)


def print_source(module):
    source = inspect.getsource(module)
    return f"# {get_source_path(module)}\n\n" + source


def print_output(model, args):
    cmd = f"# >>> python {get_source_path(model)} {' '.join(args)}\n"

    parsed = parse(model, args)
    return cmd + parsed.__repr__()


def print_help(model):
    cmd = f"# >>> python {get_source_path(model)} -h\n"
    with redirect_stdout(io.StringIO()) as fl:
        try:
            model = parse(model, ["-h"])
        except SystemExit:
            pass

    print_output = fl.getvalue()
    return cmd + print_output
