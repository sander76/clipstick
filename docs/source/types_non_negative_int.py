from typing import Annotated
from pydantic import BaseModel, PositiveInt
from clipstick import parse, short


class MyModel(BaseModel):
    my_value: Annotated[PositiveInt, short("m")] = 10
    """Value must be positive"""


if __name__ == "__main__":
    model = parse(MyModel)
