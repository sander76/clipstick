import pytest
from pathlib import Path
from typing import Annotated, Literal
from pydantic import BaseModel, FilePath, PositiveInt
from clipstick import short


class FailingPositional(BaseModel):
    my_value: PositiveInt


def test_failing_positional(capture_output):
    out = capture_output(FailingPositional, ["-5"])

    assert (
        "Incorrect value for my-value. Input should be greater than 0, value: -5" in out
    )


class NonExistingPath(BaseModel):
    my_path: FilePath


def test_failing_non_existing_path(capture_output):
    pth = Path("clipstick/non_exist")
    out = capture_output(NonExistingPath, [str(pth)])

    assert (
        "Incorrect value for my-path. Path does not point to a file, value: clipstick/non_exist"
        in out
    )


class FailingChoice(BaseModel):
    my_value: Literal["option1", "option2"] = "option1"


def test_failing_choice(capture_output):
    out = capture_output(FailingChoice, ["--my-value", "option3"])

    assert (
        "Incorrect value for --my-value. Input should be 'option1' or 'option2', value: option3"
        in out
    )


class FailingOptional(BaseModel):
    my_value: Annotated[PositiveInt, short("m")] = 10


@pytest.mark.parametrize(
    "args",
    [
        ["-m", "-10"],
        ["--my-value", "-10"],
    ],
)
def test_failing_optional(capture_output, args):
    out = capture_output(FailingOptional, args)

    assert (
        f"Incorrect value for {args[0]}. Input should be greater than 0, value: -10"
    ) in out
