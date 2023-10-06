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
    out = capture_output(FirstLevelNestedModel, ["-h"])

    assert "First level model." in out
    assert "second-level-model-one" in out
    assert "Second level model 1." in out

    assert "second-level-model-two" in out
    assert "Second level model 2." in out


def test_model_help_second_level(capture_output):
    out = capture_output(FirstLevelNestedModel, ["second-level-model-one", "-h"])

    assert "First level model." not in out
    assert "dummy-entrypoint second-level-model-one" in out

    assert "Second level model 1." in out
    assert "third-level-model-two" in out
    assert "third-level-model-one" in out
    assert "Second level model one value." in out
