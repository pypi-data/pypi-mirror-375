# Ceph client

Ceph client

- [Prerequisites](#prerequisites)
- [Updating project template](#updating-project-template)

## Prerequisites

Make sure you have the following software installed:

- [python ^3.12](https://www.python.org/downloads/)
- [poetry ^2.1.3](https://python-poetry.org/docs/#installation)

Install python dependencies using poetry and activate the virtual environment:

```sh
poetry env use python3.12
poetry install
eval $(poetry env activate)
```

Lastly, install `pre-commit hooks` by running:

```sh
pre-commit install
```

## Updating project template

To update the project template, run `copier update` and answer template
questions:

```sh
copier update --trust
```

Review the changes Copier made to your project:

```sh
git diff
```

Resolve any merge conflicts, then stage and commit the changes:

```sh
git add .
git commit -m "Updated project template"
git push
```
