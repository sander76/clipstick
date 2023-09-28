from pydantic import BaseModel

from smplcli._clipstick import parse


class SimpleModel(BaseModel):
    """A simple model. Main description."""

    snake_cased: bool
    proceed: bool = True


def test_parse_simple_positional_only():
    model = parse(SimpleModel, ["true"])
    assert model == SimpleModel(verbose=True)


def test_parse_simple_mode_with_optional():
    model = parse(SimpleModel, ["true", "--proceed", "false"])
    assert model == SimpleModel(verbose=True, proceed=False)


def test_parse_simple_model_help(capsys):
    try:
        parse(SimpleModel, ["-h"])
    except SystemExit:
        pass

    cap = capsys.readouterr()
    out = cap.out
    assert "snake-cased" in out
    assert "A simple model. Main description." in out
