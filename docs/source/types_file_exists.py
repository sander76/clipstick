from pydantic import BaseModel, FilePath
from clipstick import parse


class MyModel(BaseModel):
    my_path: FilePath
    """provide an existing file location."""


if __name__ == "__main__":
    model = parse(MyModel)
