from typing import Literal

import pytest
from clipstick import parse
from pydantic import BaseModel


class ModelWithChoice(BaseModel):
    choice: Literal["option1", "option2"]


class ModelWithOptionalChoice(BaseModel):
    choice: Literal["option1", "option2"] = "option1"
    """A choice with a default."""


class ModelWithOptionalIntChoice(BaseModel):
    choice: Literal[1, 2] = 1
    """A choice with a default."""


class ModelWithOptionalNoneChoice(BaseModel):
    choice: Literal["option1", "option2"] | None = None
    """A choice with a default."""


def test_choice():
    model = parse(ModelWithChoice, ["option1"])

    assert model.choice == "option1"


def test_optional_choice():
    model = parse(ModelWithOptionalChoice, ["--choice", "option2"])
    assert model.choice == "option2"


def test_optional_none_choice():
    model = parse(ModelWithOptionalNoneChoice, ["--choice", "option2"])
    assert model.choice == "option2"


def test_choice_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithChoice, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Arguments]

Arguments:
    choice                [allowed values: option1, option2]
"""
        == capture_output.captured_output
    )


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


def test_optional_none_choice_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithOptionalNoneChoice, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Options]

Options:
    --choice             A choice with a default. [allowed values: option1, option2] [default = None]
"""
        == capture_output.captured_output
    )


def test_optional_int_choice_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithOptionalIntChoice, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Options]

Options:
    --choice             A choice with a default. [allowed values: 1, 2] [default = 1]
"""
        == capture_output.captured_output
    )


def test_failing_choice(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithOptionalChoice, ["--choice", "option3"])

    assert err.value.code == 1
    assert (
        """ERROR:
Incorrect value for --choice ('option3'). Input should be 'option1' or 'option2'
"""
        == capture_output.captured_output
    )
