import pytest
from clipstick._clipstick import parse
from pydantic import BaseModel


class StrPositional(BaseModel):
    my_value: str
    """A string positional."""


class IntPositional(BaseModel):
    my_value: int


def test_parse_simple_positional_only():
    model = parse(StrPositional, ["Adam"])
    assert model == StrPositional(my_value="Adam")


def test_too_much_positionals_must_raise(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(StrPositional, ["Adam", "Ondra"])

    assert err.value.code == 1


def test_int_positional_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(IntPositional, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Arguments]

Arguments:
    my-value              [int]
"""
        == capture_output.captured_output
    )


def test_str_positional_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(StrPositional, ["-h"])

    assert err.value.code == 0

    assert (
        """
Usage: my-cli-app [Arguments]

Arguments:
    my-value             A string positional. [str]
"""
        == capture_output.captured_output
    )
