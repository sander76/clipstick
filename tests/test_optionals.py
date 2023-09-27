from pydantic import BaseModel
from smplcli.tokens import parse


class OptionalsModel(BaseModel):
    """A model with only optionals."""

    value_1: int = 10
    """Optional value 1."""

    value_2: str = "ABC"


def test_no_optionals():
    model = parse(OptionalsModel, [])
    assert model == OptionalsModel()


def test_some_optionals():
    model = parse(OptionalsModel, ["--value_1", "24"])
    assert model == OptionalsModel(value_1=24)


def test_all_optionals():
    model = parse(OptionalsModel, ["--value_1", "24", "--value_2", "25"])
    assert model == OptionalsModel(value_1=24, value_2="25")


def test_help(capsys):
    try:
        parse(OptionalsModel, ["-h"])
    except SystemExit:
        pass

    cap = capsys.readouterr()
    out = cap.out
    print(cap.out)
