from pathlib import Path
from typing import Annotated, Literal

import pytest
from clipstick import short
from pydantic import BaseModel, FilePath, PositiveInt


class FailingPositional(BaseModel):
    my_value: PositiveInt


def test_too_many_arguments(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FailingPositional, ["10", "12"])

    assert err.value.code == 1
    assert (
        """ERROR:
Unable to consume all provided arguments.
Use the-h argument to help
"""
        == capture_output.captured_output
    )


def test_incorrect_age(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FailingPositional, ["no_int"])

    assert err.value.code == 1
    assert (
        """ERROR:
Incorrect value for my-value ('no_int'). Input should be a valid integer, unable to parse string as an integer
"""
        == capture_output.captured_output
    )


class RequiredValue(BaseModel):
    my_value: int
    another_value: str


def test_too_little_values(capture_output):
    """Two positional values are required.

    Only one is given.
    """
    with pytest.raises(SystemExit) as err:
        capture_output(RequiredValue, ["10"])

    assert err.value.code == 1
    assert (
        """ERROR:
Missing a value for positional argument 'another-value'
"""
        == capture_output.captured_output
    )


class NonExistingPath(BaseModel):
    my_path: FilePath


def test_failing_non_existing_path(capture_output):
    pth = Path("clipstick/non_exist")
    with pytest.raises(SystemExit) as err:
        capture_output(NonExistingPath, [str(pth)])

    assert err.value.code == 1
    assert (
        "Incorrect value for my-path ('clipstick/non_exist'). Path does not point to a file"
        in capture_output.captured_output
    )


class FailingChoice(BaseModel):
    my_value: Literal["option1", "option2"] = "option1"


class FailingOptional(BaseModel):
    my_value: Annotated[PositiveInt, short("m")] = 10


@pytest.mark.parametrize(
    "args",
    [
        ["-m", "-10"],
        ["--my-value", "-10"],
    ],
)
def test_correct_key_used_in_error_message(capture_output, args):
    with pytest.raises(SystemExit) as err:
        capture_output(FailingOptional, args)

    assert err.value.code == 1
    assert (
        f"Incorrect value for {args[0]} ('-10'). Input should be greater than 0"
    ) in capture_output.captured_output
