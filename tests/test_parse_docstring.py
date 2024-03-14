from typing import Annotated
import pytest
from clipstick._docstring import set_undefined_field_descriptions_from_var_docstrings
from pydantic import BaseModel, Field


class GlobalModel(BaseModel):
    my_value_docstring: str
    """Docstring for my_value."""

    my_value_annotation: str = Field(description="Description for my_value.")


class SomeClass:
    class ModelInClass(BaseModel):
        my_value_docstring: str
        """Docstring for my_value."""

        my_value_annotation: str = Field(description="Description for my_value.")


def some_function():
    class ModelInFunction(BaseModel):
        my_value_docstring: str
        """Docstring for my_value."""

        my_value_annotation: str = Field(description="Description for my_value.")

    return ModelInFunction


@pytest.mark.parametrize(
    "model", [GlobalModel, SomeClass.ModelInClass, some_function()]
)
def test_set_field_descriptions_for_var_docstrings(model: type[BaseModel]):
    set_undefined_field_descriptions_from_var_docstrings(model)
    assert (
        model.model_fields["my_value_docstring"].description
        == "Docstring for my_value."
    )
    assert (
        model.model_fields["my_value_annotation"].description
        == "Description for my_value."
    )
