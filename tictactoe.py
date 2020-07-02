from collections import deque
from random import choice
from typing import (Any, Callable, ClassVar, Deque, Dict, Iterable, List,
                    NoReturn, Set, Tuple, Type, Union, cast)

from typing_extensions import Literal

Coordinate = Tuple[int, int]
Cell = Tuple[Coordinate, str]
Side = Tuple[Cell, ...]
Sides = Tuple[Side, ...]
Strategy = Callable[[Tuple[str, ...]], bool]
SupportedPlayers = Dict[str, Type['Player']]
Label = Literal['X', 'O', 'W', 'V']

EMPTY: Literal[' '] = ' '


class SquareBattlefield:
    """

    :param field: The battlefield, represented as a string, where each
     character is mapped to a cell left to right top to bottom.
    :param gap: ``' '`` by default. Defines the gap that will be printed
     between cells in a row.
    :param axis: ``False`` by default. If ``True`` print axis.

    :ivar size: The size of field from 2 to 9.

    """

    undefined_coordinate: ClassVar[Coordinate] = (-1, -1)
    undefined_cell: ClassVar[Cell] = (undefined_coordinate, '')

    def __init__(
            self, *, field: str = EMPTY * 9, gap: str = ' ', axis: bool = False
    ) -> None:

        side = int(len(field) ** (1 / 2))
        if 1 > side > 9:
            raise ValueError("The size of the battlefield must be between 2 and 9!")
        # check that the field is a square
        if side ** 2 != len(field):
            raise ValueError(
                f"The battlefield must be square! {side}^2 != {len(field)}."
            )
        self.size: int = side

        self._field: str = field
        self._gap: str = gap
        self._axis: bool = axis

    def __str__(self) -> str:
        horizontal_border: str = (
                ("  " if self._axis else "")
                + "-" * (self.size + len(self._gap) * (self.size + 1) + 2)
        )
        sparse_rows: List[str] = list()
        row: Side
        for num, row in enumerate(self.rows):
            row_as_str: str = (
                    (f"{self.size - num} " if self._axis else "")
                    + f"|{self._gap}"
                    + f"{self._gap}".join(label for _, label in row)
                    + f"{self._gap}|"
            )
            sparse_rows.append(row_as_str)

        field: str = f"\n".join(sparse_rows)
        col_nums: str = f"{self._gap}".join(map(str, range(1, self.size + 1)))
        battlefield: str = (
                f"{horizontal_border}\n"
                f"{field}\n"
                f"{horizontal_border}"
                + (f"\n   {self._gap}{col_nums}{self._gap}" if self._axis else "")
        )
        return battlefield

    def __iter__(self) -> Iterable[str]:
        return iter(self._field)

    def __len__(self) -> int:
        return len(self._field)

    def __call__(self, x: int, y: int) -> Cell:
        """Return cell by coordinate as 2-tuple.

        :param x: column number. Column number starts with 1 from left
         side of field.
        :param y: row number. Row number starts with 1 from bottom of
         field.

        :return: 2-tuple, where:
         * ``first item`` - column and row coordinates of corresponding
           cell.
         * ``second item`` - is a string with the label of corresponding
           cell.

        """
        if (1 <= y <= self.size) and (1 <= x <= self.size):
            index: int = self._coordinate_to_index(x=x, y=y)
            return (x, y), self._field[index]
        return self.undefined_cell

    @property
    def columns(self) -> Sides:
        """Return all columns as a tuple of column.

        For details see :meth:`.SquareBattlefield.all_sides`.

        """
        first_index_of_each_column = range(self.size)
        columns: List[Side] = list()
        for index in first_index_of_each_column:
            columns.append(self.cells[index:: self.size])
        return tuple(columns)

    @property
    def rows(self) -> Sides:
        """Return all rows as a tuple of row.

        For details see :meth:`.SquareBattlefield.all_sides`.

        """
        first_index_of_each_row = range(0, self.size ** 2 - 1, self.size)
        rows: List[Side] = list()
        for index in first_index_of_each_row:
            rows.append(self.cells[index: index + self.size])
        return tuple(rows)

    @property
    def diagonals(self) -> Sides:
        """Return main and reverse diagonals as a tuple.

        For details see :meth:`.SquareBattlefield.all_sides`.

        """
        main_diagonal: Side = tuple(
            self.cells[i * (self.size + 1)] for i in range(self.size)
        )
        reverse_diagonal: Side = tuple(
            self.cells[(i + 1) * (self.size - 1)] for i in range(self.size)
        )
        return main_diagonal, reverse_diagonal

    @property
    def all_sides(self) -> Sides:
        """Return all rows, columns and diagonals as a tuple of all
        sides. Where each side is a tuple of cells.

        """
        return self.rows + self.columns + self.diagonals

    @property
    def cells(self) -> Tuple[Cell, ...]:
        """Return tuple of cells of the battelfield where each cell is
        a 2-tuple, where:
         * ``first item`` - is a coordinate of the corresponding cell;
         * ``second item`` - is a label (as string) of the corresponding
           cell.

        """
        return tuple(
            (self._index_to_coordinate(index), label)
            for index, label in enumerate(self._field)
        )

    @property
    def possible_steps(self) -> Tuple[Coordinate, ...]:
        """Return coordinates of all possible steps. By default,
        coordinates of all ``EMPTY`` cells.

        """
        return tuple(coordinate for coordinate, label in self.cells if label == EMPTY)

    def count(self, label: str) -> int:
        """Returns the number of occurrences of a :param:`label` in the
        current battlefield.

        """
        return self._field.count(label)

    def _coordinate_to_index(self, x: int, y: int) -> int:
        """Translates :param:`x` and :param:`y` to index of cell.

        Where an example for a 3x3 ``self._field``::

            (1, 3) (2, 3) (3, 3)         0  1  2
            (1, 2) (2, 2) (3, 2)  ==>    3  4  5
            (1, 1) (2, 1) (3, 1)         6  7  8

        Return "-1" if it is impossible to convert.

        """
        if (1 <= x <= self.size) and (1 <= y <= self.size):
            return (x - 1) + self.size * (self.size - y)
        else:
            print(f'Coordinates should be from 1 to {self.size}!')
        return -1

    def _index_to_coordinate(self, index: int) -> Coordinate:
        """Convert the index to coordinate.

        For details see :meth:`.SquareBattlefield._coordinate_to_index`.

        """
        if 0 <= index < len(self._field):
            x, y = divmod(index, self.size)
            column = y + 1
            row = self.size - x
            return column, row
        return self.undefined_coordinate

    def get_offset_cell(self, coordinate: Coordinate, shift: Coordinate) -> Cell:
        """Return "Cell" (as tuple of coordinate and label) by
        coordinate calculated as algebraic sum of vectors:
        :param:`coordinate` and :param:`shift`.

        """
        new_coordinate: Coordinate = cast(
            Tuple[int, int], tuple(map(sum, zip(coordinate, shift)))
        )
        return self(*new_coordinate)

    def print(self) -> None:
        """Print battlefield."""
        print(self)

    def label(self, coordinate: Coordinate, label: str, *, force: bool = False) -> bool:
        """Label position of battelfield with :param:`coordinate` with
        :param:`label` if :param:`force` = ``True`` or occupied position
        is **empty** (``EMPTY``). Return ``True``, otherwise return
        ``False``.

        """
        index: int = self._coordinate_to_index(*coordinate)
        if 0 <= index < len(self._field):
            if force or self._field[index] == EMPTY:
                self._field = label.join(
                    (self._field[:index], self._field[index + 1:])
                )
                return True
            print("This cell is occupied! Choose another one!")
        return False

    def move(
            self,
            from_coordinate: Coordinate,
            to_coordinate: Coordinate,
            label: str,
            *,
            force: bool = False,
    ) -> Union[NoReturn, bool]:
        """Move :param:`label` from one place to another.

        :param from_coordinate: The coordinate of cell that will be
         erased (set ``EMPTY``).
        :param to_coordinate: The coordinate of cell that will be
         labeled with param:`label` if at least one of condition is
         ``True``:
          * ``force=True``;
          * value in destination cell is ``EMPTY``and :param:`label` is
            equal "label" in cell with :param:`from_coordinate`.
        :param label: "label" that will be set cell with
         ``to_coordinate``.
        :param force: Default is ``False``. If ``force=True`` it doesn't
         matter if the position with ``to_coordinate`` is empty or if
         the position with ``from_coordinate`` contains the same "label"
         as :param:`label`.

        """
        if force or label == self(*from_coordinate)[1]:
            result = self.label(to_coordinate, label, force=force)
            if result:
                self.label(from_coordinate, EMPTY, force=True)
                return result
        else:
            raise ValueError("You cannot move other player's 'label'")
        return False


