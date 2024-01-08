from clipstick import parse
from pydantic import BaseModel


class Clone(BaseModel):
    """Clone a repo.

    This is a subcommand.
    """

    repo: str
    """Clone this repo."""

    def main(self):
        """Run when this subcommand is choosen."""
        print(f"Cloning repo {self.repo}")


class Merge(BaseModel):
    """Merge a branch.

    Provide a branch and merge it into your active branch.
    """

    branch: str
    """Branch name."""

    def main(self):
        """Run when this subcommand is choosen."""
        print(f"Merging {self.branch} into current branch.")


class MyGit(BaseModel):
    """My git tool."""

    sub_command: Clone | Merge  # <-- a subcommand of clone and merge

    def main(self):
        """Main entrypoint for this cli."""
        self.sub_command.main()


model = parse(MyGit)
model.main()
