from typing import Annotated

from clipstick import parse, short
from pydantic import BaseModel


class MyModel(BaseModel):
    """A model with a required boolean value."""

    verbose: Annotated[bool, short("v")]
    """Some verbose thingy with a shorthand."""

    more_verbose: Annotated[bool, short("m")] = False
    """More verbose thingy with a default and short."""


print(parse(MyModel))
