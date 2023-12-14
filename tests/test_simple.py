import pytest
from clipstick._clipstick import parse
from pydantic import BaseModel


class SimpleModel(BaseModel):
    """A simple model. Main description."""

    my_name: str
    """A snake cased argument."""
    snake_cased_kwarg: int = 10


def test_parse_simple_positional_only():
    model = parse(SimpleModel, ["Adam"])
    assert model == SimpleModel(my_name="Adam")


def test_parse_simple_mode_with_optional():
    model = parse(SimpleModel, ["Adam", "--snake-cased-kwarg", "10"])
    assert model == SimpleModel(my_name="Adam", snake_cased_kwarg=10)


def test_too_much_positionals_must_raise(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(SimpleModel, ["Adam", "Ondra"])

    assert err.value.code == 1


def test_parse_simple_model_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(SimpleModel, ["-h"])

    assert err.value.code == 0
    assert "snake-cased" in capture_output.captured_output
    assert "A snake cased argument." in capture_output.captured_output

    assert "snake-cased-kwarg" in capture_output.captured_output
    assert "A simple model. Main description." in capture_output.captured_output
