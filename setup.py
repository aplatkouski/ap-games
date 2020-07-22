from setuptools import setup, find_packages
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8")

setup(
    name="ap-games",
    author="Artsiom Platkouski",
    version="0.0.1b1",
    description="Games Tic-Tac-Toe and Reversi with CLI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aplatkouski/tic-tac-toe",
    classifiers=[
        'Development Status :: 4 - Beta',
        "Environment :: Console",
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="board game, console game, tic-tac-toe",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires='>=3.8, <4',
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
    license_file="LICENSE",
    entry_points={
        'console_scripts': [
            'cli=cli:cli',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/aplatkouski/tic-tac-toe/issues',
        'Source': 'https://github.com/aplatkouski/tic-tac-toe',
    },
    # mypy requirements for py.typed files:
    zip_safe=False,
)
