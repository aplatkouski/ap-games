# Project description

## AP Games
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The AP Games is the result of the completion of the project
[Tic-Tac-Toe with AI][] at [JetBrains Academy][]. This project
was developed just for fun and to learn Python and some
concepts of a decision-making algorithm.

## Tic-Tac-Toe with AI + bonus **Reversi** game

Tic-tac-toe, is a paper-and-pencil game for two players,
X and O, who take turns marking the spaces in a 3×3 grid.
The player who succeeds in placing three of their marks in
a horizontal, vertical, or diagonal row is the winner.

### Reversi

Reversi is a strategy board game for two players who take
turns marking the spaces in an 8x8 board.

Each player must place the piece so that an opponent's piece, or a
row of opponent's pieces, is flanked by your pieces. All of
the opponent's pieces between your pieces are then turned
over to become your color. The object of the game is to own
more pieces than your opponent when the game is over.
See [source][reversi rules source].

The example below shows the game interface:
```txt
Please choose the game:
	0 - Tic-Tac-Toe;
	1 - Reversi.
Print 'exit' to exit the program.

Input command: 1
Type 'start user1_type user2_type' to run the selected game,
where user_X_type is one of the supported values:
user, easy, hard and nightmare;
Type 'rules' to get game rules or type 'exit' to return
to the main menu.

Input command: rules
You must place the piece so that an opponent's piece, or a row
of opponent's pieces, is flanked by your pieces.
All of the opponent's pieces between your pieces are then
turned over to become your color. The object of the game is
to own more pieces than your opponent when the game is over.

Input command: start user hard
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
Enter the coordinate [X]: 1 1
You cannot go here!
Enter the coordinate [X]: 1
You should enter two numbers!
Enter the coordinate [X]: 4 3
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

The project has been tested only with [python 3.8][python] on
Ubuntu Linux and Windows 10. If you have python 3.8 and above
installed in your machine, just install the AP Games from [PyPI]:

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
    - ``0`` or ``tic-tac-toe`` for Tic-Tac-Toe game;
    - ``1`` or ``reversi`` for Reversi game.
- ``user-1`` and ``user-2`` are values from the following
  set:
    - ``user`` for human player;
    - ``easy``, ``medium``, ``hard`` and ``nightmare`` for AI
      player.

**Note**: Parameters in brackets are optional.

Or open the python console and type:
```python
# Python version 3.8+
from ap_games import cli
cli.main()
```

## Notes

This package can be run as a console game or integrated into
another application. This project provides the following basic
structures:
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

See also our [CONTRIBUTING.md][].

## Copyright

Copyright (c) 2020 Artsiom Platkouski.
``AP_games`` is licensed under the MIT License - see the [LICENSE.txt][]
file for details.

[Tic-Tac-Toe with AI]: https://hyperskill.org/projects/82
[JetBrains Academy]: https://hyperskill.org/join/0482410e
[PyPI]: https://pypi.org/project/realpython-reader/
[reversi rules source]: http://www.flyordie.com/games/help/reversi/en/games_rules_reversi.html
[python]: https://www.python.org/
[github]: https://github.com
[aplatkouski/ap-games]: https://github.com/aplatkouski/ap-games
[CONTRIBUTING.md]: https://github.com/aplatkouski/ap-games/blob/master/CONTRIBUTING.md
[minimax algorithm video]: https://www.youtube.com/watch?v=KU9Ch59-4vw
[LICENSE.txt]: https://github.com/aplatkouski/ap-games/blob/master/LICENSE.txt
