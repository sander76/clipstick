from pydantic import BaseModel
from clipstick import parse


class SimpleModel(BaseModel):
    """A simple model demonstrating clipstick."""

    name: str
    """Your name"""

    repeat_count: int = 10
    """How many times to repeat your name."""

    def main(self):
        for _ in range(self.repeat_count):
            print(f"hello: {self.name}")


if __name__ == "__main__":
    model = parse(SimpleModel)
    model.main()
