from pydantic import BaseModel
from clipstick import parse


class Rates(BaseModel):
    """Display all available rates."""

    climber_name: str
    """The name of the climber."""

    difficulty_rate: str = "6a"
    """Boulder grade"""

    def main(self):
        print(f"{self.climber_name} has climbed {self.difficulty_rate} and higher")


class Climbers(BaseModel):
    """Display climber info"""

    climber_name: str
    """The name of the climber."""

    def main(self):
        print(f"Climber {self.climber_name} has climbed 10 boulders")


class Boulder(BaseModel):
    """My Boulder database"""

    sub_command: Rates | Climbers

    def main(self):
        self.sub_command.main()


if __name__ == "__main__":
    model = parse(Boulder)
    model.main()
