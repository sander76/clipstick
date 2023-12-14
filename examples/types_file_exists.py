from clipstick import parse
from pydantic import BaseModel, FilePath


class MyModel(BaseModel):
    my_path: FilePath
    """provide an existing file location."""


print(parse(MyModel))
