from pydantic import BaseModel

from clipstick._clipstick import parse


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


def test_parse_simple_model_help(capture_output):
    out = capture_output(SimpleModel, ["-h"])

    assert "snake-cased" in out
    assert "A snake cased argument." in out

    assert "snake-cased-kwarg" in out
    assert "A simple model. Main description." in out
