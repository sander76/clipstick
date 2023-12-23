# examples/simple.py

from clipstick import parse
from pydantic import BaseModel


class SimpleModel(BaseModel):
    """A simple model demonstrating clipstick.

    This docstring is used as the help output of the cli.
    """

    name: str
    """Your name. This is used in help describing name."""

    repeat_count: int = 10
    """How many times to repeat your name. Used in help describing repeat_count."""

    def main(self):
        """Main entrypoint for this cli."""
        for _ in range(self.repeat_count):
            print(f"hello: {self.name}")


if __name__ == "__main__":
    model = parse(SimpleModel)
    model.main()
