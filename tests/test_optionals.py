from pydantic import BaseModel
from clipstick._clipstick import parse
import pytest


class OptionalsModel(BaseModel):
    """A model with only optionals."""

    value_1: int = 10
    """Optional value 1."""

    value_2: str = "ABC"


def test_no_optionals():
    model = parse(OptionalsModel, [])
    assert model == OptionalsModel()


def test_positional():
    with pytest.raises(ValueError):
        parse(OptionalsModel, [20])


def test_some_optionals():
    model = parse(OptionalsModel, ["--value-1", "24"])
    assert model == OptionalsModel(value_1=24)


def test_all_optionals():
    model = parse(OptionalsModel, ["--value-1", "24", "--value-2", "25"])
    assert model == OptionalsModel(value_1=24, value_2="25")


def test_help(capture_output):
    out = capture_output(OptionalsModel, ["-h"])

    assert "A model with only optionals." in out
    assert "--value-1" in out
    assert "Optional value 1." in out
    assert "--value-2" in out
