# Clipstick

A cli-tool based on Pydantic models.

There are many other tools out there, that do kind of the same, 
but they all didn't do quite exactly what I wanted.

The goal of clipstip is to use pydantic to model your cli by leveraging:

- The automatic casting of input variables.
- The powerful validation capabilities.
- Docstrings as cli documentation.
- No other mental model required than Typing and Pydantic.

Clipstick is inspired by [tyro](https://brentyi.github.io/tyro/). It is excellent and is more versatile than this tool. But in my opionion it's primary focus is not building a cli tool along the lines of Argparse or Click, but more on composing complex objects from the command line. Making tyro behave like a "traditional" cli tool requires additional `Annotation` flags, which I didn't want.


## Installation

`pip install clipstick`


## Example

<!-- [[[cog
import cog
contents = open("examples/simple.py").read() 

cog.outl("```python")
cog.outl("")
cog.out(contents)
cog.outl("```")
]]]> -->

<!-- [[[end]]] -->


`python examples/simple.py -h` gives you:
<!-- [[[cog
import cog
import subprocess

result = subprocess.run(['python','examples/simple.py','-h'],capture_output=True)
cog.outl("```")
cog.out(result.stdout.decode('utf-8'))
cog.outl("```")
]]]> -->

<!-- [[[end]]] -->

`python examples/simple.py alex --repeat-count 3` gives you:
<!-- [[[cog
import cog
import subprocess

result = subprocess.run(['python','examples/simple.py','alex','--repeat-count','3'],capture_output=True)
cog.outl("```")
cog.out(result.stdout.decode('utf-8'))
cog.outl("```")
]]]> -->

<!-- [[[end]]] -->

> [!INFO]
>
> The inclusion of the `def main(self)` method is not a requirement. `clipstick` generates a pydantic model based on provided cli arguments and gives it back to you for your further usage. Using `def main()` is one of the options to further process it.


## Positional arguments

All properties in your pydantic model without a default value
are converted to cli positional arguments.


<!-- [[[cog
import cog
file="examples/positional.py"

contents = open(file).read() 

cog.outl("```python")
cog.outl(contents)
cog.outl("```")
]]]> -->

<!-- [[[end]]] -->


## Keyword arguments

## Choices

## Lists

## Booleans/Flags

## Subcommands

