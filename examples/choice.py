from typing import Literal

from clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    """My model with choice values."""

    my_value: Literal["option1", "option2"] = "option1"
    """A value with restricted values."""


model = parse(MyModel)
