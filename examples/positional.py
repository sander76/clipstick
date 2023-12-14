from clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    """My model with a required value."""

    my_value: int
    """My required value."""


print(parse(MyModel))
