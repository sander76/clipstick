from typing import Annotated

from clipstick import parse, short
from pydantic import BaseModel


class MyModel(BaseModel):
    """A model with a keyword and shorthand optional value"""

    my_value: Annotated[int, short("m")] = 22  # <-- this adds a shorthand of `-m`.
    """My value with a default."""


print(parse(MyModel))
