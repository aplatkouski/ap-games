from setuptools import setup  # type: ignore

setup(
    extras_require=dict(
        test=['coverage==5.2.1', 'pytest==6.0.1', 'pytest-cov==2.10.1'],
        dev=[
            'black==19.10b0',
            'bump2version==1.0.0',
            'check-manifest==0.42',
            'darglint==1.5.2',
            'flake8==3.8.3',
            'flake8-bugbear==20.1.4',
            'flake8-builtins==1.5.3',
            'flake8-docstrings==1.5.0',
            'flake8-import-order==0.18.1',
            'flake8-mypy==17.8.0',
            'flake8-pytest-style==1.2.3',
            'flake8-rst-docstrings==0.0.13',
            'flake8-typing-imports==1.9.0',
            'keyring==21.3.0',
            'mypy==0.782',
            'mypy-extensions==0.4.3',
            'pre-commit==2.6.0',
            'pre-commit-hooks==3.2.0',
            'pydocstyle==5.0.2',
            'pyupgrade==2.7.2',
            'tox==3.19.0',
            'twine==3.2.0',
        ],
    ),
)
