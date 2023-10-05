from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: int


if __name__ == "__main__":
    """your cli entrypoint"""
    model = parse(MyModel)
