from typing import Annotated

import pytest
from clipstick import short
from clipstick._clipstick import parse
from pydantic import BaseModel


class FlagShort(BaseModel):
    """Model with a flag with shorthand"""

    proceed: Annotated[bool, short("p")]
    """Continue with this operation."""


@pytest.mark.parametrize("args", (["--proceed"], ["-p"]))
def test_short_hand_flag_true(args):
    model = parse(FlagShort, args)
    assert model == FlagShort(proceed=True)


@pytest.mark.parametrize("args", (["--no-proceed"], ["-no-p"]))
def test_short_hand_flag_false(args):
    model = parse(FlagShort, args)
    assert model == FlagShort(proceed=False)


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FlagShort, ["-h"])
    assert err.value.code == 0

    assert (
        """
Usage: my-cli-app [Arguments]

Model with a flag with shorthand

Arguments:
    -p/-no-p --proceed/--no-proceed Continue with this operation. [bool]
"""
        == capture_output.captured_output
    )