class Player:
    """Class introduces the player in the game."""

    def __init__(self, game: 'Game', label: Label) -> None:
        self.game = game
        self.label = label

    def __str__(self) -> str:
        return self.label

    def random_choice(self, field: SquareBattlefield) -> Coordinate:
        possible_steps: Tuple[Coordinate, ...] = self.game.possible_steps
        if possible_steps:
            return choice(possible_steps)
        return field.undefined_coordinate

    def go(self, field: SquareBattlefield) -> Coordinate:
        """Return random coordinate of any empty (``EMTPY``) cell in
        ``field``.

        This method should be overridden by subclasses if there is a
        more complex rule for determining coordinates.

        """
        return self.random_choice(field)


class HumanPlayer(Player):
    """HumanPlayer class introduces the user in the game with the
    ability to interact through the CLI.

    """

    def go(self, field: SquareBattlefield) -> Coordinate:
        """Read coordinate from input and return them.

        :return: Return :attr:`.SquareBattlefield.undefined_coordinate`
         if the coordinate are incorrect.

        """
        input_list = input("Enter the coordinate: ").split()
        if len(input_list) >= 2:
            x, y = input_list[:2]
        else:
            x, y = EMPTY, EMPTY
        if x.isdigit() and y.isdigit():
            return int(x), int(y)
        print('You should enter numbers!')
        return field.undefined_coordinate


