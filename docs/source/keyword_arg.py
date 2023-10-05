from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: int = 22


if __name__ == "__main__":
    model = parse(MyModel)
