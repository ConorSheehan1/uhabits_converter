## Installing dependencies
```bash
pip install poetry
poetry install
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
# once the tag is built by the release action, check the attached .tar is installable.
# e.g. `pip install git+https://github.com/ConorSheehan1/shot@v0.1.1`
# if it is update the release draft and pre-release state.
```
