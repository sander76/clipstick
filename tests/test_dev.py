from pydantic import BaseModel

from arrrg.tokens import tokenize, tokens, parse


class SimpleModel(BaseModel):
    verbose: bool
    proceed: bool = True


class SubModelOne(BaseModel):
    value: int


class SubModelTwo(BaseModel):
    value: str


class MainModel(BaseModel):
    debug: bool
    """Enable debugging"""

    sub_command: SubModelOne | SubModelTwo


def test_parse_simple():
    starting_point = []
    tokens["main"] = starting_point
    result = tokenize(MainModel, starting_point)
    print(tokens)

    parse(["true", "SubModelTwo", "10"])
