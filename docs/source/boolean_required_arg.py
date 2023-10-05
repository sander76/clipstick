from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    verbose: bool


if __name__ == "__main__":
    model = parse(MyModel)
