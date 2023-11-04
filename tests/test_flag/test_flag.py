import pytest
from clipstick._clipstick import parse
from pydantic import BaseModel


class Flag(BaseModel):
    """A model with a flag."""

    continue_this: bool
    """proceed or not."""


def test_flag_true():
    model = parse(Flag, ["--continue-this"])
    assert model == Flag(continue_this=True)


def test_flag_false():
    model = parse(Flag, ["--no-continue-this"])
    assert model == Flag(continue_this=False)


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(Flag, ["-h"])

    assert err.value.code == 0
    assert (
        "--continue-this/--no-continue-this proceed or not. [bool]"
        in capture_output.captured_output
    )
