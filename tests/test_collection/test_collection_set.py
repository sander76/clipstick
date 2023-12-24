import pytest
from clipstick._clipstick import parse
from pydantic import BaseModel


class MyModel(BaseModel):
    my_list: set[int]
    """A list type object"""


def test_list_args_success():
    model = parse(MyModel, ["--my-list", "10", "--my-list", "11"])

    assert model == MyModel(my_list=[10, 11])


def test_help(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(MyModel, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Arguments]

Arguments:
    --my-list            A list type object Can be applied multiple times. [set[int]]
"""
        == capture_output.captured_output
    )
