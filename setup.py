from setuptools import setup  # type: ignore

setup(
    use_scm_version=True,
    extras_require=dict(
        test=["coverage==5.2.1", "pytest==5.4.3"],
        dev=[
            "black==stable",
            "bump2version==1.0.0",
            "check-manifest==0.42",
            "flake8==3.8.3",
            "flake8-bugbear==20.1.4",
            "flake8-mypy==17.8.0",
            "flake8-typing-imports==1.9.0",
            "mypy==0.782",
            "mypy-extensions==0.4.3",
            "pre-commit==2.6.0",
            "pre-commit-hooks==3.1.0",
            "pydocstyle==5.0.2",
            "pyupgrade==2.7.2",
            "reorder-python-imports==2.3.2",
            "setup-cfg-fmt==1.11.0",
            "setuptools_scm==4.1.2",
            "tox==3.18.0",
            "twine==3.2.0",
            "typing-extensions==3.7.4.2",
            "typing-inspect==0.6.0",
        ],
    ),
)
