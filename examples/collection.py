from clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    """My model with with a collection."""

    my_values: list[str]
    """A collection type."""


print(parse(MyModel))
