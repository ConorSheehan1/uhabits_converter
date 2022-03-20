#### Dev Install
```bash
poetry install

# install uhabits_converter as symlink to avoid reinstall whenever code changes
# instead of pip install /path/to/uhabits_converter
# https://github.com/python-poetry/poetry/issues/1135
# workaround using __name__ == '__main__' and fire
poetry run task dev
```

### Tests
```bash
poetry run task tests
```

### Linting
```bash
poetry run task lint
poetry run task isort
poetry run task mypy
```

### Version management
```bash
# pass args e.g. patch, minor, major, choose to commit changes or not
poetry run bumpversion --commit --tag patch
```

### GitHooks
To setup git hooks run:
```bash
poetry run pre-commit install
```
