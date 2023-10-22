import ast
import inspect
from pydantic import BaseModel


def set_undefined_field_descriptions_from_var_docstrings(
    model: type[BaseModel],
) -> None:
    module = ast.parse(inspect.getsource(model))
    assert isinstance(module, ast.Module)
    class_def = module.body[0]
    assert isinstance(class_def, ast.ClassDef)
    if len(class_def.body) < 2:
        return

    for last, node in zip(class_def.body, class_def.body[1:]):
        if not (
            isinstance(last, ast.AnnAssign)
            and isinstance(last.target, ast.Name)
            and isinstance(node, ast.Expr)
        ):
            continue

        info = model.model_fields[last.target.id]
        if info.description is not None:
            continue

        doc_node = node.value
        if isinstance(doc_node, ast.Constant):
            docstring = doc_node.value  # 'regular' variable doc string
        else:
            raise NotImplementedError(doc_node)  # pragma: nocover

        info.description = docstring
