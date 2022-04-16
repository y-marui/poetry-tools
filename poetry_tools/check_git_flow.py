"""check_git_flow: Check compatibility with git-flow."""
import subprocess
import warnings

import click
from pre_commit_hooks.no_commit_to_branch import is_on_branch
from pre_commit_hooks.util import cmd_output


def _get_version_poetry():
    return cmd_output('poetry', 'version', '-s').strip()


def _get_full_peotry():
    ref_name = cmd_output('poetry', 'version')
    repo_name, version_poetry = ref_name.strip().split()
    repo_name = repo_name.replace("-", "_")
    return repo_name, version_poetry


def _check_git_flow() -> int:
    """Check compatibility with git-flow.

    Check version from package and poetry match.
    Retruns exit code instead of raise Errors.

    If branch is `main` or `master`,
    * run `pytest`

    If branch is `hotfix/.*` or `release/.*`,
    * check version from branch and poetry match
    * check version from changelog and poetry match

    priority of version
    branch > poetry > package > markdown
    """
    code = 0

    # branch > poetry
    if is_on_branch(["main", "master"], []):
        code = code or _check_pytest()
    elif is_on_branch([], ["hotfix/.*", "release/.*"]):
        code = code or _check_version_branch()
        code = code or _check_version_md()

    # poetry > package
    code = code or _check_version_package()

    return code


def _check_pytest() -> int:
    res = subprocess.run(["poetry", "run", "pytest"])
    return res.returncode


def _check_version_package() -> int:
    repo_name, version_poetry = _get_full_peotry()

    version_package = cmd_output(
        "poetry",
        "run",
        "python",
        "-c",
        f"import {repo_name}; print({repo_name}.__version__)"
    ).strip()
    if version_package != version_poetry:
        warnings.warn(
            f"Package returns `{version_package}` "
            f"but Poetry returns `{version_poetry}`"
        )
        subprocess.run(["bump2version",
                        "--current-version",
                        f"{version_package}",
                        "--new-version",
                        f"{version_poetry}",
                        "--allow-dirty",
                        "patch",
                        f"{repo_name}/__init__.py"])
        return 1
    else:
        return 0


def _check_version_branch() -> int:
    version_poetry = _get_version_poetry()

    ref_name = cmd_output('git', 'symbolic-ref', 'HEAD')
    chunks = ref_name.strip().split('/')
    version_branch = '/'.join(chunks[3:])

    if version_branch != version_poetry:
        warnings.warn(
            f"Git flow work on `{version_branch}` "
            f"but Poetry returns `{version_poetry}`"
        )
        subprocess.run(["poetry", "version", f"{version_branch}"])
        return 1
    else:
        return 0


def _check_version_md() -> int:
    version_poetry = _get_version_poetry()

    with open("CHANGELOG.md") as fp:
        fp.readline()
        ref_name = fp.readline()
        _, version_md, *_ = ref_name.strip().split()

    if version_md != version_poetry:
        warnings.warn(
            f"CHANGELOG.md returns `{version_md}` "
            f"but Poetry returns `{version_poetry}`"
        )
        return 1
    else:
        return 0


@click.command()
def check_git_flow():
    """Check compatibility with git-flow.

    Check version from package and poetry match.

    If branch is `main` or `master`,
    * run `pytest`

    If branch is `hotfix/.*` or `release/.*`,
    * check version from branch and poetry match
    * check version from changelog and poetry match
    """
    raise SystemExit(_check_git_flow())


if __name__ == '__main__':
    check_git_flow()
