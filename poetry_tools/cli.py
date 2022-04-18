"""CLI commands."""
import subprocess
from pathlib import Path

import click
import toml
from click_default_group import DefaultGroup
from click_help_colors import HelpColorsGroup

from .check_git_flow import check_git_flow as git_flow


class Custum(DefaultGroup, HelpColorsGroup):
    """Combination of `DefaultGroup` and `HelpColorsGroup`."""

    def __init__(self,
                 *args,
                 default_if_no_args: bool = None,
                 help_headers_color: str = None,
                 help_options_color: str = None,
                 options_custom_colors: str = None,
                 **kwargs):
        """Combine of `DefaultGroup` and `HelpColorsGroup`.

        Parameters
        ----------
        default_if_no_args : bool, optional
            resolves to the default command if no arguments passed.,
            by default None
        help_headers_color : str, optional
            `help_headers_color`, by default None
        help_options_color : str, optional
            `help_options_color`, by default None
        options_custom_colors : str, optional
            `options_custom_colors`, by default None
        """
        super(Custum, self).__init__(
            *args,
            default_if_no_args=default_if_no_args,
            **kwargs)
        super(HelpColorsGroup, self).__init__(
            *args,
            help_headers_color=help_headers_color,
            help_options_color=help_options_color,
            options_custom_colors=options_custom_colors,
            **kwargs)


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


@click.group(cls=Custum,
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
