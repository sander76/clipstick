from __future__ import annotations

from pydantic import ValidationError
from rich.text import Text

from clipstick import _tokens


class ClipStickError(Exception):
    """Base clipstick Exception"""

    def __init__(self, message: str | Text) -> None:
        super().__init__()
        self.message = message

    def __rich__(self) -> str | Text:
        return self.message

    def __str__(self) -> str:
        return str(self.message)


class MissingPositional(ClipStickError):
    """Raised when an incorrect number of positionals is provided."""

    def __init__(self, key: str, idx: int, values: list[str]) -> None:
        text = Text("Missing a value for positional argument:")
        text.append(key, style="orange3")
        # message = "\n".join(
        #     (
        #         "Missing a value for positional argument:",
        #         Text(key, style="orange3"),
        #         f"user entry: {' '.join(values[:idx])} [bold red]<REQUIRED: {key}>[/]",
        #     ),
        # )

        super().__init__(text)


class InvalidModel(ClipStickError):
    """Raised when your clipstick model is invalid"""


class InvalidTypesInUnion(InvalidModel):
    def __init__(self) -> None:
        super().__init__("A union composing a subcommand must all be of type BaseModel")


class NoDefaultAllowedForSubcommand(InvalidModel):
    def __init__(self) -> None:
        super().__init__("A subcommand cannot have a default value.")


class TooManySubcommands(InvalidModel):
    def __init__(self) -> None:
        super().__init__("Only one subcommand per model allowed.")


class TooManyShortsException(ClipStickError):
    def __init__(self, model, shorts: list[str]) -> None:
        super().__init__("too many shorts defined inside model")
        self._model = model
        self._shorts = shorts

    def __str__(self):
        return f"{self.message}, model={self._model}, shorts={self._shorts}"


class FieldError(ClipStickError):
    """A pydantic validation error wrapper."""

    def __init__(
        self,
        exception: ValidationError,
        token: _tokens.Command | _tokens.Subcommand,
        provided_args: list[str],
    ) -> None:
        errors = []
        for error in exception.errors():
            input = error["input"]
            error_msg = error["msg"]
            # todo: most of times I need just the fist item.
            # Have not encountered a situation where I need something else,
            # but it will need some investigating though.
            failing_field = error["loc"][0]

            # find the token by using the input value (which is the key) that is causing the exception.
            positional_token = next(
                (tk for tk in token.args if tk.key == failing_field), None
            )
            if positional_token:
                # this token relates to a positional argument.
                if isinstance(token, _tokens.Subcommand):
                    errors.append(
                        f"Incorrect value for {positional_token.user_keys[0]} in {token.user_keys[0]}. {error_msg}, value: {input}"
                    )
                else:
                    errors.append(
                        f"Incorrect value for {positional_token.user_keys[0]}. {error_msg}, value: {input}"
                    )
            else:
                optional_token = next(
                    tk for tk in token.optional_kwargs if tk.key == failing_field
                )
                if optional_token and optional_token.indices:
                    used_token = provided_args[optional_token.indices][0]
                    # do token stuff
                    if isinstance(token, _tokens.Subcommand):
                        errors.append(
                            f"Incorrect value for {used_token} in {token.user_keys[0]}. {error_msg}, value: {input}"
                        )
                    else:
                        errors.append(
                            f"Incorrect value for {used_token}. {error_msg}, value: {input}"
                        )
        super().__init__("\n".join(errors))
