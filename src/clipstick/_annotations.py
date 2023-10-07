from dataclasses import dataclass


@dataclass(frozen=True)
class Short:
    short: str


def short(name: str) -> Short:
    """Add a short-hand name to the full argument name.

    Args:
        name: The name of the short-hand name. Provide just the letter. not the preceding dash.

    Returns:
        A Short marker inside a type annotation.
    """
    return Short(name)
