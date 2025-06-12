## Getting Started

In this document we will guide you through the process of setting up the environment to work and contribute to this codebase.

> Note: *Advanced users, who are familar with poetry or want to use conda/pip with a requirements.txt files, can skip this section. Nonetheless, we recommend using poetry when contributing to this package.*

### 1. Environment Setup

This project uses poetry to manage the dependencies. Therefore it's recommended to install poetry first. You can find the installation instructions [here](https://python-poetry.org/docs/). To install multiple python versions, you might also want to use [pyenv](https://github.com/pyenv/pyenv) or [pyenv-win](https://github.com/pyenv-win/pyenv-win) on Windows.

As many researchers are using conda, or pip with other virtual environments, we provide a `requirements.txt` file for the installation of the dependencies.

#### 1.1 Poetry

Once poetry is installed, you can create a virtual environment and install the dependencies by running the following commands in the root directory of the repository:

```bash
poetry env use [Your-Python-Version]
```
Make sure to have a supported python version installed on your system. You can find the supported python versions in the `pyproject.toml` file.
If your default version in poetry is >3.9 a simple:

```bash
poetry shell
```

Should do the trick as well.

Make sure the environment is activated, by checking whether the python executable is the one from the virtual environment. You can check this by running:

```bash
which python
```

on Unix systems or:

```powershell
(Get-Command python).Path
```

on Windows systems (powershell).

Once the environment is activated, you can install the dependencies by running:

```bash
poetry install
```

This will install the basic dependencies for the project. If you want to install the development dependencies as well - **which you will need for executing the notebooks** - you can run:

```bash
poetry install --with dev
```

#### 1.2. pre-commit

This repository uses [pre-commit](https://pre-commit.com/) to automatically format the code and check for linting errors. Pre-commit is installed automatically when you run `poetry install --with dev`. To enable pre-commit, you need to run the following command once:

```bash
pre-commit install
```
