# AP Games

[![PyPI](https://img.shields.io/pypi/v/ap-games)][pypi ap-games]
[![PyPI - License](https://img.shields.io/pypi/l/ap-games)][license.txt]
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ap-games)](https://www.python.org/downloads/release/python-380/)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/434f6c66b7c24320bf36b591b3c81e23)](https://app.codacy.com/manual/aplatkouski/ap-games?utm_source=github.com&utm_medium=referral&utm_content=aplatkouski/ap-games&utm_campaign=Badge_Grade_Dashboard)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The AP Games is the result of the completion of the project
[Tic-Tac-Toe with AI][tic-tac-toe with ai] at
[JetBrains Academy][jetbrains academy]. This project was developed just for
fun and to learn Python and some concepts of a decision-making algorithm.

## Tic-Tac-Toe with AI + bonus **Reversi** game

Tic-tac-toe, is a paper-and-pencil game for two players, X and O, who take
turns marking the spaces in a 3×3 grid. The player who succeeds in placing
three of their marks in a horizontal, vertical, or diagonal row is the winner.

### Reversi

Reversi is a strategy board game for two players who take turns marking the
spaces in an 8x8 board.

Each player must place the piece so that an opponent's piece, or a row of
opponent's pieces, is flanked by your pieces. All of the opponent's pieces
between your pieces are then turned over to become your color. The object of
the game is to own more pieces than your opponent when the game is over.
See [source][reversi rules source].

The example below shows the game interface:
```txt
Please choose the game:
	1 - Tic-Tac-Toe;
	2 - Reversi.
Type "exit" to exit the program.

Input command:
2
Type "start user-1 user-2" to run the game, where "user-1" and "user-2"
is one of the supported values: user, easy, medium, hard, nightmare;
Type "rules" to get game rules or type "exit" to exit from the game.

Input command:
rules
You must place the piece so that an opponent's piece, or a row of
opponent's pieces, is flanked by your pieces.
All of the opponent's pieces between your pieces are then turned over to
become your color. The object of the game is to own more pieces than
your opponent when the game is over.

Input command:
start
Bad parameters!

Input command:
start user hard
  -------------------
8 |                 |
7 |                 |
6 |                 |
5 |       X O       |
4 |       O X       |
3 |                 |
2 |                 |
1 |                 |
  -------------------
    1 2 3 4 5 6 7 8
Enter the coordinate [X]:
1 1
You cannot go here!
Enter the coordinate [X]:
1
You should enter two numbers!
Enter the coordinate [X]:
4 3
  -------------------
8 |                 |
7 |                 |
6 |                 |
5 |       X O       |
4 |       X X       |
3 |       X         |
2 |                 |
1 |                 |
  -------------------
    1 2 3 4 5 6 7 8
Making move level "hard" [O]
  -------------------
8 |                 |
7 |                 |
6 |                 |
5 |       X O       |
4 |       O X       |
3 |     O X         |
2 |                 |
1 |                 |
  -------------------
    1 2 3 4 5 6 7 8
Enter the coordinate [X]:

```

## Installation

The project has been tested only with [python 3.8][python] on Ubuntu Linux
and Windows 10. If you have python 3.8 and above installed in your machine,
just install the AP Games from [PyPI][pypi]:

```shell script
python --version
pip install ap-games
```

You can find source code of this package on [github][].
See [aplatkouski/ap-games][] repository.

## How to use

Run module:
```shell script
python -m ap_games [game] [user-1 user-2]
```

Where:
  - ``game`` is a value from the following set:
    - ``1`` or ``tic-tac-toe`` for Tic-Tac-Toe game;
    - ``2`` or ``reversi`` for Reversi game.
  - ``user-1`` and ``user-2`` are values from the following set:
    - ``user`` for human player;
    - ``easy``, ``medium``, ``hard`` and ``nightmare`` for AI player.

**Note**: Parameters in brackets are optional.

Or open the python console and type:
```python
# Python version 3.8+
from ap_games import cli
cli.main()
```

## Notes

This package can be run as a console game or integrated into another
application. This project provides the following basic structures:
  - ``SquareGameboard``
  - ``GameBase``
    - ``TicTacToe``
    - ``Reversi``
  - ``Player``
    - ``HumanPlayer``
    - ``AIPlayer`` - uses mini-max as decision-making algorithm.

## Credits

Thanks to Gaurav Sen for his video
[What is the Minimax Algorithm? - Artificial Intelligence][minimax algorithm video]

## Development & Contributing

Development of this happens on GitHub, patches including tests,
documentation are very welcome, as well as bug reports!

See also our [CONTRIBUTING.md][contributing.md].

## Copyright

Copyright (c) 2020 Artsiom Platkouski. ``AP_games`` is licensed under the
MIT License - see the [LICENSE.txt][license.txt] file for details.

[pypi ap-games]: https://pypi.org/project/ap-games/
[tic-tac-toe with ai]: https://hyperskill.org/projects/82
[jetbrains academy]: https://hyperskill.org/join/0482410e
[pypia]: https://pypi.org/project/realpython-reader/
[reversi rules source]: http://www.flyordie.com/games/help/reversi/en/games_rules_reversi.html
[python]: https://www.python.org/
[github]: https://github.com
[aplatkouski/ap-games]: https://github.com/aplatkouski/ap-games
[contributing.md]: https://github.com/aplatkouski/ap-games/blob/master/CONTRIBUTING.md
[minimax algorithm video]: https://www.youtube.com/watch?v=KU9Ch59-4vw
[license.txt]: https://github.com/aplatkouski/ap-games/blob/master/LICENSE.txt
