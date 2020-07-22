from setuptools import setup, find_packages
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.resolve()

readme = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="ap-games",
    version="0.0.1b1",
    description="Games Tic-Tac-Toe and Reversi with CLI.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/aplatkouski/ap-games",
    author="Artsiom Platkouski",
    author_email="komukc.apt@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="board game, console game, tic-tac-toe, reversi",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8, <4",
    extras_require=dict(
        tests=["pytest", "coverage"],
        dev=[
            "flake8",
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
    package_data={
        "ap_games": ["py.typed"],
        "player": ["py.typed", "player.pyi"],
        "gameboard": ["py.typed"],
        "game": ["py.typed"],
    },
    include_package_data=True,
    entry_points={"console_scripts": ["ap_games=ap_games.cli:cli"]},
    project_urls={
        "Bug Reports": "https://github.com/aplatkouski/ap-games/issues",
        "Source": "https://github.com/aplatkouski/ap-games",
    },
    # mypy requirements for py.typed files:
    zip_safe=False,
)
