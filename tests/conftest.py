from typing import Callable
import pytest
from pydantic import BaseModel
from tests import HELP_OUTPUT_FOLDER
from pathlib import Path
from clipstick import parse
import tests

from clipstick._help import console

TEST_FOLDER = Path(tests.__file__).parent


@pytest.fixture
def capture_output(capsys, request) -> Callable[[type[BaseModel], list[str]], str]:
    # set this width. othewise rich will assume the console with of your ide window
    # and potentially wrap output breaking your tests.
    console.width = 1000

    def parse_input(model: type[BaseModel], args: list[str]) -> str:
        try:
            parse(model, args)
        except SystemExit:
            pass
        file_path = Path(request.fspath)
        relative_from_test = file_path.relative_to(TEST_FOLDER)
        output = HELP_OUTPUT_FOLDER / relative_from_test.with_suffix("")

        output.mkdir(exist_ok=True)

        target_file = (output / request.function.__name__).with_suffix(".txt")

        out = capsys.readouterr().out

        target_file.write_text(out, encoding="utf-8")
        return out

    return parse_input
