from typing import Any, Callable
import pytest
from pydantic import BaseModel
from tests import HELP_OUTPUT_FOLDER
from pathlib import Path
from clipstick import parse
import tests

from clipstick._help import console

TEST_FOLDER = Path(tests.__file__).parent


class CapturedOutput:
    def __init__(self, fixture_request, capsys) -> None:
        self.captured_output: str | None = None
        self._fixture_request = fixture_request
        self._capsys = capsys

    def __call__(self, model: type[BaseModel], args: list[str]) -> None:
        try:
            parse(model, args)
        finally:
            file_path = Path(self._fixture_request.fspath)
            relative_from_test = file_path.relative_to(TEST_FOLDER)
            output = HELP_OUTPUT_FOLDER / relative_from_test.with_suffix("")

            output.mkdir(exist_ok=True)

            target_file = (
                output / self._fixture_request.function.__name__
            ).with_suffix(".txt")

            self.captured_output = self._capsys.readouterr().out

            target_file.write_text(self.captured_output, encoding="utf-8")


@pytest.fixture
def capture_output(capsys, request) -> CapturedOutput:
    # set this very long width. othewise rich will assume the console with of your ide window
    # and potentially wrap output breaking your tests.
    console.width = 1000

    return CapturedOutput(request, capsys)

    # def parse_input(
    #     model: type[BaseModel], args: list[str], raise_system_exit=False
    # ) -> str:
    #     try:
    #         parse(model, args)
    #     except SystemExit:
    #         if raise_system_exit:
    #             raise
    #     finally:
    #         file_path = Path(request.fspath)
    #         relative_from_test = file_path.relative_to(TEST_FOLDER)
    #         output = HELP_OUTPUT_FOLDER / relative_from_test.with_suffix("")

    #         output.mkdir(exist_ok=True)

    #         target_file = (output / request.function.__name__).with_suffix(".txt")

    #         out = capsys.readouterr().out

    #         target_file.write_text(out, encoding="utf-8")
    #         # return out

    # return parse_input
