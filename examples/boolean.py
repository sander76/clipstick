from clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    """A model with a required boolean value."""

    verbose: bool
    """Some verbose thingy."""

    more_verbose: bool = False
    """More verbose thingy with a default."""


if __name__ == "__main__":
    print(parse(MyModel))
