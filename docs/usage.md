# Usage

## General

Crafting your cli is identical to composing a pydantic class. Toghether with some assumptions this is enough to create a fully working cli tool:


## Positional arguments

All fields in your pydantic model *without* a default value are converted to cli positional arguments.

```{literalinclude} ../examples/positional.py
:emphasize-lines: 8
```

A positional argument is required. If you don't provide it an error will be raised. So running this without any arguments will result in the following error message:

![missing argument](_images/positional-error.svg)

### Help output:

![positional help](_images/positional-help.svg)



## Keyword arguments

All fields in your model *with* a default value are converted to cli optional arguments.

```{literalinclude} ../examples/keyword.py
```


### Help output:

![positional with short](_images/keyword-help.svg)

## Choices

A contraint set of values for a certain argument is defined by using the `Literal` annotation.

```{literalinclude} ../examples/choice.py
```

Failing to provide a valid value gives you the error:

![wrong choice](_images/choice-wrong-choice.svg)

### Help output:

![choice argument](_images/choice-help.svg)


## Booleans/Flags

A flag (true/false) is defined by the `bool` annotation.

```{literalinclude} ../examples/boolean.py

```

### Help output:

![boolean help](_images/boolean-help.svg)

## Collections

A collection (a list of ints or string) is defined providing a keyworded argument multiple times.

```{literalinclude} ../examples/collection.py
```

### example

![collection usage](_images/collection-required.svg)

![collection usage](_images/collection-optional.svg)

### help output
![collection help](_images/collection-help.svg)

(subcommands)=
## Subcommands

Bigger cli applications will need the use of subcommands.
A probably well known example of this is the git cli which has `git clone ...`, `git merge ...` etc.
A subcommand is implemented by using pydantic models annotated with a `Union`:

```{literalinclude} ../examples/subcommand.py
:emphasize-lines: 36
```

### Help output

Clipstick assumes you are using google docstring (or any other docstring) convention
which follows these rules for class docstrings:

- The first line is used as a summary description what the class is all about.
- The rest of the lines contain a more detailed description.

With the above docstring of the `Merge` class in mind
see only the first line of the docstring being used for the `merge` subcommand:
![subcommand help](_images/subcommand-help.svg)

And observe the full docstring when printing out help for the `merge` subcommand:
![subcommand sub help](_images/subcommand-merge-help.svg)


### Points of attention

When using subcommands, be aware of the following:

- Only one subcommand per model is allowed. (If you need more (and want to follow the more object-composition path), have a look at [tyro](https://brentyi.github.io/tyro/))
- A subcommand cannot have a default: It needs to always be provided by the user.
- `sub_command` as a name is not required. Any name will do.
- Nesting of subcommands is possible.



## Validators

Pydantic provides many field validators which can be used in clipstick too.

For example a cli which requires you to provide your age which can (obviously) not be negative:

```{literalinclude} ../examples/types_non_negative_int.py
:emphasize-lines: 8
```

When you do provide a negative value, Pydantic raises an error which is picked up by clipstick and presented to the user.

![invalid negative](_images/types_non_negative_int-invalid.svg)

Another example would be a cli which needs a reference to an *existing* file location.

```{literalinclude} ../examples/types_file_exists.py
:emphasize-lines: 8
```

Failing to provide a valid file location gives you:

![invalid file](_images/types_file_exists-invalid.svg)

There are many more out-of-the-box validators available. Have a look [here](https://docs.pydantic.dev/latest/api/types/)
It is also pretty easy to write your own validators.

### Restrictions

While most of the model definitions will just work, some don't and some work better than others:

- A nesting of Models (a field inside a pydantic object which has a type of a pydantic object) is not allowed unless it is used in a `Union` as described in [](subcommands).
- Restrict the usage of `Unions` to using a `type` and a `NoneType` where `None` is the default value of a field:

    ```python
    class MyModel(BaseModel)
        my_value: int | None = None # <-- Union with a None. Omitted in help output
    ```

    ```python
    class MyModel(BaseModel)
        my_value: int | str # <-- Not allowed. Doesn't make sense of having a model like this?
    ```
