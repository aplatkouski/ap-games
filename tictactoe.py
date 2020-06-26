from collections import deque
from random import choice
from typing import ClassVar, Deque, FrozenSet, Optional, Set, Tuple

Side = Tuple[str, str, str]

EMPTY = ' '


class Player:
    """Player class introduces player in Tic-Tac-Toe game and interacts
    by CLI.

    This class has only one public interface :meth:`.Player.go`.

    """

    supported_types: ClassVar[FrozenSet[str]] = frozenset(("user", "easy"))

    def __init__(self, mark: str, *, type_: str = "user") -> None:
        if type_ not in Player.supported_types:
            raise ValueError
        self.mark = mark
        self.is_ai = False
        if type_ != "user":
            self.is_ai = True
            self.level = type_

    def __str__(self) -> str:
        return self.mark

    @staticmethod
    def _coordinate_converter(x: int, y: int) -> int:
        """Translates :param:`x` and :param:`y` to one coordinate
        (x, y) ==> coordinate. Where::

            (1, 3) (2, 3) (3, 3)         0  1  2
            (1, 2) (2, 2) (3, 2)  ==>    3  4  5
            (1, 1) (2, 1) (3, 1)         6  7  8

        """
        return (x - 1) + 3 * (3 - y)

    @classmethod
    def _read_coordinates(cls) -> int:
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
                return cls._coordinate_converter(int(x), int(y))
            else:
                print('Coordinates should be from 1 to 3!')
        else:
            print('You should enter numbers!')
        return -1

    def go(self, field: str) -> int:
        if self.is_ai:
            print(f'Making move level "{self.level}"')
            return choice([index for index, cell in enumerate(field) if cell == EMPTY])
        return self._read_coordinates()


class TicTacToe:
    """TicTacToe class introduces Tic-Tac-Toe game and supports CLI.

    :param field: Contains 9 symbols containing 'X', 'O' and '_',
     the latter means it's an empty cell.
    :ivar active: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar player_x: first :class:`.Player`.
    :ivar player_o: second :class:`.Player`.
    :ivar field: battlefield as 9-letters string. It can contain only
     ``X``, ``O`` and `` `` symbols.
    :ivar players: The queue with :class:`.Player`s.

    """

    def __init__(
            self, *, field: str = EMPTY * 9, x_type: str = "user", o_type: str = "user"
    ):
        self.active: bool = True

        self.player_x: Player = Player('X', type_=x_type)
        self.player_o: Player = Player('O', type_=o_type)

        self.field: str = field.replace('_', EMPTY)
        if not frozenset(self.field).issubset(
                {self.player_x.mark, self.player_o.mark, EMPTY}
        ):
            raise ValueError
        self.players: Deque[Player] = deque((self.player_x, self.player_o))
        if self.field.count(self.players[0].mark) > self.field.count(
                self.players[1].mark
        ):
            self.players.rotate(1)

    def _define_winners(self) -> Set[Optional[str]]:
        """Define and return set of all players who draw solid line.

        If all symbols in a line are the same and not equal ' ' than
        first (any) symbol in the line defines the winner.

        """
        winners: Set[Optional[str]] = set()
        for i in range(3):
            # check rows
            row: str = self.field[i * 3: (i * 3) + 3]
            if len(frozenset(row)) == 1:
                winners.add(row[0])
            # check column
            column: str = self.field[0 + i:: 3]
            if len(frozenset(column)) == 1:
                winners.add(column[0])
        # check diagonal
        back_diagonal: Side = (self.field[0], self.field[4], self.field[8])
        if len(frozenset(back_diagonal)) == 1:
            winners.add(back_diagonal[0])
        forward_diagonal: Side = (self.field[2], self.field[4], self.field[6])
        if len(frozenset(forward_diagonal)) == 1:
            winners.add(forward_diagonal[0])
        winners.discard(EMPTY)
        return winners

    def _define_game_status(self) -> None:
        if (
                abs(
                    self.field.count(self.player_x.mark)
                    - self.field.count(self.player_o.mark)
                )
                <= 1
        ):
            winners: Set[Optional[str]] = self._define_winners()
            if len(winners) == 0:
                if self.field.count(EMPTY) > 0:
                    return
                else:  # self.field.count(EMPTY) == 0
                    print("Draw")
            elif len(winners) == 1:
                print(f"{winners.pop()} wins\n")
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
            coordinate: int = self.players[0].go(self.field)
            if coordinate >= 0:
                if self.field[coordinate] == EMPTY:
                    self.field = self.players[0].mark.join(
                        (self.field[:coordinate], self.field[coordinate + 1:])
                    )
                    self.print_battlefield()
                    self._define_game_status()
                    self.players.rotate(1)
                else:
                    print("This cell is occupied! Choose another one!")


if __name__ == '__main__':
    command = input("Input command: ")
    while command != "exit":
        parameters = command.split()
        if (
                len(parameters) == 3
                and parameters[0] == "start"
                and parameters[1] in Player.supported_types
                and parameters[2] in Player.supported_types
        ):
            tic_tac_toe = TicTacToe(x_type=parameters[1], o_type=parameters[2])
            tic_tac_toe.play()
        else:
            print("Bad parameters!")
        command = input("Input command: ")
