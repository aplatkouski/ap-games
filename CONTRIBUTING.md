# Development process

## First-time
 1. Go to ``https://github.com/aplatkouski/ap-games``
    and click the "fork" to create own copy of the project.

 2. Using [git] clone the project to local computer and add the upstream
    repository:
    ```shell script
    git clone https://github.com/your-username/ap-games.git
    cd ap-games
    git remote add upstream  https://github.com/aplatkouski/ap-games.git
    git remote -v
    ```

 3. Create [virtual environment] and active it.

    All commands should be run in the project directory
    "ap-games" by default
    ```shell script
    python3 -m venv .venv
    source .venv/bin/activate
    ```

 4. Upgrade ``pip`` and ``setuptools`` and install the
    development dependencies.
    ```shell script
    pip install --no-cache-dir --upgrade pip setuptools
    pip install -r requirements-dev.txt
    ```
    You're now all set to begin development.

 5. Check python version.
    
    *The minimum supported Python version is 3.8.*
    ```shell script
    python --version
    ```

## Develop
 1. Pull the last changes from ``upstream`` and create own 
    branch for the feature:
    ```shell script
    git checkout master
    git pull upstream master
    git checkout -b new-feature
    # your work here ... 
    # don't forget:
    #  1. to activate virtual environment before (see above)
    #  2. to run tests after (see below)
    git add .
    git commit
    ```
 2. To rebase on master
    ```shell script
    git fetch upstream
    # go to the feature branch
    git checkout new-feature
    # make a backup in case you mess up
    git branch new-feature-temp new-feature
    # rebase on upstream master branch
    git rebase upstream/master
    # to resolve conflicts...
    # remove the backup branch upon a successful rebase
    git branch -D new-feature-temp
    ```
    1. Or recovering from mess-ups if necessary:
       ```shell script
       git rebase --abort
       
       # reset branch back to the saved point
       git reset --hard new-feature-temp
       
       # OR look at the reflog of the branch
       git reflog show new-feature
       # ...
       # reset the branch to where it was before 
       # the botched rebase
       git reset --hard new-feature@{2}
       ```

## To submit contribution

```shell script
$ git push origin my-feature
```

On ``https://github.com/your-username/ap-games`` click 
**Open pull request**.

For details see [GitHub.com Help Documentation]


## Testing

Test are written using the [pytest] testing framework.

Run all tests in project directory:
```shell script
(.venv) $ python -m pytest
```
or run tests using ``tox``
```shell script
(.venv) $ pip install tox
(.venv) $ tox
```

Run tests in a directory:
```shell script
(.venv) $ python -m pytest tests/gameboard
```

To run a specific test:
```shell script
(.venv) $ python -m pytest tests/gameboard/test_gameboard.py::test_rows
```


[git]: https://git-scm.com/
[virtual environment]: https://docs.python.org/3/library/venv.html
[GitHub.com Help Documentation]: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests
[pytest]: https://docs.pytest.org/en/latest/
