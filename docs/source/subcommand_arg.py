from pydantic import BaseModel
from clipstick import parse


class Routes(BaseModel):
    """Some climbing routes."""

    route_name: str
    """Name of a route."""


class Climbers(BaseModel):
    """Climbers model."""

    climber_name: str
    """Name of a climber."""


class MyModel(BaseModel):
    """The base model with a subcommand."""

    sub_command: Routes | Climbers


if __name__ == "__main__":
    model = parse(MyModel)
