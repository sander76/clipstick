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
