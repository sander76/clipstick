from clipstick import parse
import inspect
from pathlib import Path

base_path = Path(__file__).parent.parent.parent


def get_source_path(item):
    source_file = Path(inspect.getfile(item))
    return source_file.relative_to(base_path)


def print_source(module):
    source = inspect.getsource(module)

    _str = ["```python", f"# {get_source_path(module)}\n", source, "```"]

    return "\n".join(_str)


def print_output(model, args: list[str]):
    cmd = f"# >>> python {get_source_path(model)} {' '.join(args)}\n"

    parsed = parse(model, args)
    return "\n".join(
        [
            "```python",
            cmd,
            parsed.__repr__(),
            "```",
        ]
    )


def print_error(model, args: list[str]):
    from clipstick._help import console

    console.record = True
    console.width = 110
    src = get_source_path(model)

    cmd = f">>> python {src} {' '.join(args)}\n"
    console.print(cmd)

    try:
        model = parse(model, args)
    except SystemExit:
        pass

    svg = src.with_suffix(".svg")
    console.save_svg(svg, title="")

    return str(svg)


def print_help(model):
    from clipstick._help import console

    console.record = True
    console.width = 110

    src = get_source_path(model)

    console.print(f">>>  python {src} -h\n")

    try:
        model = parse(model, ["-h"])
    except SystemExit:
        pass

    svg = src.with_suffix(".svg")
    console.save_svg(svg, title="")

    return str(svg)
