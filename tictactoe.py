from collections import deque
from random import choice
from typing import (Callable, ClassVar, Deque, Dict, List, Literal, Optional,
                    Set, Tuple, Type)

Side = Tuple[str, str, str]
Strategy = Callable[[str], int]
SupportedPlayers = Dict[str, Type['TicTacToePlayer']]
PlayerMarks = Literal["X", "O"]


EMPTY = ' '


class TicTacToePlayer:
    """TicTacToePlayer class introduces player in Tic-Tac-Toe."""

    def __init__(self, mark: PlayerMarks) -> None:
        self.mark = mark

    def __str__(self) -> str:
        return self.mark

    def go(self, field: str) -> int:
        raise NotImplementedError


class HumanPlayer(TicTacToePlayer):
    """HumanPlayer class introduces user in Tic-Tac-Toe game and
    interacts by CLI.

    """

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
    def go(cls, field: str) -> int:
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


class EasyPlayer(TicTacToePlayer):
    """EasyPlayer class introduces AI player in Tic-Tac-Toe
    game with choice random index of any empty (' ') cell in field.

    """

    @staticmethod
    def _random_choice(field: str) -> int:
        empty_cells: List[int] = [
            index for index, cell in enumerate(field) if cell == EMPTY
        ]
        if empty_cells:
            return choice(empty_cells)
        return -1

    def go(self, field: str) -> int:
        """Return random index of any empty (' ') cell in field."""
        print(f'Making move level "easy"')
        return self._random_choice(field)


class MediumPlayer(EasyPlayer):
    """MediumPlayer class introduces AI player in Tic-Tac-Toe game
    with making choice index of empty cell based on analysis
    of consequences of one-next-step.

    """

    @staticmethod
    def _strategy(*, func: Strategy, field: str) -> int:
        """Iterates over all possible combinations of sides (rows,
        columns and diagonals) and check them with :param:`func`.

        If :param:`func` return ``True`` (strategy can be applied to
        side) return index of empty cell in field as move option.
        Otherwise return "-1"

        """
        for i in range(3):
            row: str = field[i * 3: (i * 3) + 3]
            if func(row):
                return i * 3 + row.index(EMPTY)

            column: str = field[0 + i:: 3]
            if func(column):
                return column.index(EMPTY) * 3 + i

        back_diagonal: str = field[0] + field[4] + field[8]
        if func(back_diagonal):
            return back_diagonal.index(EMPTY) * 3 + back_diagonal.index(EMPTY)

        forward_diagonal: str = field[2] + field[4] + field[6]
        if func(forward_diagonal):
            return (back_diagonal.index(EMPTY) + 1) * 2
        return -1

    def _can_win(self, side: str) -> bool:
        """Strategy: If player can win, return ``True``, otherwise
        return ``False``

        :param side: any side (row, column or diagonal) as 3-letters string

        """
        if side.count(EMPTY) == 1 and side.count(self.mark) == 2:
            return True
        return False

    def _can_lose(self, side: str) -> bool:
        """Strategy: If player can lose, return ``True``, otherwise
        return ``False``

        :param side: any side (row, column or diagonal) as 3-letters string

        """
        if side.count(EMPTY) == 1 and side.find(self.mark) == -1:
            return True
        return False

    def go(self, field: str) -> int:
        print(f'Making move level "medium"')
        for func in [self._can_win, self._can_lose]:
            result: int = self._strategy(func=func, field=field)
            if result >= 0:
                return result
        return self._random_choice(field=field)


class TicTacToe:
    """TicTacToe class introduces Tic-Tac-Toe game and supports CLI.

    :param field: Contains 9 symbols containing 'X', 'O' and '_'.
     '_' means an empty cell.

    :ivar active: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar player_x: first :class:`.TicTacToePlayer`.
    :ivar player_o: second :class:`.TicTacToePlayer`.
    :ivar field: battlefield as 9-letters string. It can contain only
     ``X``, ``O`` and `` `` symbols.
    :ivar players: The queue with :class:`.TicTacToePlayer`s.

    """

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": EasyPlayer,
        "medium": MediumPlayer,
    }

    def __init__(
            self, *, field: str = EMPTY * 9, x_type: str = "user", o_type: str = "user"
    ):
        self.active: bool = True

        self.player_x: TicTacToePlayer = TicTacToe.supported_players[x_type]('X')
        self.player_o: TicTacToePlayer = TicTacToe.supported_players[o_type]('O')

        self.field: str = field.replace('_', EMPTY)
        if not frozenset(self.field).issubset(
                {self.player_x.mark, self.player_o.mark, EMPTY}
        ):
            raise ValueError
        self.players: Deque[TicTacToePlayer] = deque((self.player_x, self.player_o))
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
                    print("Draw\n")
            elif len(winners) == 1:
                print(f"{winners.pop()} wins\n")
            else:  # len(winners) > 1
                print("Impossible\n")
        else:
            print("Impossible\n")
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
                and parameters[1] in TicTacToe.supported_players
                and parameters[2] in TicTacToe.supported_players
        ):
            tic_tac_toe = TicTacToe(x_type=parameters[1], o_type=parameters[2])
            tic_tac_toe.play()
        else:
            print("Bad parameters!")
        command = input("Input command: ")
