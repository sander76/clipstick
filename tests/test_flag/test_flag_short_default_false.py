from typing import Annotated

import pytest
from clipstick import _annotations
from clipstick._clipstick import parse
from pydantic import BaseModel


class FlagShortDefaultFalse(BaseModel):
    """A model including an optional boolean flag."""

    proceed: Annotated[bool, _annotations.short("m")] = False
    """my optional flag"""


@pytest.mark.parametrize("args", (["--proceed"], ["-m"]))
def test_short_hand_flag_default_false(args):
    model = parse(FlagShortDefaultFalse, args)
    assert model == FlagShortDefaultFalse(proceed=True)


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FlagShortDefaultFalse, ["-h"])
    assert err.value.code == 0

    assert (
        """
Usage: my-cli-app [Options]

A model including an optional boolean flag.

Options:
    -m --proceed         my optional flag [bool] [default = False]
"""
        == capture_output.captured_output
    )
