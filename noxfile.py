from pathlib import Path

import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["fix_quality", "quality", "test", "check_version"]
PROJECT_FOLDER = "src"


@nox.session(python=False)
def fix_quality(session):
    """Fixes possible quality errors."""
    session.run("poetry", "install", "--sync", external=True)

    session.run("black", PROJECT_FOLDER)
    session.run("black", "tests")
    session.run("black", "docs")
    session.run("black", "examples")

    session.run("ruff", PROJECT_FOLDER, "--fix")
    session.run("ruff", "tests", "--fix")
    session.run("ruff", "docs", "--fix")
    session.run("ruff", "examples", "--fix")


@nox.session
def quality(session):
    session.run("poetry", "install", "--sync", external=True)

    session.run("black", PROJECT_FOLDER, "--check")
    session.run("black", "tests", "--check")

    session.run("mypy", PROJECT_FOLDER)

    session.run("ruff", PROJECT_FOLDER)


@nox.session
@nox.parametrize("python", ["3.10", "3.11"])
def test(session, python):
    session.run("poetry", "install", "--sync", external=True)
    if python == "3.11":
        session.run("coverage", "run", "--source", "src/clipstick", "-m", "pytest")
        session.run("coverage", "json")
    else:
        session.run("pytest", "tests")


@nox.session
def build(session):
    session.run("poetry", "build", external=True)


@nox.session
def build_docs(session):
    session.run("poetry", "install", "--sync", external=True)
    session.run("python", "tools/cogger.py")
    session.run("sphinx-build", "docs", "_build")


@nox.session(python=False)
def check_version(session: nox.Session):
    """check whether the version in this branch is newer than the latest tagged version."""
    session.run("pip", "install", "packaging")

    from packaging.version import Version

    branch_version = Version(
        session.run("poetry", "version", "--short", external=True, silent=True)
    )

    # get the released version by checking tags.
    released_version = session.run(
        "git", "tag", "--list", "--sort=taggerdate", "v*", external=True, silent=True
    )
    latest = Version(released_version.strip().split("\n")[-1])

    print("actual version", branch_version)
    print("tagged version", latest)
    if branch_version <= latest:
        session.error("version not latest")

    # check whether this new version string exists inside the CHANGELOG.md
    change_log = Path("CHANGELOG.md").read_text(encoding="utf-8")
    if str(branch_version) not in change_log:
        session.error(f"missing an entry in the CHANGELOG for version {branch_version}")
