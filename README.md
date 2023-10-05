# Clipstick


A cli-tool based on Pydantic models.

There are many other tools out there that do kind of the same, 
but they all don't do quite exactly what I want.

The goal of clipstip is to use pydantic to model your cli by leveraging:

- The automatic casting of input variables.
- The powerful validation capabilities.
- Docstrings as cli documentation.
- No other mental model required than Typing and Pydantic.

Clipstick is inspired by [tyro](https://brentyi.github.io/tyro/). It is excellent and is more versatile than this tool. But in my opionion its primary focus is not building a cli tool along the lines of Argparse or Click, but more on composing complex objects from the command line. Making tyro behave like a "traditional" cli requires additional `Annotation` flags, which I don't want.


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
```python

# examples/simple.py

from pydantic import BaseModel
from clipstick import parse


class SimpleModel(BaseModel):
    """A simple model demonstrating clipstick.

    This is used in help as describing the main command.
    """

    name: str
    """Your name. This is used in help describing name."""

    repeat_count: int = 10
    """How many times to repeat your name. Used in help describing repeat_count."""

    def main(self):
        for _ in range(self.repeat_count):
            print(f"hello: {self.name}")


if __name__ == "__main__":
    model = parse(SimpleModel)
    model.main()
```
<!-- [[[end]]] -->


`python examples/simple.py -h` gives you:
<!-- [[[cog
import cog
import subprocess

result = subprocess.run(['python','examples/simple.py','-h'], check=True, stdout=subprocess.PIPE)
cog.outl("```")
cog.out(result.stdout.decode('utf-8'))
cog.outl("```")
]]]> -->
```

usage: <your entrypoint here> [-h] name [['--repeat-count']]

A simple model demonstrating clipstick.

    This is used in help as describing the main command.
    

positional arguments:
    name                     Your name. This is used in help describing name. [str]

optional keyword arguments:
    --repeat-count           How many times to repeat your name. Used in help describing repeat_count. [int]
```
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
```
hello: alex
hello: alex
hello: alex
```
<!-- [[[end]]] -->

> [!NOTE]
> The inclusion of the `def main(self)` method is not a requirement. `clipstick` generates a pydantic model based on provided cli arguments and gives it back to you for your further usage. Using `def main()` is one of the options to further process it.


## Positional arguments

All properties in your pydantic model without a default value
are converted to cli positional arguments.


<!-- [[[cog
import cog

from docs.source import positional_arg as module
from docs.source import cogger

cog.outl("```python")
cog.outl(cogger.print_source(module))
cog.outl("```")
cog.outl("```python")
cog.outl(cogger.print_output(module.MyModel,['10']))
cog.outl("```")
cog.outl("```shell")
cog.outl(cogger.print_help(module.MyModel))
cog.outl("```")


]]]> -->
```python
# source/positional_arg.py

from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: int


if __name__ == "__main__":
    """your cli entrypoint"""
    model = parse(MyModel)

```
```python
# >>> python source/positional_arg.py 10
MyModel(my_value=10)
```
```shell
# >>> python source/positional_arg.py -h

usage: <your entrypoint here> [-h] my-value

None

positional arguments:
    my-value                 None [int]

```
<!-- [[[end]]] -->


## Keyword arguments

All fields with a default value are converted to cli optional arguments.

<!-- [[[cog
import cog

from docs.source import keyword_arg as module
from docs.source import cogger

cog.outl("```python")
cog.outl(cogger.print_source(module))
cog.outl("```")
cog.outl("```python")
cog.outl(cogger.print_output(module.MyModel,['--my-value','10']))
cog.outl("```")
cog.outl("```shell")
cog.outl(cogger.print_help(module.MyModel))
cog.outl("```")


]]]> -->
```python
# source/keyword_arg.py

from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    my_value: int = 22


if __name__ == "__main__":
    model = parse(MyModel)

```
```python
# >>> python source/keyword_arg.py --my-value 10
MyModel(my_value=10)
```
```shell
# >>> python source/keyword_arg.py -h

usage: <your entrypoint here> [-h] [['--my-value']]

None

optional keyword arguments:
    --my-value               None [int]

```
<!-- [[[end]]] -->

## Choices

## Lists

## Booleans/Flags

<!-- [[[cog
import cog

from docs.source import boolean_required_arg as module
from docs.source import cogger

cog.outl("```python")
cog.outl(cogger.print_source(module))
cog.outl("```")
cog.outl("```python")
cog.outl(cogger.print_output(module.MyModel,['--verbose']))
cog.outl("```")
cog.outl("```python")
cog.outl(cogger.print_output(module.MyModel,['--no-verbose']))
cog.outl("```")
cog.outl("```shell")
cog.outl(cogger.print_help(module.MyModel))
cog.outl("```")


]]]> -->
```python
# source/boolean_required_arg.py

from pydantic import BaseModel
from clipstick import parse


class MyModel(BaseModel):
    verbose: bool


if __name__ == "__main__":
    model = parse(MyModel)

```
```python
# >>> python source/boolean_required_arg.py --verbose
MyModel(verbose=True)
```
```python
# >>> python source/boolean_required_arg.py --no-verbose
MyModel(verbose=False)
```
```shell
# >>> python source/boolean_required_arg.py -h

usage: <your entrypoint here> [-h] --verbose

None

positional arguments:
    --verbose/--no-verbose   None [bool]

```
<!-- [[[end]]] -->
## Subcommands

Subcommands are possible by adding a property with a union of `BaseModel`, each defined as new path in the sub-command tree.

<!-- [[[cog
import cog

from docs.source import subcommand_arg as module
from docs.source import cogger

cog.outl("```python")
cog.outl(cogger.print_source(module))
cog.outl("```")
cog.outl("```python")
cog.outl(cogger.print_output(module.MyModel,['climbers','Ondra']))
cog.outl("```")
cog.outl("```")
cog.outl(cogger.print_help(module.MyModel))
cog.outl("```")


]]]> -->
```python
# source/subcommand_arg.py

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

```
```python
# >>> python source/subcommand_arg.py climbers Ondra
MyModel(sub_command=Climbers(climber_name='Ondra'))
```
```
# >>> python source/subcommand_arg.py -h

usage: <your entrypoint here> [-h] {routes, climbers}

The base model with a subcommand.

subcommands:
    routes                   None
    climbers                 None

```
<!-- [[[end]]] -->

- Only one subcommand per model is allowed. (If you need more (and want to follow the more object-composition path), have a look at [tyro](https://brentyi.github.io/tyro/))
- `sub_command` as a name is not required. Any name will do.
- Nesting of subcommands is possible.
