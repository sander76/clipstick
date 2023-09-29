# Clipstick

A cli-tool based on Pydantic models.

There are many other tools out there, that do kind of the same, 
but they all didn't do quite exactly what I wanted.

The goal of clipstip is to use pydantic to model your cli by leveraging:

- The automatic casting of input variables.
- The powerful validation capabilities.
- Docstrings as cli documentation

## Installation

`pip install clipstick`


## Example

<!-- [[[cog
import cog
contents = open("examples/simple.py").read() 

cog.outl("```python")
cog.outl("# examples/simple.py")
cog.outl("")
cog.out(contents)
cog.outl("```")
]]]> -->
```python
# examples/simple.py

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
```
<!-- [[[end]]] -->


running the above `python examples/simple.py -h` gives you:
<!-- [[[cog
import cog
import subprocess

result = subprocess.run(['python','examples/simple.py','-h'],capture_output=True)
cog.outl("```")
cog.out(result.stdout.decode('utf-8'))
cog.outl("```")
]]]> -->
```
A simple model demonstrating clipstick.

positional args:
name :   Your name
optional keyword arguments:
--repeat-count :  How many times to repeat your name.
```
<!-- [[[end]]] -->

running the above `python examples/simple.py alex --repeat-count 3` gives you:
<!-- [[[cog
import cog
import subprocess

result = subprocess.run(['python','examples/simple.py','alex','--repeat-count','3'],capture_output=True)
cog.outl("```")
cog.out(result.stdout.decode('utf-8'))
cog.outl("```")
]]]> -->
```
hello: alex
hello: alex
hello: alex
```
<!-- [[[end]]] -->
