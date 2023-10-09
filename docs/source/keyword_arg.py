from typing import Annotated
from pydantic import BaseModel
from clipstick import parse, short


class MyModel(BaseModel):
    """A model with a keyworded optional value"""

    my_value: int = 22
    """My value with a default."""
    another_value: Annotated[str, short("a")] = "value"
    """Value with a shorthand"""


if __name__ == "__main__":
    model = parse(MyModel)
