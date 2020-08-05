# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][], and this project adheres to
[PEP 440 - Version Identification][PEP 440]

## [Unreleased]

## [0.0.2] - 2020-08-05
### Changed
- rename ``Label`` to ``PlayerMark``;
- rename ``GameBase`` class to ``TwoPlayerBoardGame``;
- rename Player methods ``go`` to ``move``, ``label`` to ``mark``,
  ``type`` ;
- rename ``step`` to ``move`` everywhere;
- rename ``surface`` to ``grid`` everywhere;
- replace ``print`` with ``logger`` instance;
- replace ``input`` with ``sys.stdin``;
- update ``.gitignore``;
- move ``main`` function from ``__main__.py`` to ``cli.py``;
- resort methods in classes (public method are first);

### Fixed
- ``pydocstyle`` configuration;
- ``setuptools`` version in ``pyproject.toml``;

### Added
- docstrings to all public methods;
- ``check-manifest`` to ``.pre-commit-config.yaml`` and settings to
  ``tox.ini``;
- ``darglint`` to ``.pre-commit-config.yaml``;
- additional dependencies to ``flake`` in ``.pre-commit-config.yaml``
  and ``requirements-dev.txt``;

### Removed
- ``setup-cfg-fmt`` from ``.pre-commit-config.yaml``;
- ``reorder_python_imports`` from ``.pre-commit-config.yaml``;
- versions of dependencies in ``.pre-commit-config.yaml``;

## [0.0.1b3] - 2020-07-25
### Added
- Docstrings to basic classes;
- ``pre-commit`` configuration;
- CONTRIBUTION.md and CODE_OF_CONDUCT.md files.

## [0.0.1b2] - 2020-07-22
### Changed
- Game board is colored only in OS Linux.

## [0.0.1b1] - 2020-07-22
### Added
- Initial release.


[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[PEP 440]: https://www.python.org/dev/peps/pep-0440/
[Unreleased]: https://github.com/aplatkouski/ap-games/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/aplatkouski/ap-games/compare/v0.0.2...v0.0.1b3
[0.0.1b3]: https://github.com/aplatkouski/ap-games/compare/v0.0.1b3...v0.0.1b2
[0.0.1b2]: https://github.com/aplatkouski/ap-games/compare/v0.0.1b2...v0.0.1b1
[0.0.1b1]: https://github.com/aplatkouski/ap-games/releases/tag/v0.0.1b1
