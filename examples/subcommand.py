from clipstick import parse
from pydantic import BaseModel


class Clone(BaseModel):
    """Clone a repo."""

    repo: str
    """Clone this repo."""

    def main(self):
        print(f"Cloning repo {self.repo}")


class Merge(BaseModel):
    """Merge a branch."""

    branch: str
    """Branch to merge into active branch."""

    def main(self):
        print(f"Merging {self.branch} into current branch.")


class MyGit(BaseModel):
    """My git tool."""

    sub_command: Clone | Merge  # <-- a subcommand of clone and merge

    def main(self):
        self.sub_command.main()


model = parse(MyGit)
model.main()
