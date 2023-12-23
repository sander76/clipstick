from clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    """A model with a keyworded optional value."""

    my_value: int = 22
    """My value with a default."""


print(parse(MyModel))
