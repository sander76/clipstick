from pydantic import BaseModel

from smplcli.tokens import parse


class SimpleModel(BaseModel):
    verbose: bool
    proceed: bool = True


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


def test_parse_simple_positional_only():
    model = parse(SimpleModel, ["true"])
    assert model == SimpleModel(verbose=True)


def test_parse_simple_mode_with_optional():
    model = parse(SimpleModel, ["true", "--proceed", "false"])
    assert model == SimpleModel(verbose=True, proceed=False)


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
