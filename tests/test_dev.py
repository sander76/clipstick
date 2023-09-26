from pydantic import BaseModel

from beta.tokens import parse


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


def test_parse_simple():
    model = parse(SimpleModel, ["true", "--proceed", "false"])
    assert model == SimpleModel(verbose=True, proceed=False)


def test_parse_nested():
    model = parse(MainModel, ["true", "SubModelTwo", "10"])
    assert model == MainModel(debug=True, sub_command=SubModelTwo(value="10"))
