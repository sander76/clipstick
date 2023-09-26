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
    model = MainModel(debug="true", sub_command=SubModelTwo(value="1a"))
    assert model.sub_command.value == "1"


def test_nested_model_from_dict():
    dct = {"debug": "true", "sub_command": {"value": "1"}}
    model = MainModel.model_validate(dct)
