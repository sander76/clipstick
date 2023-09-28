from smplcli._parse import tokenize
from smplcli._tokens import Subcommand


from pydantic import BaseModel


def parse(model: type[BaseModel], args: list[str]) -> BaseModel:
    args = ["__main_entry__"] + args
    root_node = Subcommand("__main_entry__", "__main_entry__", model)
    tokenize(model=model, sub_command=root_node)

    success, _ = root_node.match(0, args)
    if success:
        parsed = root_node.parse(args)
    else:
        raise ValueError("No matching pattern found.")
    return parsed["__main_entry__"]
