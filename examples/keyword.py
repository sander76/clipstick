from typing import Annotated

from clipstick import parse, short
from pydantic import BaseModel


class MyModel(BaseModel):
    """A model with keyworded optional values."""

    my_value: int = 22
    """My value with a default."""

    other_value: int | None = None
    """Value with None as default."""

    with_short: Annotated[str, short("w")] = "some_value"
    """With a shorthand key."""


print(repr(parse(MyModel)))
