from clipstick import parse
from pydantic import BaseModel, PositiveInt


class MyModel(BaseModel):
    my_age: PositiveInt = 10
    """Your age."""


model = parse(MyModel)
