from typing import Literal
from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: Literal["option1", "option2"] = "option1"


if __name__ == "__main__":
    model = parse(MyModel)
