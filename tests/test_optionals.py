from typing import Annotated

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


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(OptionalsModel, ["-h"])

    assert err.value.code == 0
    assert "A model with only optionals." in capture_output.captured_output
    assert "--value-1" in capture_output.captured_output
    assert "Optional value 1." in capture_output.captured_output
    assert "--value-2" in capture_output.captured_output


def test_help_with_shorts(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(OptionalWithShort, ["-h"])

    assert err.value.code == 0
    assert "-v --value-1" in capture_output.captured_output