class EasyPlayer(Player):
    """EasyPlayer class introduces an AI player in the game with ability
    to select a random index of any empty (``EMPTY``) cell on the
    battelfield.

    """

    def go(self, field: SquareBattlefield) -> Coordinate:
        """Return random coordinate of any empty (``EMPTY``) cell in
        ``field``.

        """
        print(f'Making move level "easy"')
        return self.random_choice(field)


class TicTacToeMediumPlayer(Player):
    """TicTacToeMediumPlayer class introduces AI player in Tic-Tac-Toe
    game with making choice index of empty cell based on analysis
    of consequences of one-next-step.

    """

    @staticmethod
    def _strategy(*, func: Strategy, field: SquareBattlefield) -> Coordinate:
        """Iterates over all possible sides (rows, columns and
        diagonals) and check them with :param:`func`.

        If :param:`func` return ``True`` (strategy can be applied to
        side) return coordinate of first empty cell in side as next move
        option.

        :return: Return :attr:`.SquareBattlefield.undefined_coordinate`
         if no one strategy can be applied (all ``func`` return
         ``False``).

        """
        coordinates: Tuple[Coordinate, ...]
        labels: Tuple[str, ...]

        for side in field.all_sides:
            coordinates, labels = zip(*side)
            if func(labels):
                return coordinates[labels.index(EMPTY)]
        return field.undefined_coordinate

    def _try_to_win(self, labels: Tuple[str, ...]) -> bool:
        """Strategy: If player can win taking the next step, return
        ``True``, otherwise return ``False``.

        :param labels: any side (row, column or diagonal) as tuple of
         labels.

        """
        if labels.count(EMPTY) == 1 and labels.count(self.label) == (len(labels) - 1):
            return True
        return False

    def _try_not_to_lose(self, labels: Tuple[str, ...]) -> bool:
        """Strategy: If player can lose without taking the next step,
        return ``True``, otherwise return ``False``.

        :param labels: any side (row, column or diagonal) as tuple of
         labels.

        """
        if labels.count(EMPTY) == 1 and labels.count(self.label) == 0:
            return True
        return False

    def go(self, field: SquareBattlefield) -> Coordinate:
        print(f'Making move level "medium"')
        func: Strategy
        for func in (self._try_to_win, self._try_not_to_lose):
            result: Coordinate = self._strategy(func=func, field=field)
            if result != field.undefined_coordinate:
                return result
        return self.random_choice(field=field)


