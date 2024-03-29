"""CLI commands."""
import os
import subprocess
from pathlib import Path

import click
import toml
from click_default_group_colors import DefaultGroupColors

from .check_git_flow import check_git_flow as git_flow


def _get_repo_name():
    path = Path("pyproject.toml")
    if not path.exists():
        raise FileNotFoundError(f"`{path}` not found.")

    with path.open("r") as fp:
        data = toml.load(fp)

        repo_name = data["tool"]["poetry"]["name"]

    return repo_name


def _get_disp_name():
    path = Path("README.md")
    if not path.exists():
        raise FileNotFoundError(f"`{path}` not found.")

    with path.open("r") as fp:
        data = fp.readline()

        disp_name = data[2:].strip()

    return disp_name


@click.group(cls=DefaultGroupColors,
             default_if_no_args=True,
             help_headers_color='yellow',
             help_options_color='green')
def cli():
    """Excute CLI."""
    pass


@cli.command(default=True)
def install():
    """Install Poetry."""
    repo_name = _get_repo_name()
    disp_name = _get_disp_name()

    res = input(f"Continue install `{repo_name}` as `{disp_name}`? [y/n]:")
    if res.strip() != "y":
        return

    subprocess.run([
        "poetry",
        "install"
    ])
    subprocess.run([
        "pre-commit",
        "install"
    ])
    subprocess.run([
        "poetry",
        "add",
        "-D",
        "ipykernel",
        "pytest"
    ])

    pwd = Path(".").absolute()
    sep = os.pathsep

    res = subprocess.run([
        "poetry",
        "run",
        "ipython",
        "kernel",
        "install",
        "--user",
        f"--name={repo_name}",
        f"--display-name={disp_name}",
        "--env",
        "PYTHONPATH",
        f"${{PYTHONPATH}}{sep}{pwd}"
    ], capture_output=True)

    print(res.stderr.decode())


@cli.command("list")
def _list():
    subprocess.run([
        "jupyter",
        "kernelspec",
        "list",
        "--json"
    ])


@cli.command()
def uninstall():
    """Uninstall Poetry."""
    path = Path(".venv")
    if not path.exists():
        raise FileNotFoundError("Poetry is not installed.")

    repo_name = _get_repo_name()

    subprocess.run([
        "jupyter",
        "kernelspec",
        "uninstall",
        f"{repo_name}"
    ])

    res = input("Uninstall poetry from `{repo_name}`? [y/n]:")
    if res.strip() != "y":
        return

    subprocess.run([
        "pre-commit",
        "uninstall"
    ])

    subprocess.run([
        "rm",
        "-rf",
        ".venv"
    ])


cli.add_command(git_flow, name="git_flow")
