from pydantic import BaseModel

from clipstick._clipstick import parse


class SubModelOne(BaseModel):
    value: int


class SubModelTwo(BaseModel):
    value: str


class MainModel(BaseModel):
    """The main entry point."""

    debug: bool
    """Enable debugging"""

    sub_command: SubModelOne | SubModelTwo


class NestedModel(BaseModel):
    sub_command: SubModelTwo | SubModelOne


class DeeplyNestedModel(BaseModel):
    sub_command: SubModelOne | NestedModel


def test_parse_nested():
    model = parse(MainModel, ["true", "SubModelTwo", "10"])
    assert model == MainModel(debug=True, sub_command=SubModelTwo(value="10"))


def test_deeply_nested_model_nest_1():
    model = parse(DeeplyNestedModel, ["SubModelOne", "10"])
    assert model == DeeplyNestedModel(sub_command=SubModelOne(value=10))


def test_deeply_nested_model_nest_2():
    model = parse(DeeplyNestedModel, ["NestedModel", "SubModelOne", "11"])
    assert model == DeeplyNestedModel(
        sub_command=NestedModel(sub_command=SubModelOne(value=11))
    )
