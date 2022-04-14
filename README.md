# Poetry tools
Script of workflow to setup Poetry.

## CLI commands
### `poetry-tools`
1. Run `poetry install`
2. Add kernel to Jupyter

### `poetry-tools uninstall`
1. Remove kernel from Jupyter
2. Remove .venv created by Poetry

### `poetry-tools list`
1. List kernels fo Jupyter

### `poetry-tools git_flow`
1. Check version from package and poetry match.
2. If branch is `main` or `master`,
  - run `pytest`
3. If branch is `hotfix/.*` or `release/.*`,
  * check version from branch and poetry match
  * check version from changelog and poetry match

## pre-commit
Run `poetry-tools git_flow` whenever commit is made.
```yaml:.pre-commit-config.yaml
- repo: https://github.com/y-marui/poetry-tools
  rev: 1.1.1
  hooks:
  - id: check-poetry-git-flow
```
