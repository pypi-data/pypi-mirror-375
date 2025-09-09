import nox

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
nox.options.sessions = ["tests", "lint", "type_check", "docs"]

nox.options.default_venv_backend = "uv"


def install_dev_dependencies(session: nox.Session) -> None:
    """Helper function to install dev dependencies."""
    session.install("--group", "dev", ".")


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    install_dev_dependencies(session)
    session.run(
        "pytest",
        "--cov=synthbiodata",
        "--cov-report=term-missing",
        *session.posargs,
    )


@nox.session(python=PYTHON_VERSIONS)
def lint(session: nox.Session) -> None:
    """Run the linter."""
    install_dev_dependencies(session)
    session.run("ruff", "check", "src", "tests", "noxfile.py")


@nox.session(python=PYTHON_VERSIONS)
def type_check(session: nox.Session) -> None:
    """Type-check using ty."""
    install_dev_dependencies(session)
    session.run("ty", "check", "src", "tests", "noxfile.py")


@nox.session(python=PYTHON_VERSIONS)
def docs(session: nox.Session) -> None:
    """Build and check documentation with MkDocs."""
    session.install("--group", "docs", ".")
    session.run("mkdocs", "build", "--strict")