class Game:
    """Game class.

    :param field: String contains symbols from set :attr:`.Game.labels`
     and symbols '_' or ' ' mean an empty cell.
    :param player_types: Tuple of strings from
     :attr:`.Game.supported_players` that determine types and count of
     players. Length of tuple must be between :attr:`.Game.min_players`
     and :attr:`.Game.max_players`.

    :ivar _active: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar field: The battlefield as instance of
     :class:`.SquareBattlefield`.
    :ivar players: The queue with players. Player is an instance of
     :class:`.Player`. Player with index ``0`` is a current player.


    """

    _X: Literal['X'] = 'X'
    _O: Literal['O'] = 'O'
    _W: Literal['W'] = 'W'
    _V: Literal['V'] = 'V'
    labels: ClassVar[Tuple[Label, ...]] = (_X, _O, _W, _V)

    default_field: ClassVar[str] = EMPTY * 9
    axis: ClassVar[bool] = False
    gap: ClassVar[str] = ' '

    min_players: ClassVar[int] = 2
    max_players: ClassVar[int] = 2

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": EasyPlayer,
    }

    def __init__(
            self,
            *,
            field: str = default_field,
            player_types: Tuple[str, ...] = ("user", "user"),
    ):
        players_number = len(player_types)
        if (players_number < self.min_players) or (players_number > self.max_players):
            raise ValueError(
                f"The number of players should be from 2 to {self.max_players}!"
            )

        self.players: Deque[Player] = deque()
        for num, player_type in enumerate(player_types):
            label: Label = self.labels[num]
            self.players.append(
                self.supported_players[player_type](game=self, label=label)
            )

        field_without_underscore = field.replace('_', EMPTY)
        if not frozenset(field_without_underscore).issubset({*self.labels, EMPTY}):
            raise ValueError

        self._active: bool = True
        self.field: SquareBattlefield = SquareBattlefield(
            field=field_without_underscore, gap=self.gap, axis=self.axis
        )
        # move the player with the least number of "label" to the front
        # of the queue
        while self.field.count(self.players[0].label) > self.field.count(
                self.players[1].label
        ):
            self.players.rotate(1)

    @property
    def winners(self) -> Set[Player]:
        """Must be overridden by subclasses and must return
        a set of instance ot the :class:`.Player` defined as winner.

        """
        raise NotImplementedError

    @property
    def possible_steps(self) -> Tuple[Coordinate, ...]:
        """Return coordinates of all empty cells as a tuple.

        This method should be overridden by subclasses if there is a
        more complex rule for determining which cell is empty.

        """
        return self.field.possible_steps

    def refresh_status(self) -> None:
        """Must be overridden by subclasses and must change
        :attr:`.Game._active` if game cannot be continued.

        """
        raise NotImplementedError

    def step(self, coordinate: Coordinate, **kwargs: Any) -> bool:
        """Change the cell(s) in :attr:`.Game.field` using
        :param:`coordinate` and the current user (user with index ``0``
        in :attr:`.Game.players`).

        This method should be overridden by subclasses if there is a
        more complex rule for labeling cell(s) in ``field``.

        """
        if coordinate not in self.possible_steps:
            print("You cannot go here!")
            return False
        return self.field.label(coordinate=coordinate, label=self.players[0].label)

    def play(self) -> None:
        """The main public interface that run the game."""
        self.field.print()
        while self._active:
            coordinate: Coordinate = self.players[0].go(self.field)
            if self.step(coordinate=coordinate):
                self.field.print()
                self.players.rotate(1)
                self.refresh_status()


class TicTacToe(Game):
    """TicTacToe class introduces Tic-Tac-Toe game and supports CLI.

    For details see :class:`.Game`.

    """

    default_field: ClassVar[str] = EMPTY * 9

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": EasyPlayer,
        "medium": TicTacToeMediumPlayer,
    }

    def __init__(
            self,
            *,
            field: str = default_field,
            player_types: Tuple[str, ...] = ("user", "user"),
    ):
        super().__init__(field=field, player_types=player_types)

    @property
    def winners(self) -> Set[Player]:
        """Define and return the set of all players who draw solid line.

        If all characters on a "side" are the same and equal to label of
        player from :attr:`.players`, this player is added to the set of
        winners.

        """
        winners: Set[Player] = set()
        for side in self.field.all_sides:
            labels: str = ''.join(label for _, label in side)
            for player in self.players:
                if labels.count(player.label) == len(labels):
                    winners.add(player)
        return winners

    def refresh_status(self) -> None:
        """Change :attr:`._active` using Tic-Tac-Toe game rule to
        ``False`` if game cannot be continued.
        Print the status of the game, if necessary.

        """
        if (
                abs(
                    self.field.count(self.players[0].label)
                    - self.field.count(self.players[1].label)
                )
                > 1
        ):
            print("Impossible\n")
        else:
            winners: Set[Player] = self.winners
            if not winners:
                if self.field.count(EMPTY) > 0:
                    # game can continue
                    return
                else:  # self.field.count(EMPTY) == 0
                    print("Draw\n")
            elif len(winners) == 1:
                print(f"{winners.pop().label} wins\n")
            else:  # len(winners) > 1
                print("Impossible\n")
        self._active = False


