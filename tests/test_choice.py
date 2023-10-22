from typing import Literal
from pydantic import BaseModel
import pytest
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
    with pytest.raises(SystemExit) as err:
        capture_output(ModelWithChoice, ["-h"])

    assert err.value.code == 0  # exit code
    assert "allowed values" in capture_output.captured_output
    assert "option1" in capture_output.captured_output
    assert "option2" in capture_output.captured_output
