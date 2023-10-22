"""Clipstick works with plain pydantic models.

Some constraints apply though. These constraints are tested here.
"""
from typing import Annotated
from pydantic import BaseModel
from clipstick._annotations import short
from clipstick._parse import _validate_shorts
from clipstick import parse
import pytest
from clipstick._exceptions import (
    TooManyShortsException,
    TooManySubcommands,
    InvalidTypesInUnion,
    NoDefaultAllowedForSubcommand,
)


class Model_1(BaseModel):
    val: Annotated[str, short("v")]
    val_1: Annotated[str, short("v")]


class Model_2(BaseModel):
    sub_model: Model_1


class Model_3(BaseModel):
    sub_command: Model_2 | Model_1


@pytest.mark.parametrize("model", [Model_1, Model_2, Model_3])
def test_validate_shorts_fail(model):
    with pytest.raises(TooManyShortsException):
        _validate_shorts(model)


def test_shorts_fail_error_message(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(Model_1, ["-h"])

    assert err.value.code == 1
    assert "too many shorts defined inside model" in capture_output.captured_output


class Model_4(BaseModel):
    val_1: int


class Model_5(BaseModel):
    val_2: str


class Model_6(BaseModel):
    sub_command: Model_4 | Model_5
    one_sub_command_too_many: Model_4 | Model_5


def test_multiple_subcommands(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(Model_6, ["-h"])

    assert err.value.code == 1
    assert "Only one subcommand per model allowed." in capture_output.captured_output


class Model_7(BaseModel):
    invalid_type_in_union: Model_4 | int


def test_invalid_subcommand_composition(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(Model_7, ["-h"])

    assert err.value.code == 1
    assert (
        "A union composing a subcommand must all be of type BaseModel"
        in capture_output.captured_output
    )


class Model_8(BaseModel):
    no_default_allowed: Model_4 | Model_5 = Model_4(val_1=10)


def test_no_default_allowed(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(Model_8, ["-h"])

    assert err.value.code == 1
    assert "A subcommand cannot have a default value." in capture_output.captured_output
