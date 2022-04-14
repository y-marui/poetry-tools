import subprocess
from pathlib import Path

import click
import toml
from click_default_group import DefaultGroup

from .check_git_flow import check_git_flow as git_flow


def get_repo_name():
    path = Path("pyproject.toml")
    if not path.exists():
        raise FileNotFoundError(f"`{path}` not found.")

    with path.open("r") as fp:
        data = toml.load(fp)

        repo_name = data["tool"]["poetry"]["name"]

    return repo_name


def get_disp_name():
    path = Path("README.md")
    if not path.exists():
        raise FileNotFoundError(f"`{path}` not found.")

    with path.open("r") as fp:
        data = fp.readline()

        disp_name = data[2:].strip()

    return disp_name


@click.group(cls=DefaultGroup, default="install", default_if_no_args=True)
def cli():
    print("Start cli")
    pass


@cli.command()
def install():
    print("Start install")

    repo_name = get_repo_name()
    disp_name = get_disp_name()

    res = input(f"Continue install `{repo_name}` as `{disp_name}`? [y/n]:")
    if res.strip() != "y":
        return

    subprocess.run([
        "poetry",
        "install"
    ])
    subprocess.run([
        "poetry",
        "add",
        "-D",
        "ipykernel"
    ])

    pwd = Path(".").absolute()

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
        f"${{PYTHONPATH}}:{pwd}"
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
    path = Path(".venv")
    if not path.exists():
        raise FileNotFoundError("Poetry is not installed.")

    repo_name = get_repo_name()

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
        "rm",
        "-rf",
        ".venv"
    ])


cli.add_command(git_flow, name="git_flow")
