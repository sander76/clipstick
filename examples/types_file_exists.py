from clipstick import parse
from pydantic import BaseModel, FilePath


class MyModel(BaseModel):
    """Model with a pydantic validator."""

    my_path: FilePath
    """provide an existing file location."""


print(parse(MyModel))
