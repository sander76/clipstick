from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: int


model = parse(MyModel, ["10"])

assert model == MyModel(my_value=10)
