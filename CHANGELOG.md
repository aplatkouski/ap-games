# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][], and this project adheres to
[PEP 440 - Version Identification][PEP 440]

## [Unreleased]

## [0.0.1] - 2020-08-19
### Changed
- ``SquareGameboard.rows`` method doesn't return rows in reverse order;
- Rename ``TwoPlayerBoardGame.get_adversary_mark`` method to
  ``TwoPlayerBoardGame.get_enemy_mark``;
- Rename``TwoPlayerBoardGame.hight_priority_coordinates`` attribute to
  ``priority_coordinates``;
- Increase the value of the priority coordinates in the Reversi game
  from 5 to 10;
- Rename namedtuple from ``Step`` to ``Move`` and add the boolean field
  ``last``;
- Rename ``axis`` and ``gap`` attributes of ``TwoPlayerBoardGame`` class
  to ``grid_axis`` and ``grid_gap``, respectively;
- Swap the first and second items of the minimax algorithm in
  ``AIPlayer._minimax`` method.
- Rename ``SquareGameboard.grid`` method to ``grid_as_string``.

### Fixed
- Log message in ``AIPlayer._choose_best_move`` method;
- Bug in ``SquareGameboard.__str__`` with missing ``indent``;
- Bug with incorrect calculation of the percentage of move;
- Bug with incorrect selection of the max-min function for
  ``percentage`` of the move, when the ``score`` of the move equal '0';
- Missing ``f-string`` in the log message in
  ``AIPlayer._extract_desired_moves`` method.

### Added
- Parameter ``test_mode`` in config.ini;
- Description of ``_cells_dict`` and ``_colors_dict`` attributes in the
  docstring of ``SquareGameboard`` class;
- Using ``SquareGameboard._available_moves_cache`` in
  ``Revers.place_mark`` method;
- ``SquareGameboard.get_offsets`` method;
- Attribute ``AIPlayer.tree`` with cached moves;
- Method ``TwoPlayerBoardGame.get_adversary_mark``;
- Console ``logger`` handler in log.py;
- ``SquareGameboard.indent`` attribute.

### Removed
- @property ``SquareGameboard.counter``;
- ``SquareGameboard.__getitem__`` method;
- ``SquareGameboard.get_marked_coordinates`` method;
- ``SquareGameboard.get_directions`` method;
- ``SquareGameboard.print_grid`` method.

## [0.0.1rc0] - 2020-08-05
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
[Unreleased]: https://github.com/aplatkouski/ap-games/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/aplatkouski/ap-games/compare/v0.0.1rc0...v0.0.1
[0.0.1rc0]: https://github.com/aplatkouski/ap-games/compare/v0.0.1b3...v0.0.1rc0
[0.0.1b3]: https://github.com/aplatkouski/ap-games/compare/v0.0.1b2...v0.0.1b3
[0.0.1b2]: https://github.com/aplatkouski/ap-games/compare/v0.0.1b1...v0.0.1b2
[0.0.1b1]: https://github.com/aplatkouski/ap-games/releases/tag/v0.0.1b1
