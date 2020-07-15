from setuptools import setup, find_packages

setup(
    name="tictactoe",
    author="Artsiom Platkouski",
    extras_require=dict(
        tests=["pytest", "coverage"],
        dev=[
            "black",
            "isort",
            "mypy",
            "mypy-extensions",
            "pyre-check",
            "pyre-extensions",
            "typing-extensions",
            "typing-inspect",
        ],
    ),
    package_date={
        "ap_games": ["py.typed"],
        "player": ["py.typed", "player.pyi"],
        "gameboard": ["py.typed"],
        "game": ["py.typed"],
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # mypy
    zip_safe=False,
)
