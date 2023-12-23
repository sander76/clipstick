import pytest
from clipstick import _clipstick
from pydantic import BaseModel


class SimpleModel(BaseModel):
    """A simple model. Main description."""

    my_name: str
    """A snake cased argument."""


@pytest.mark.parametrize("entrypoint", ["/test/my-app", "\\test\\my-app", "my-app"])
def test_command_name(entrypoint, monkeypatch, capture_output):
    monkeypatch.setattr(_clipstick, "DUMMY_ENTRY_POINT", entrypoint)

    with pytest.raises(SystemExit):
        capture_output(SimpleModel, ["-h"])

    assert "Usage: my-app [Arguments]" in capture_output.captured_output
