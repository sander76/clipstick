from typing import Literal

import pytest
from clipstick import parse
from pydantic import BaseModel


class ModelWithChoice(BaseModel):
    choice: Literal["option1", "option2"]


class ModelWithOptionalChoice(BaseModel):
    choice: Literal["option1", "option2"] = "option1"
    """A choice with a default."""


def test_choice():
    model = parse(ModelWithChoice, ["option1"])

    assert model.choice == "option1"


def test_optional_choice():
    model = parse(ModelWithOptionalChoice, ["--choice", "option2"])
    assert model.choice == "option2"


def test_choice_help(capture_output):
    with pytest.raises(SystemExit):
        capture_output(ModelWithChoice, ["-h"])

    assert "Arguments" in capture_output.captured_output
    assert "[allowed values: option1, option2]" in capture_output.captured_output


def test_optional_choice_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithOptionalChoice, ["-h"])
    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Options]

Options:
    --choice             A choice with a default. [allowed values: option1, option2] [default = option1]
"""
        == capture_output.captured_output
    )