class Reversi(Game):
    """Reversi class introduces Reversi game includes a CLI and supports
    human user and simple AI.

    For details see :class:`.Game`.

    """
    axis: ClassVar[bool] = True

    default_field: ClassVar[str] = (
            (EMPTY * 27) + 'XO' + (EMPTY * 6) + 'OX' + (EMPTY * 27)
    )

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": EasyPlayer,
    }

    directions: ClassVar[Set[Coordinate]] = {
        (0, 1),  # top
        (1, 1),  # right-top
        (1, 0),  # right and so on
        (1, -1),
        (0, -1),
        (-1, -1),
        (-1, 0),
        (-1, 1),
    }

    def __init__(
            self,
            *,
            field: str = default_field,
            player_types: Tuple[str, ...] = ("user", "user"),
    ):
        super().__init__(field=field, player_types=player_types)

    @property
    def winners(self) -> Set[Player]:
        """Define and return the set of all players who have the maximum
        count of player labels on the field.

        """
        player_scores: List[Tuple[int, Player]] = list()
        for player in self.players:
            player_scores.append((self.field.count(player.label), player))
        max_score = max(score for score, _ in player_scores)
        return set(player for score, player in player_scores if score == max_score)

    @property
    def possible_steps(self) -> Tuple[Coordinate, ...]:
        """Return indexes of empty cells as a tuple."""
        current_player_label: Label = self.players[0].label

        actual_possible_steps: List[Coordinate] = list()
        for coordinate in self.field.possible_steps:
            # Iterate over all directions where the cell occupied by
            # the opponent
            for shift in self.opponent_occupied_directions(coordinate=coordinate):
                analyzed_coordinate, label = self.field.get_offset_cell(
                    coordinate, shift
                )
                # Iterate over all cells in this direction
                while label and label not in (EMPTY, current_player_label):
                    analyzed_coordinate, label = self.field.get_offset_cell(
                        analyzed_coordinate, shift
                    )
                else:
                    # If behind the opponent's cells, the cell occupied
                    # by the current player is located
                    if label == current_player_label:
                        actual_possible_steps.append(coordinate)
                        # if successful, other directions can not be
                        # checked
                        break
        return tuple(actual_possible_steps)

    def opponent_occupied_directions(
            self, coordinate: Coordinate, player_label: str = ''
    ) -> Set[Coordinate]:
        """Determine the ``directions`` where adjacent cells are
        occupied by the opponent

        :param coordinate: The coordinate against which adjacent
         cells will be checked.
        :param player_label: Cells with this "friendly" label will
         not be considered an opponent.

        :return: set of offsets relative to the :param:`coordinate`.

        """
        if not player_label:
            player_label = self.players[0].label
        adjacent_label: str
        directions: List[Coordinate] = list()
        for shift in self.directions:
            _, adjacent_label = self.field.get_offset_cell(coordinate, shift)
            if adjacent_label and adjacent_label not in (EMPTY, player_label):
                directions.append(shift)
        return set(directions)

    def refresh_status(self) -> None:
        if not self.possible_steps:
            skipped_message: str = (
                f"Player '{self.players[0].label}' doesn't have possible steps!"
            )
            self.players.rotate(1)
            if not self.possible_steps:
                winners: Set[Player] = self.winners
                if len(winners) == 1:
                    print(f"{winners.pop().label} wins\n")
                else:  # len(winners) > 1
                    print("Draw\n")
                self._active = False
            else:
                print(skipped_message)

    def step(self, coordinate: Coordinate, **kwargs: Any) -> bool:
        if coordinate not in self.possible_steps:
            print("You cannot go here!")
            return False

        current_player_label: Label = self.players[0].label
        if self.field.label(coordinate=coordinate, label=current_player_label):
            for shift in self.opponent_occupied_directions(coordinate=coordinate):
                opponent_occupied_cells: List[Coordinate] = list()
                analyzed_coordinate, label = self.field.get_offset_cell(
                    coordinate, shift
                )
                # Iterate over all cells in this direction while label is
                # occupied opponent
                while label and label not in (EMPTY, current_player_label):
                    # Save the coordinate of the current occupied cell
                    opponent_occupied_cells.append(analyzed_coordinate)
                    analyzed_coordinate, label = self.field.get_offset_cell(
                        analyzed_coordinate, shift
                    )
                else:
                    # Label all opponent's cells if there is a cell behind
                    # them occupied by the current player
                    if label == current_player_label:
                        while opponent_occupied_cells:
                            self.field.label(
                                coordinate=opponent_occupied_cells.pop(),
                                label=current_player_label,
                                force=True,
                            )
            return True
        return False


def main(game_class: Type[Game]) -> None:
    command = input("Input command: ")
    while command != "exit":
        parameters = command.split()
        if (
                len(parameters) == 3
                and parameters[0] == "start"
                and parameters[1] in game_class.supported_players
                and parameters[2] in game_class.supported_players
        ):
            game = game_class(player_types=(parameters[1], parameters[2]))
            game.play()
        else:
            print("Bad parameters!")
        command = input("Input command: ")


if __name__ == '__main__':
    main(game_class=TicTacToe)
