from typing import Annotated

from clipstick import parse, short
from pydantic import BaseModel


class MyModel(BaseModel):
    """My model with with a collection."""

    required_collection: list[str]
    """A required collection."""

    optional_short: Annotated[list[int], short("o")] = [1]
    """Optional collection."""


print(repr(parse(MyModel)))
