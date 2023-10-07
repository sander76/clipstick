from typing import Annotated
from pydantic import BaseModel
from clipstick._annotations import short
from clipstick._parse import _validate_shorts
import pytest
from clipstick._exceptions import TooManyShortsException


class Model_1(BaseModel):
    val: Annotated[str, short("v")]
    val_1: Annotated[str, short("v")]


class Model_2(BaseModel):
    sub_model: Model_1


class Model_3(BaseModel):
    sub_command: Model_2 | Model_1


@pytest.mark.parametrize("model", [Model_1, Model_2, Model_3])
def test_validate_shorts_fail(model):
    with pytest.raises(TooManyShortsException):
        _validate_shorts(model)
