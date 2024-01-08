from clipstick import parse
from pydantic import BaseModel, PositiveInt


class MyModel(BaseModel):
    """Model with a pydantic validator."""

    my_age: PositiveInt = 10
    """Your age."""


print(repr(parse(MyModel)))
