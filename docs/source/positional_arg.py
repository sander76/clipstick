from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    """My model with a required value."""

    my_value: int
    """My required value."""


if __name__ == "__main__":
    """your cli entrypoint"""
    model = parse(MyModel)
