from typing import Annotated
from pydantic import BaseModel
from clipstick import _annotations
from clipstick._clipstick import parse
import pytest


class FlaggedModel(BaseModel):
    """A simple model. Main description."""

    add_flag: bool
    """my flag"""


class DefaultFalseFlaggedModel(BaseModel):
    """A model including an optional boolean flag."""

    my_false_flag: bool = False
    """my optional flag"""


class DefaultTrueFlaggedModel(BaseModel):
    my_true_flag: bool = True


class FlaggedModelShort(BaseModel):
    add_flag: Annotated[bool, _annotations.short("a")]


class DefaultFalseFlaggedModelShort(BaseModel):
    """A model including an optional boolean flag."""

    my_false_flag: Annotated[bool, _annotations.short("m")] = False
    """my optional flag"""


def test_parse_flagged_model():
    model = parse(FlaggedModel, ["--add-flag"])
    assert model == FlaggedModel(add_flag=True)


def test_parse_no_flagged_model():
    model = parse(FlaggedModel, ["--no-add-flag"])
    assert model == FlaggedModel(add_flag=False)


def test_parse_model_with_flag_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FlaggedModel, ["-h"])

    assert err.value.code == 0
    assert "--add-flag/--no-add-flag" in capture_output.captured_output


def test_default_false_model():
    model = parse(DefaultFalseFlaggedModel, ["--my-false-flag"])

    assert model == DefaultFalseFlaggedModel(my_false_flag=True)


def test_default_true_model():
    model = parse(DefaultTrueFlaggedModel, ["--no-my-true-flag"])

    assert model == DefaultTrueFlaggedModel(my_true_flag=False)


@pytest.mark.parametrize("args", (["--add-flag"], ["-a"]))
def test_short_hand_flag_true(args):
    model = parse(FlaggedModelShort, args)
    assert model == FlaggedModelShort(add_flag=True)


@pytest.mark.parametrize("args", (["--no-add-flag"], ["-no-a"]))
def test_short_hand_flag_false(args):
    model = parse(FlaggedModelShort, args)
    assert model == FlaggedModelShort(add_flag=False)


@pytest.mark.parametrize("args", (["--my-false-flag"], ["-m"]))
def test_short_hand_flag_default_false(args):
    model = parse(DefaultFalseFlaggedModelShort, args)
    assert model == DefaultFalseFlaggedModelShort(my_false_flag=True)


def test_default_false_model_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(DefaultFalseFlaggedModel, ["-h"])

    assert err.value.code == 0
    assert "my-false-flag" in capture_output.captured_output
    assert "--no-my-false-flag" not in capture_output.captured_output


def test_default_true_model_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(DefaultTrueFlaggedModel, ["-h"])

    assert err.value.code == 0
    assert (
        " my-true-flag" not in capture_output.captured_output
    )  # prepend it with a space to make sure it doesn't match the --no-my-true-flag
    assert "--no-my-true-flag" in capture_output.captured_output


def test_short_model_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(FlaggedModelShort, ["-h"])
    assert err.value.code == 0

    assert "-no-a/-a/--add-flag/--no-add-flag  [bool]" in capture_output.captured_output
