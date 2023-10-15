from __future__ import annotations
from pydantic import ValidationError
from clipstick import _tokens

# if TYPE_CHECKING:
#     from clipstick._tokens import Command, Subcommand


class ClipStickError(Exception):
    """Base clipstick Exception"""

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message


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
        super().__init__("A pydantic validation wrapper")
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
        self.errors = errors

    def __str__(self) -> str:
        return "\n".join(self.errors)
