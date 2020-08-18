# How to contribute

Thanks for your interest in improving this project!
These guidelines attempt to make the process easier and more enjoyable.

## General guidelines

Everyone interacting with this project is expected to follow the
[Code of Conduct][].

Submit questions, bug reports, and feature requests in the [issue tracker][].
Please be as descriptive as you can. For bug reports, please include
information about your local environment, the steps to reproduce the bug,
and any relevant command-line output.

Submit improvements to code and documentation via [pull requests][].
Unless it’s a small/quick fix, pull requests should reference an open issue
that’s been discussed. This helps ensure that your contribution is aligned
with the goals of this project.

During development, use the provided tools to check for consistent style,
coding errors, and test coverage. In general, only pull requests with passing
tests and checks will be merged.

## Setting up a development environment

### [Fork and clone][GitHub Docs fork-a-repo] this repository
1. Go to ``https://github.com/aplatkouski/ap-games`` and click the
   "fork" to create own copy of the project.

2. Using [git][] clone the project to local computer and add the upstream
   repository:
   ```shell script
   $ git clone https://github.com/your-username/ap-games.git
   $ cd ap-games
   $ git remote add upstream  https://github.com/aplatkouski/ap-games.git
   $ git remote -v
   ```

### Create and activate a [virtual environment]

**Note**: The minimum supported Python version is 3.8.

To get multiple versions of Python installed on your system use
[pyenv][] or [virtualenv][] tools for that. See short tutorial for
details [Pipenv & Virtual Environments][].

```shell script
$ cd ap-games
$ python3 -m virtualenv -p /usr/bin/python3.8 .venv
$ source .venv/bin/activate
```

### Check python version
```shell script
(.venv) $ python --version
```

### Install this package
1. Upgrade ``pip`` and ``setuptools``
   ```shell script
   (.venv) $ pip install --no-cache-dir --upgrade pip setuptools
   ```

2. Install package, along with the tools you need to develop and run
   tests, run the following in your virtual environment:
   ```shell script
   (.venv) $ pip install -e .[dev,test]
   (.venv) $ pre-commit install --install-hooks
   ```

   This will install:
     - [pytest][] and [coverage.py][] to run the tests;
     - [black][] to format the code;
     - [flake8][] to identify coding errors and check code style;
     - [pydocstyle][] to check docstring style;
     - [pre-commit][] to run the formatters and linters on every commit;
     - [tox][] to run common development tasks.

**Congratulations!** You're now all set to begin development.

## During development

- Activate your virtual environment
  ```shell script
  $ cd ap-games
  $ source .venv/bin/activate
  ```

- Pull the last changes from ``upstream`` and create own
  branch for the feature:
  ```shell script
  (.venv) $ git checkout master
  (.venv) $ git pull upstream master
  (.venv) $ git checkout -b new-feature
  ```

- Your work here ...

- Run the tests:
  ```shell script
  (.venv) $ pytest
  ```

- Run the tests and generate a coverage report:
  ```shell script
  (.venv) $ tox -e py,coverage
  ```

  Please add or update tests to ensure the coverage doesn't drop.

- Run the formatters and linters:
  ```shell script
  (.venv) $ tox -e check
  ```

  These checks are also run on every commit via [pre-commit hooks][].
  Please fix any failures before committing.

- Run the tests in all supported Python versions, generate a coverage report,
  and run the checks
  ```shell script
  (.venv) $ tox
  ```

- Commit the changes
  ```shell script
  (.venv) $ git commit add .
  (.venv) $ git commit -s -m "A brief description of changes"
  ```

## To submit contribution

### To rebase on master
```shell script
(.venv) $ git fetch upstream

# go to the feature branch
(.venv) $ git checkout new-feature

# make a backup in case you mess up
(.venv) $ git branch new-feature-temp new-feature

# rebase on upstream master branch
(.venv) $ git rebase upstream/master
# to resolve conflicts...

# remove the backup branch upon a successful rebase
(.venv) $ git branch -D new-feature-temp
```

Or recovering from mess-ups if necessary:
```shell script
(.venv) $ git rebase --abort

# reset branch back to the saved point
(.venv) $ git reset --hard new-feature-temp

# OR look at the reflog of the branch
(.venv) $ git reflog show new-feature
# ...
# reset the branch to where it was before he botched rebase
(.venv) $ git reset --hard new-feature@{2}
```

### Push changes

```shell script
(.venv) $ git push origin new-feature
```

### Open pull request

On ``https://github.com/your-username/ap-games`` click
**Open pull request**.

For details see [GitHub.com Help Documentation]

## Making a release

**Note**: This tutorial is only for contributors who have access to the
main repository.

This project adheres to [PEP 440 - Version Identification][PEP 440] and
uses [bump2version][]

### Checkout and update `master`

```shell script
(.venv) $ git checkout master
(.venv) $ git pull upstream master
```

### Update the [changelog]

### Change a version number, commit the changes, tag the release
(e.g. ``0.0.1b3`)
```shell script
(.venv) $ python setup.py --version
0.0.1b3.dev1+gea9858a.d20200725
(.venv) $ bump2version --dry-run --list [major|minor|maintenance|release|build]
```
Run ``bump2version`` without ``--dry-run`` upon a correct output.

For example:
```shell script
(.venv) $ version=v`bump2version --dry-run --list maintenance | tail -n 1 | sed -r "s/^.*=//"`
(.venv) $ bump2version --list maintenance
```

### Push origin
```shell script
(.venv) $ git push origin master $version
```

### Run the release pipeline to upload to [TestPyPI]
```shell script
(.venv) $ tox -e release
```

### If it looks good on TestPyPI, run the release pipeline to upload to [PyPI]

```shell script
(.venv) $ tox -e release pypi
```

### Create a new GitHub Release

Using the [GitHub CLI][], with the version number
as the title, the changelog as the description, and the distribution packages
as assets

```shell script
(.venv) $ hub release create -m $version -e $(find dist/* -exec echo "-a {}" \;) $version
```

Add the ``-p`` flag for pre-releases.


[Code of Conduct]: https://github.com/aplatkouski/ap-games/blob/master/CODE_OF_CONDUCT.md
[issue tracker]: https://github.com/aplatkouski/ap-games/issues
[pull requests]: https://github.com/aplatkouski/ap-games/pulls
[GitHub Docs fork-a-repo]: https://docs.github.com/en/github/getting-started-with-github/fork-a-repo
[git]: https://git-scm.com/
[pyenv]: https://github.com/pyenv/pyenv
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[Pipenv & Virtual Environments]: https://docs.python-guide.org/dev/virtualenvs/
[virtual environment]: https://docs.python.org/3/library/venv.html
[pre-commit hooks]: ./.pre-commit-config.yaml
[PEP 440]: https://www.python.org/dev/peps/pep-0440/
[GitHub.com Help Documentation]: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests
[pytest]: https://docs.pytest.org/en/latest/
[coverage.py]: https://coverage.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable/
[flake8]: http://flake8.pycqa.org/en/latest/
[pydocstyle]: http://www.pydocstyle.org/en/latest/
[pre-commit]: https://pre-commit.com/
[tox]: https://tox.readthedocs.io/en/latest/
[changelog]: ./CHANGELOG.md
[TestPyPI]: https://test.pypi.org/project/ap-games/
[PyPI]: https://pypi.org/project/ap-games/
[bump2version]: https://github.com/c4urself/bump2version
[GitHub CLI]: https://hub.github.com/
