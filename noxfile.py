"""Nox sessions."""

import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox
from nox_uv import session

package = "dapla_metadata"
python_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]
nox.needs_version = ">= 2021.6.6"
nox.options.default_venv_backend = "uv"

@session(name="pre-commit", python=python_versions[-1], uv_only_groups=["dev"])
def precommit(session: nox.Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
        "--show-diff-on-failure",
    ]
    session.run("pre-commit", *args)


@session(python=python_versions[1:], uv_groups=["type_check"])
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or ["src", "tests"]
    session.run("mypy", *args)
    if not session.posargs:
        session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


@session(python=python_versions, uv_groups=["test"])
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    try:
        session.run(
            "coverage",
            "run",
            "--parallel",
            "-m",
            "pytest",
            "-o",
            "pythonpath=",
            *session.posargs,
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@session(python=python_versions[-1], uv_only_groups=["test"])
def coverage(session: nox.Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report", "--skip-empty"]
    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@session(python=python_versions[-1], uv_groups=["test"])
def typeguard(session: nox.Session) -> None:
    """Runtime type checking using Typeguard."""
    session.run("pytest", f"--typeguard-packages={package}.datasets", *session.posargs)


@session(python=python_versions[-1], uv_groups=["test"])
def xdoctest(session: nox.Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")
    session.run("python", "-m", "xdoctest", *args)


@session(name="docs-build", python=python_versions[-1], uv_groups=["docs"], default=False)
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "docs/_build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")
    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@session(python=python_versions[-1], uv_only_groups=["docs"], default=False)
def docs(session: nox.Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]
    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)
