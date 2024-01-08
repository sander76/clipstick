from typing import Literal

from clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    """My model with choice values."""

    required_choice: Literal["option1", "option2"]
    """Required restricted values."""

    optional_choice: Literal[1, 2] = 2
    """Optional with a literal default."""

    optional_with_none: Literal[4, 5] | None = None
    """Optional with None as default."""


print(repr(parse(MyModel)))
