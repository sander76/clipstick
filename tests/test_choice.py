from typing import Literal
from pydantic import BaseModel
from clipstick import parse


class ModelWithChoice(BaseModel):
    choice: Literal["option1", "option2"]


class ModelWithOptionalChoice(BaseModel):
    choice: Literal["option1", "option2"] = "option1"


def test_choice():
    model = parse(ModelWithChoice, ["option1"])

    assert model.choice == "option1"


def test_optional_choice():
    model = parse(ModelWithOptionalChoice, ["--choice", "option2"])
    assert model.choice == "option2"


def test_model_help(capture_output):
    out = capture_output(ModelWithChoice, ["-h"])

    assert "allowed values" in out
    assert "option1" in out
    assert "option2" in out
