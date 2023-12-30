import pytest
from clipstick import parse
from pydantic import BaseModel


class Info(BaseModel):
    """Show information about this repo"""

    verbose: bool = True


class Clone(BaseModel):
    """Clone a repo."""

    depth: int


class Remote(BaseModel):
    """Clone a git repository."""

    url: str = "https://mysuperrepo"
    """Url of the git repo."""

    sub_command: Clone | Info


class Merge(BaseModel):
    """Git merge command."""

    branch: str
    """Git branch to merge into current branch."""


class MyGitModel(BaseModel):
    """My custom git cli."""

    sub_command: Remote | Merge


def test_deeply_nested_model_nest_1():
    model = parse(MyGitModel, ["remote", "info", "--no-verbose"])
    assert model == MyGitModel(sub_command=Remote(sub_command=Info(verbose=False)))


def test_deeply_nested_model_nest_2():
    model = parse(MyGitModel, ["remote", "clone", "11"])
    assert model == MyGitModel(sub_command=Remote(sub_command=Clone(depth=11)))


def test_deeply_nested_model_nest_3():
    model = parse(MyGitModel, ["merge", "my_working_branch"])
    assert model == MyGitModel(sub_command=Merge(branch="my_working_branch"))


def test_model_help_first_level(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(MyGitModel, ["-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app [Subcommands]

My custom git cli.

Subcommands:
    remote               Clone a git repository.
    merge                Git merge command.     
"""
        == capture_output.captured_output
    )


def test_model_help_second_level(capture_output):
    with pytest.raises(SystemExit) as err:
        capture_output(MyGitModel, ["remote", "-h"])

    assert err.value.code == 0
    assert (
        """
Usage: my-cli-app remote [Options] [Subcommands]

Clone a git repository.

Options:
    --url                Url of the git repo. [str] [default = https://mysuperrepo]

Subcommands:
    clone                Clone a repo.                   
    info                 Show information about this repo
"""
        == capture_output.captured_output
    )
