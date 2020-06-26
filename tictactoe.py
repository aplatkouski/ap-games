from collections import deque
from typing import Deque, Optional, Set, Tuple

Side = Tuple[str, str, str]

EMPTY = ' '


class TicTacToe:
    """TicTacToe class introduces Tic-Tac-Toe game and supports CLI.

    :param field: Contains 9 symbols containing 'X', 'O' and '_',
     the latter means it's an empty cell.
    :ivar active: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar players: The queue with players.

    """

    def __init__(self, field: str):
        self.field = field.replace('_', EMPTY)
        self.active: bool = True
        self.players: Deque[str] = deque('XO')
        if self.field.count(self.players[0]) > self.field.count(self.players[1]):
            self.players.rotate(1)

    @staticmethod
    def _coordinate_converter(x: int, y: int) -> int:
        """Translates :param:`x` and :param:`y` to one coordinate
        (x, y) ==> coordinate. Where::

            (1, 3) (2, 3) (3, 3)         0  1  2
            (1, 2) (2, 2) (3, 2)  ==>    3  4  5
            (1, 1) (2, 1) (3, 1)         6  7  8

        """
        return (x - 1) + 3 * (3 - y)

    def _read_coordinates(self) -> int:
        """Read ``x`` and ``y`` coordinates from input and return one
        coordinate.

        :return: one coordinate computed from ``x`` and ``y``. Return
         "-1" if coordinate can't be define.

        """
        input_list = input("Enter the coordinates: ").split()
        if len(input_list) >= 2:
            x, y = input_list[:2]
        elif len(input_list) == 1:
            x, y = input_list[0], EMPTY
        else:  # input string is empty
            x = y = EMPTY
        # check ``x`` and ``y``
        if x.isdigit() and y.isdigit():
            if (1 <= int(x) <= 3) and (1 <= int(y) <= 3):
                return self._coordinate_converter(int(x), int(y))
            else:
                print('Coordinates should be from 1 to 3!')
        else:
            print('You should enter numbers!')
        return -1

    def _define_winners(self) -> Set[Optional[str]]:
        """Define and return set of all players who draw solid line.

        If all symbols in a line are the same and not equal ' ' than
        first (any) symbol in the line defines the winner.

        """
        winners: Set[Optional[str]] = set()
        for i in range(3):
            # check rows
            row: str = self.field[i * 3: (i * 3) + 3]
            if len(set(row)) == 1:
                winners.add(row[0])
            # check column
            column: str = self.field[0 + i:: 3]
            if len(set(column)) == 1:
                winners.add(column[0])
        # check diagonal
        back_diagonal: Side = (self.field[0], self.field[4], self.field[8])
        if len(set(back_diagonal)) == 1:
            winners.add(back_diagonal[0])
        forward_diagonal: Side = (self.field[2], self.field[4], self.field[6])
        if len(set(forward_diagonal)) == 1:
            winners.add(forward_diagonal[0])
        winners.discard(EMPTY)
        return winners

    def _define_game_status(self) -> None:
        if -1 <= (self.field.count('X') - self.field.count('O')) <= 1:
            winners: Set[Optional[str]] = self._define_winners()
            if len(winners) == 0:
                if self.field.count(EMPTY) > 0:
                    print("Game not finished")
                else:
                    print("Draw")
            elif len(winners) == 1:
                print(f"{winners.pop()} wins")
            else:  # len(winners) > 1
                print("Impossible")
        else:
            print("Impossible")
        self.active = False

    def print_battlefield(self) -> None:
        """Print "Tic-Tac-Toe" battlefield"""

        print('-' * 9)
        for i in range(0, 7, 3):
            print(f"| {self.field[i]} {self.field[i + 1]} {self.field[i + 2]} |")
        print('-' * 9)

    def play(self) -> None:
        """The main public interface that run the game."""
        self.print_battlefield()
        while self.active:
            coordinate: int = self._read_coordinates()
            if coordinate >= 0:
                if self.field[coordinate] == EMPTY:
                    self.field = self.players[0].join(
                        (self.field[:coordinate], self.field[coordinate + 1:])
                    )
                    self.print_battlefield()
                    self._define_game_status()
                    self.players.rotate(1)
                else:
                    print("This cell is occupied! Choose another one!")


if __name__ == '__main__':
    enter_field = input("Enter cells: ")
    tic_tac_toe = TicTacToe(enter_field)
    tic_tac_toe.play()
