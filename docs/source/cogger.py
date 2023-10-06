from clipstick import parse
import io
from contextlib import redirect_stdout
import inspect
from pathlib import Path
from rich.console import Console
from rich.markup import escape

base_path = Path(__file__).parent.parent.parent


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
    src = get_source_path(model)
    cmd = f">>>  python {src} -h\n"
    with redirect_stdout(io.StringIO()) as fl:
        try:
            model = parse(model, ["-h"])
        except SystemExit:
            pass

    print_output = fl.getvalue()

    console = Console(record=True, width=110, highlight=False)
    console.print(cmd)
    console.print(escape(print_output))
    svg = src.with_suffix(".svg")
    console.save_svg(svg, title="")

    return str(svg)
