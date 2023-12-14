from clipstick import parse
from pydantic import BaseModel


class MyName(BaseModel):
    """What is my name.

    In case you forgot I will repeat it x times.
    """

    name: str
    """Your name."""

    age: int = 24
    """Your age."""

    repeat_count: int = 10
    """How many times to repeat your name."""

    def main(self):
        for _ in range(self.repeat_count):
            print(f"Hello: {self.name}. You are {self.age} years old.")


if __name__ == "__main__":
    model = parse(MyName)
    model.main()
