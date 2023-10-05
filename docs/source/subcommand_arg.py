from pydantic import BaseModel
from clipstick import parse


class Routes(BaseModel):
    route_name: str


class Climbers(BaseModel):
    climber_name: str


class MyModel(BaseModel):
    """The base model with a subcommand."""

    sub_command: Routes | Climbers


if __name__ == "__main__":
    model = parse(MyModel)
