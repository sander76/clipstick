"""General tests that check pydantic v2 functionality.

Can probably be removed later when code is more mature.
"""

from pydantic import BaseModel


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


def test_nested_model_correct_submodel():
    model = MainModel(debug="true", sub_command=SubModelTwo(value="1"))
    assert model.sub_command.value == "1"


def test_nested_model_from_dict():
    dct = {"debug": "true", "sub_command": {"value": "1"}}
    MainModel.model_validate(dct)


class ModelWithListOfInts(BaseModel):
    items: list[int]


def test_model_with_list():
    model = ModelWithListOfInts(items=["1", "2", "3"])
    assert model.items == [1, 2, 3]
