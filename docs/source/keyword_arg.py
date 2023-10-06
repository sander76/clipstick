from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    """A model with a keyworded optional value"""

    my_value: int = 22
    """My value with a default."""


if __name__ == "__main__":
    model = parse(MyModel)
