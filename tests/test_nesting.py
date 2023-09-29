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

    value: bool


class FirstLevelNestedModel(BaseModel):
    """First level model."""

    sub_command: SecondLevelModelOne | SecondLevelModelTwo


def test_deeply_nested_model_nest_1():
    model = parse(
        FirstLevelNestedModel, ["SecondLevelModelOne", "ThirdLevelModelOne", "10"]
    )
    assert model == FirstLevelNestedModel(
        sub_command=SecondLevelModelOne(sub_command=ThirdLevelModelOne(value=10))
    )


def test_deeply_nested_model_nest_2():
    model = parse(
        FirstLevelNestedModel, ["SecondLevelModelOne", "ThirdLevelModelTwo", "11"]
    )
    assert model == FirstLevelNestedModel(
        sub_command=SecondLevelModelOne(sub_command=ThirdLevelModelTwo(value="11"))
    )


def test_deeply_nested_model_nest_3():
    model = parse(FirstLevelNestedModel, ["SecondLevelModelTwo", "true"])
    assert model == FirstLevelNestedModel(sub_command=SecondLevelModelTwo(value=True))


def test_model_help_first_level(capsys):
    try:
        parse(FirstLevelNestedModel, ["-h"])
    except SystemExit:
        pass

    out = capsys.readouterr().out
    assert "First level model." in out
    assert "SecondLevelModelOne" in out
    assert "Second level model 1." in out

    assert "SecondLevelModelTwo" in out
    assert "Second level model 2." in out


def test_model_help_second_level(capsys):
    try:
        parse(FirstLevelNestedModel, ["SecondLevelModelOne", "-h"])
    except SystemExit:
        pass

    out = capsys.readouterr().out
    assert "First level model." not in out
    assert "SecondLevelModelOne" not in out
    assert "Second level model 1." in out
    assert "ThirdLevelModelTwo" in out
    assert "ThirdLevelModelOne" in out
    assert "Second level model one value." in out
