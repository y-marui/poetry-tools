# import argparse
# import imp
# import re
# from typing import AbstractSet
# from typing import Sequence
import subprocess

from pre_commit_hooks.util import cmd_output

from pre_commit_hooks.no_commit_to_branch import is_on_branch

import click


@click.command()
def check_git_flow():
    """Check compatibility with git-flow.
    
    If branch is `main` or `master`, run `pytest`.
    If branch is `hotfix/.*` or `release/.*`, check version from branck and poetry match.
    """
    if is_on_branch(["main", "master"], []):
        res = subprocess.run(["poetry", "run", "pytest"])
        return res.returncode 

    elif is_on_branch([], ["hotfix/.*", "release/.*"]):
        ref_name = cmd_output('git', 'symbolic-ref', 'HEAD')
        chunks = ref_name.strip().split('/')
        version_git_flow = '/'.join(chunks[3:])

        version_poetry = cmd_output('poetry', 'version', "-s").strip()

        if version_git_flow != version_poetry:
            print(f"Git flow work on `{version_git_flow}` but Poetry returns `{version_poetry}`")
            return 1

    return 0

if __name__ == '__main__':
    raise SystemExit(check_git_flow())