from __future__ import annotations

import sys

if sys.version_info < (3, 8):
    raise RuntimeError("This package requires Python 3.8+!")

from ap_games.game.reversi import Reversi
from ap_games.game.tictactoe import TicTacToe
from ap_games.player.player import TEST_MODE

__ALL__ = ["cli"]


def cli() -> None:
    choice: str = ""
    while choice != "exit":
        if TEST_MODE:
            choice = "1"
        else:
            choice = input(
                "Please choose the game:\n"
                "\t0 - Tic-Tac-Toe;\n"
                "\t1 - Reversi.\n"
                "Print 'exit' to exit the program.\n\nInput command: "
            ).strip()
        if choice == "0":
            TicTacToe.cli()
        elif choice == "1":
            Reversi.cli()
        if TEST_MODE:
            choice = "exit"


if __name__ == "__main__":
    cli()
