from typing import Annotated
from pydantic import BaseModel
from clipstick import short


class MyModel(BaseModel):
    """A model with a keyworded optional value"""

    my_value: Annotated[int, short("m")] = 22  # <-- this adds a shorthand of `-m`.
    """My value with a default."""
