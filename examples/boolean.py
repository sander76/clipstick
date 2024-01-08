from typing import Annotated

from clipstick import parse, short
from pydantic import BaseModel


class MyModel(BaseModel):
    """A model with flags."""

    required: bool
    """Some required thingy."""

    with_short: Annotated[bool, short("w")]
    """required flag with short."""

    an_optional: bool = True
    """An optional."""

    optional_with_short: Annotated[bool, short("o")] = False
    """Optional with short."""


print(repr(parse(MyModel)))
