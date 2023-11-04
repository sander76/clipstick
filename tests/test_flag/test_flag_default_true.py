from typing import Annotated

import pytest
from pydantic import BaseModel

from clipstick import _annotations
from clipstick._clipstick import parse


class FlagDefaultTrue(BaseModel):
    """A model with flag."""

    proceed: bool = True
    """Continue with this operation."""


def test_default_true():
    model = parse(FlagDefaultTrue, ["--no-proceed"])

    assert model == FlagDefaultTrue(proceed=False)


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FlagDefaultTrue, ["-h"])

    assert err.value.code == 0
    assert "--proceed" not in capture_output.captured_output
    assert (
        "--no-proceed         Continue with this operation. [bool] [default = True]"
        in capture_output.captured_output
    )
