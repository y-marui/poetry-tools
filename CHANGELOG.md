# Change Log
## 1.2.0
Update functions.
* Enhance `install/uninstall` commands #1
    - `pre-commit install/uninstall` at the same time.
    - `poetry add -D pytest` with `install`.

* Bumps version automatically #2

    Update package version
    ```
    bump2version --current-version {current_version} --new-version {new_version} patch {repo_name}/__init__.py
    ```
    Update poetry version
    ```
    poetry version {new_version}
    ```
* Spilit `check_git_flow` into subrotines to easily find problem. #3

## 1.1.1 (2022/04/15)
Fix `python` path.

## 1.1.0 (2022/04/14)
Add pre-commit plugin `check-poetry-git-flow`.

## 1.0.0 (2022/04/14)
Add `poetry-tools` script.
