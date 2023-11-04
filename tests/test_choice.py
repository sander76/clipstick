from typing import Literal

import pytest
from pydantic import BaseModel

from clipstick import parse


class ModelWithChoice(BaseModel):
    choice: Literal["option1", "option2"]


class ModelWithOptionalChoice(BaseModel):
    choice: Literal["option1", "option2"] = "option1"


def test_choice():
    model = parse(ModelWithChoice, ["option1"])

    assert model.choice == "option1"


def test_optional_choice():
    model = parse(ModelWithOptionalChoice, ["--choice", "option2"])
    assert model.choice == "option2"


def test_choice_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithChoice, ["-h"])

    assert "Arguments" in capture_output.captured_output
    assert "[allowed values: option1, option2]" in capture_output.captured_output


def test_optional_choice_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithOptionalChoice, ["-h"])

    assert "Options:" in capture_output.captured_output
    assert (
        "[allowed values: option1, option2] [default = option1]"
        in capture_output.captured_output
    )
