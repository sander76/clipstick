import pytest
from pydantic import BaseModel

from clipstick import parse


class ThirdLevelModelOne(BaseModel):
    value: int


class ThirdLevelModelTwo(BaseModel):
    value: str


class SecondLevelModelOne(BaseModel):
    """Second level model 1."""

    value: str = "my-second-level-value"
    """Second level model one value."""

    sub_command: ThirdLevelModelTwo | ThirdLevelModelOne


class SecondLevelModelTwo(BaseModel):
    """Second level model 2."""

    value: int


class FirstLevelNestedModel(BaseModel):
    """First level model."""

    sub_command: SecondLevelModelOne | SecondLevelModelTwo


def test_deeply_nested_model_nest_1():
    model = parse(
        FirstLevelNestedModel, ["second-level-model-one", "third-level-model-one", "10"]
    )
    assert model == FirstLevelNestedModel(
        sub_command=SecondLevelModelOne(sub_command=ThirdLevelModelOne(value=10))
    )


def test_deeply_nested_model_nest_2():
    model = parse(
        FirstLevelNestedModel, ["second-level-model-one", "third-level-model-two", "11"]
    )
    assert model == FirstLevelNestedModel(
        sub_command=SecondLevelModelOne(sub_command=ThirdLevelModelTwo(value="11"))
    )


def test_deeply_nested_model_nest_3():
    model = parse(FirstLevelNestedModel, ["second-level-model-two", "21"])
    assert model == FirstLevelNestedModel(sub_command=SecondLevelModelTwo(value=21))


def test_model_help_first_level(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FirstLevelNestedModel, ["-h"])

    assert err.value.code == 0
    assert "First level model." in capture_output.captured_output
    assert "second-level-model-one" in capture_output.captured_output
    assert "Second level model 1." in capture_output.captured_output

    assert "second-level-model-two" in capture_output.captured_output
    assert "Second level model 2." in capture_output.captured_output


def test_model_help_second_level(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FirstLevelNestedModel, ["second-level-model-one", "-h"])

    assert err.value.code == 0
    assert "First level model." not in capture_output.captured_output
    assert "my-cli-app second-level-model-one" in capture_output.captured_output

    assert "Second level model 1." in capture_output.captured_output
    assert "third-level-model-two" in capture_output.captured_output
    assert "third-level-model-one" in capture_output.captured_output
    assert "Second level model one value." in capture_output.captured_output
