![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/sander76/a25f1e6bfcb3b085ffe05f520b56e43c/raw/covbadge.json)

# Clipstick
<!-- begin index -->

Create your cli using Pydantic models

Define a pydantic model as you would normally do, pass it to clipstick and you get a cli including subcommands, nice docstrings and validations based on typing and pydantic validators.

## Why?

There are many other tools out there that do kind of the same, 
but they all don't do quite exactly what I want.

The goal of clipstip is to use pydantic to model your cli by leveraging:

- The automatic casting of input variables.
- The powerful validation capabilities.
- Docstrings as cli documentation.
- No other mental model required than Typing and Pydantic.

Clipstick is inspired by [tyro](https://brentyi.github.io/tyro/), which is excellent and more versatile than this tool. But in my opionion its primary focus is not building a cli tool along the lines of Argparse or Click but more on composing complex objects from the command line. Making tyro behave like a "traditional" cli requires additional `Annotation` flags, which I don't want.

Some other similar tools don't support pydantic v2, so I decided to create my own. Next to that I wanted to try and build my own parser instead of using `Argparse` because... why not.

## Installation

`pip install clipstick`


## Example

Create a pydantic model as you would normally do.

```python
from pydantic import BaseModel

from clipstick import parse


class MyName(BaseModel):
    """What is my name.

    In case you forgot I will repeat it x times.
    """

    name: str
    """Your name."""

    age: int = 24
    """Your age"""

    repeat_count: int = 10
    """How many times to repeat your name."""

    def main(self):
        for _ in range(self.repeat_count):
            print(f"Hello: {self.name}, you are {self.age} years old")


if __name__ == "__main__":
    model = parse(MyName)
    model.main()

```

That's it. The clipstick parser will convert this into a command line interface based on the properties assigned to the model, the provided typing and docstrings.

So `python examples/name.py -h` gives you nicely formatted (and colored) output:

![help_output](https://raw.githubusercontent.com/sander76/clipstick/main/docs/_images/name-help.svg)

And use your cli `python examples/name.py superman --repeat-count 4`:

![usage output](https://raw.githubusercontent.com/sander76/clipstick/main/docs/_images/name-output.svg)

The provided annotations define the type to which your arguments need to be converted.
If you provide a value which cannot be converted you will be presented with a nice error:

`python examples/name.py superman --age too-old`

![wrong age](https://raw.githubusercontent.com/sander76/clipstick/main/docs/_images/name-wrong-age.svg)

> The inclusion of the `def main(self)` method is not a requirement. `clipstick` generates a pydantic model based on provided cli arguments and gives it back to you for your further usage. Using `def main()` is one of the options to further process it.

<!-- end index -->

For more information visit the [documentation](https://sander76.github.io/clipstick/index.html)
