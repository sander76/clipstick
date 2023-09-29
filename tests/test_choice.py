from contextlib import suppress
from typing import Literal
from pydantic import BaseModel, ValidationError
from clipstick import parse
import pytest


class ModelWithChoice(BaseModel):
    choice: Literal["option1", "option2"]


def test_choice():
    model = parse(ModelWithChoice, ["option1"])

    assert model.choice == "option1"


def test_wrong_choice():
    with pytest.raises(ValidationError):
        parse(ModelWithChoice, ["wrong_options"])


def test_model_help(capsys):
    with suppress(SystemExit):
        parse(ModelWithChoice, ["-h"])

    out = capsys.readouterr().out

    assert "allowed values" in out
    assert "option1" in out
    assert "option2" in out
