import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["quality", "test"]
PROJECT_FOLDER = "src"


@nox.session(python=False)
def fix_quality(session):
    """Fixes possible quality errors."""
    session.run("poetry", "install", "--sync", external=True)

    session.run("black", PROJECT_FOLDER)
    session.run("black", "tests")

    session.run("ruff", PROJECT_FOLDER, "--fix")
    session.run("ruff", "tests", "--fix")


@nox.session
def quality(session):
    session.run("poetry", "install", "--sync", external=True)

    session.run("black", PROJECT_FOLDER, "--check")
    session.run("black", "tests", "--check")

    session.run("mypy", PROJECT_FOLDER)

    session.run("ruff", PROJECT_FOLDER)


@nox.session
def test(session):
    session.run("poetry", "install", "--sync", external=True)
    session.run("pytest", "tests")


@nox.session
def build(session):
    session.run("poetry", "build", external=True)


@nox.session
def build_readme(session):
    session.run("poetry", "install", "--sync", external=True)
