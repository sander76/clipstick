from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: int = 22


model = parse(MyModel, ["--my-value", "25"])

assert model == MyModel(my_value=25)
