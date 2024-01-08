from typing import Annotated, Optional, Union

import pytest
from clipstick._annotations import short
from clipstick._clipstick import parse
from pydantic import BaseModel


class OptionalsModel(BaseModel):
    """A model with only optionals."""

    value_1: int = 10
    """Optional value 1."""

    value_2: str = "ABC"


class OptionalWithShort(BaseModel):
    value_1: Annotated[int, short("v")] = 10


class OptionalValueNoneOptional(BaseModel):
    value_1: Optional[int] = None


class OptionalValueNoneUnion(BaseModel):
    value_1: Union[int, None] = None


class OptionalValueNonePipe(BaseModel):
    value_1: int | None = None


def test_no_optionals():
    model = parse(OptionalsModel, [])
    assert model == OptionalsModel()


def test_positional():
    with pytest.raises(SystemExit):
        parse(OptionalsModel, [20])


def test_some_optionals():
    model = parse(OptionalsModel, ["--value-1", "24"])
    assert model == OptionalsModel(value_1=24)


def test_all_optionals():
    model = parse(OptionalsModel, ["--value-1", "24", "--value-2", "25"])
    assert model == OptionalsModel(value_1=24, value_2="25")


@pytest.mark.parametrize("args", [["--value-1", "12"], ["-v", "12"]])
def test_optional_with_short(args):
    model = parse(OptionalWithShort, args)
    assert model == OptionalWithShort(value_1=12)


def test_optional_value_old_typing():
    model = parse(OptionalValueNoneOptional, ["--value-1", 10])
    assert model == OptionalValueNoneOptional(value_1=10)


def test_optional_value_new_typing():
    model = parse(OptionalValueNonePipe, ["--value-1", 10])
    assert model == OptionalValueNonePipe(value_1=10)


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(OptionalsModel, ["-h"])

    assert err.value.code == 0
    assert """
Usage: my-cli-app [Options]

A model with only optionals.

Options:
    --value-1            Optional value 1. [int] [default = 10]
    --value-2             [str] [default = ABC]
"""


def test_help_with_shorts(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(OptionalWithShort, ["-h"])

    assert err.value.code == 0
    assert "-v --value-1" in capture_output.captured_output


@pytest.mark.parametrize(
    "model", [OptionalValueNonePipe, OptionalValueNoneOptional, OptionalValueNoneUnion]
)
def test_help_union_none(model, capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(model, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Options]

Options:
    --value-1             [int | None] [default = None]
"""
        == capture_output.captured_output
    )
