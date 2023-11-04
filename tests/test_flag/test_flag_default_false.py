from typing import Annotated

import pytest
from clipstick import _annotations
from clipstick._clipstick import parse
from pydantic import BaseModel


class FlagDefaultFalse(BaseModel):
    """A model with flag."""

    proceed: bool = False
    """continue with this operation."""


def test_default_false_model():
    model = parse(FlagDefaultFalse, ["--proceed"])

    assert model == FlagDefaultFalse(proceed=True)


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FlagDefaultFalse, ["-h"])

    assert err.value.code == 0
    assert (
        "--proceed            continue with this operation. [bool] [default = False]"
        in capture_output.captured_output
    )
    assert "--no-proceed" not in capture_output.captured_output
