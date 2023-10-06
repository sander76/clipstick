from typing import Literal
from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    """My model with choice values."""

    my_value: Literal["option1", "option2"] = "option1"
    """A value with restricted values."""


if __name__ == "__main__":
    model = parse(MyModel)
