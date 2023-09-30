from pydantic import BaseModel
from clipstick import parse


class Routes(BaseModel):
    route_name: str


class Climbers(BaseModel):
    climber_name: str


class Boulder(BaseModel):
    """The base model with a subcommand."""

    sub_command: Routes | Climbers


model = parse(Boulder, ["climbers", "Adam Ondra"])
assert model == Boulder(sub_command=Climbers(climber_name="Adam Ondra"))

model = parse(Boulder, ["routes", "Burden of Dreams"])
assert model == Boulder(sub_command=Routes(route_name="Burden of Dreams"))
