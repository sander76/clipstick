from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    """A model with a required boolean value."""

    verbose: bool
    """Some verbose thingy."""


if __name__ == "__main__":
    model = parse(MyModel)
