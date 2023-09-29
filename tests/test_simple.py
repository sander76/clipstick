from pydantic import BaseModel

from clipstick._clipstick import parse


class SimpleModel(BaseModel):
    """A simple model. Main description."""

    snake_cased: bool
    """A snake cased argument."""
    snake_cased_kwarg: int = 10


def test_parse_simple_positional_only():
    model = parse(SimpleModel, ["true"])
    assert model == SimpleModel(snake_cased=True)


def test_parse_simple_mode_with_optional():
    model = parse(SimpleModel, ["true", "--snake-cased-kwarg", "10"])
    assert model == SimpleModel(snake_cased=True, snake_cased_kwarg=10)


def test_parse_simple_model_help(capsys):
    try:
        parse(SimpleModel, ["-h"])
    except SystemExit:
        pass

    out = capsys.readouterr().out

    assert "snake-cased" in out
    assert "A snake cased argument." in out

    assert "snake-cased-kwarg" in out
    assert "A simple model. Main description." in out
