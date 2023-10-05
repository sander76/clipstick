from pydantic import BaseModel

from clipstick._clipstick import parse


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


def test_parse_flagged_model():
    model = parse(FlaggedModel, ["--add-flag"])
    assert model == FlaggedModel(add_flag=True)


def test_parse_no_flagged_model():
    model = parse(FlaggedModel, ["--no-add-flag"])
    assert model == FlaggedModel(add_flag=False)


def test_parse_model_with_flag_help(capture_output):
    out = capture_output(FlaggedModel, ["-h"])

    assert "--add-flag/--no-add-flag" in out


def test_default_false_model():
    model = parse(DefaultFalseFlaggedModel, ["--my-false-flag"])

    assert model == DefaultFalseFlaggedModel(my_false_flag=True)


def test_default_false_model_help(capture_output):
    out = capture_output(DefaultFalseFlaggedModel, ["-h"])

    assert "my-false-flag" in out
    assert "--no-my-false-flag" not in out


def test_default_true_model():
    model = parse(DefaultTrueFlaggedModel, ["--no-my-false-flag"])

    assert model == DefaultTrueFlaggedModel(my_false_flag=False)


def test_default_true_model_help(capture_output):
    out = capture_output(DefaultTrueFlaggedModel, ["-h"])

    assert (
        " my-true-flag" not in out
    )  # prepend it with a space to make sure it doesn't match the --no-my-true-flag
    assert "--no-my-true-flag" in out
