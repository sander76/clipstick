import os
import subprocess
from itertools import chain
from pathlib import Path
from subprocess import PIPE, STDOUT

from rich.console import Console
from rich.text import Text

base_path = Path(__file__).parent.parent

unique_svg_id = "abcdefg"


def capture(file: Path, args: list[str], output: Path) -> Path:
    # create a console to capture and save the output.
    console = Console(width=100, record=True)
    console.print("")
    console.print(
        Text.assemble(
            Text("➜ ", style="green"),
            f"python {file.relative_to(base_path)} {' '.join(args)}",
        )
    )
    console.print("")
    result = subprocess.run(
        ["python", str(file)] + args,
        stdout=PIPE,
        stderr=STDOUT,
        env=os.environ
        | {"FORCE_COLOR": "1"},  # make sure we also get ansi codes (colors back.)
    )

    data = result.stdout.decode("utf-8")

    txt = Text.from_ansi(data)
    console.print(txt)

    console.save_svg(str(output), title="", unique_id=unique_svg_id)
    return output


if __name__ == "__main__":
    output_folder = base_path / "docs" / "_images"
    examples_folder = base_path / "examples"

    for fl in chain(
        (base_path / "docs" / "_python").glob("*.py"),
        examples_folder.glob("*.py"),
    ):
        name = fl.stem + "-help.svg"
        capture(fl, ["-h"], output=output_folder / name)

    name_source = (examples_folder / "name.py").read_text(encoding="utf-8")
    name_output = capture(
        examples_folder / "name.py",
        ["superman", "--repeat-count", "4"],
        output=output_folder / "name-output.svg",
    )

    name_error = capture(
        examples_folder / "name.py",
        ["superman", "--age", "too old"],
        output=output_folder / "name-wrong-age.svg",
    )

    capture(
        examples_folder / "positional.py",
        [],
        output=output_folder / "positional-error.svg",
    )

    capture(
        examples_folder / "choice.py",
        ["--my-value", "option3"],
        output=output_folder / "choice-wrong-choice.svg",
    )
    capture(
        examples_folder / "subcommand.py",
        ["merge", "-h"],
        output=output_folder / "subcommand-merge-help.svg",
    )
    capture(
        examples_folder / "types_non_negative_int.py",
        ["--my-age", "-4"],
        output_folder / "types_non_negative_int-invalid.svg",
    )
    capture(
        examples_folder / "types_file_exists.py",
        ["non-exising-file.txt"],
        output_folder / "types_file_exists-invalid.svg",
    )
    capture(
        examples_folder / "collection.py",
        ["--my-values", "value1", "--my-values", "value2"],
        output_folder / "collection-usage.svg",
    )
