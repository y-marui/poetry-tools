"""check_git_flow: Check compatibility with git-flow."""
import subprocess

import click
from pre_commit_hooks.no_commit_to_branch import is_on_branch
from pre_commit_hooks.util import cmd_output


def _check_git_flow() -> int:
    """Check compatibility with git-flow.

    Check version from package and poetry match.
    Retruns exit code instead of raise Errors.

    If branch is `main` or `master`,
    * run `pytest`

    If branch is `hotfix/.*` or `release/.*`,
    * check version from branch and poetry match
    * check version from changelog and poetry match
    """
    ref_name = cmd_output('poetry', 'version')
    reponame, version_poetry = ref_name.strip().split()
    reponame = reponame.replace("-", "_")
    version_package = cmd_output(
        "python",
        "-c",
        f"import {reponame}; print({reponame}.__version__)"
    ).strip()
    if version_package != version_poetry:
        print(
            f"Package returns `{version_package}` "
            f"but Poetry returns `{version_poetry}`"
        )
        return 1

    # Special Cases
    if is_on_branch(["main", "master"], []):
        res = subprocess.run(["poetry", "run", "pytest"])
        return res.returncode

    elif is_on_branch([], ["hotfix/.*", "release/.*"]):
        ref_name = cmd_output('git', 'symbolic-ref', 'HEAD')
        chunks = ref_name.strip().split('/')
        version_git_flow = '/'.join(chunks[3:])

        if version_git_flow != version_poetry:
            print(
                f"Git flow work on `{version_git_flow}` "
                f"but Poetry returns `{version_poetry}`"
            )
            return 1

        with open("CHANGELOG.md") as fp:
            fp.readline()
            ref_name = fp.readline()
            _, versiom_md, *_ = ref_name.strip().split()

        if versiom_md != version_poetry:
            print(
                f"CHANGELOG.md returns `{versiom_md}` "
                f"but Poetry returns `{version_poetry}`"
            )
            return 1

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
