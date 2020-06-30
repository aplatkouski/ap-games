from collections import deque
from random import choice
from typing import (Any, Callable, ClassVar, Deque, Dict, Iterable, List,
                    NoReturn, Set, Tuple, Type, Union, cast)

from typing_extensions import Literal

Coordinate = Tuple[int, int]
Indexes = Tuple[int, ...]
Side = Tuple[Indexes, str]
Sides = Tuple[Side, ...]
Strategy = Callable[[str], bool]
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
    undefined_cell: ClassVar[Tuple[Tuple[int], str]] = ((-1,), '')

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

        self._field: str = field
        self._gap: str = gap
        self._axis: bool = axis
        self.size: int = side

    def __str__(self) -> str:
        horizontal_border: str = (
                ('  ' if self._axis else '')
                + '-' * (self.size + len(self._gap) * (self.size + 1) + 2)
        )
        sparse_rows: List[str] = [
            (f'{self.size - num} ' if self._axis else '')
            + f"|{self._gap}"
            + f'{self._gap}'.join(list(row))
            for num, row in enumerate(dict(self.rows).values())
        ]
        field: str = f'{self._gap}|\n'.join(sparse_rows) + f'{self._gap}|'
        col_nums: str = f'{self._gap}'.join(map(str, range(1, self.size + 1)))
        battlefield: str = (
                f"{horizontal_border}\n"
                f"{field}\n"
                f"{horizontal_border}"
                + (f'\n   {self._gap}{col_nums}{self._gap}' if self._axis else '')
        )
        return battlefield

    def __iter__(self) -> Iterable[str]:
        return iter(self._field)

    def __len__(self) -> int:
        return len(self._field)

    def __call__(
            self, x: Union[int, Literal['*']], y: Union[int, Literal['*']]
    ) -> Side:
        """Return ``label`` or side (row or column) by coordinate as
        2-tuple.

        :param x: column number or literal ``'*'``. Column number
         starts with 1 from left side of field.
        :param y: row number or literal ``'*'`` means that it will
         return all rows. Row number starts with 1 from bottom of field.

        Note: Forbidden to pass ``column='*', row='*'`` together.

        :return: 2-tuple, where:
         * ``first item`` - is a tuple with the index(es) of each
           label of corresponding item, row or column.
         * ``second item`` - is a string with label(s) of corresponding
           cell, row or column.

        """
        if isinstance(y, int) and (1 <= y <= self.size):
            if isinstance(x, int) and (1 <= x <= self.size):
                index: int = self.coordinate_to_index(column=x, row=y)
                return (index,), self._field[index]
            elif x == '*':
                # For the user: row coordinate starts from 1 from bottom
                # to top;  In python row coordinate starts from 0 from
                # top to bottom, so: self.size - row
                return self.rows[self.size - y]
        elif y == '*' and isinstance(x, int) and (1 <= x <= self.size):
            # for the user: column coordinate starts from 1, in python
            # starts from 0
            return self.columns[x - 1]
        return self.undefined_cell

    @property
    def columns(self) -> Sides:
        """Return columns as a tuple, where each column is a 2-tuple.

        Details in :meth:`.SquareBattlefield.all_sides`.

        """
        indexes: Tuple[int, ...]
        labels: Tuple[str, ...]

        first_index_of_each_column = range(self.size)
        columns: List[Tuple[Indexes, str]] = list()
        for index in first_index_of_each_column:
            indexes, labels = zip(*self.cells[index:: self.size])
            columns.append((indexes, ''.join(labels)))
        return tuple(columns)

    @property
    def rows(self) -> Sides:
        """Return all rows as a tuple, where each row is a 2-tuple.

        Details in :meth:`.SquareBattlefield.all_sides`.

        """
        indexes: Tuple[int, ...]
        labels: Tuple[str, ...]

        first_index_of_each_row = range(0, self.size ** 2 - 1, self.size)
        rows: List[Tuple[Indexes, str]] = list()
        for index in first_index_of_each_row:
            indexes, labels = zip(*self.cells[index: index + self.size])
            rows.append((indexes, ''.join(labels)))
        return tuple(rows)

    @property
    def diagonals(self) -> Sides:
        """Return main and reverse diagonals as a tuple, where each
        diagonals is a 2-tuple.

        Details in :meth:`.SquareBattlefield.all_sides`.

        """
        indexes: Tuple[int, ...]
        labels: Tuple[str, ...]

        indexes, labels = zip(
            *(self.cells[i * self.size + i] for i in range(self.size))
        )
        main_diagonal: Side = (indexes, ''.join(labels))

        indexes, labels = zip(
            *(self.cells[i * self.size + self.size - 1 - i] for i in range(self.size))
        )
        reverse_diagonal: Side = (indexes, ''.join(labels))
        return main_diagonal, reverse_diagonal

    @property
    def all_sides(self) -> Sides:
        """Return all rows, columns and diagonals as a tuple, where
        each side is a 2-tuple:
         * ``first item`` - is a tuple with the indexes of each
           label of corresponding side.
         * ``second item`` - is a string with labels of corresponding
           side.

        """
        return self.rows + self.columns + self.diagonals

    @property
    def cells(self) -> Tuple[Tuple[int, str], ...]:
        """Return tuple of cells of the battelfield where each cell is
        a 2-tuple, where:
         * ``first item`` - is a index of the cell;
         * ``second item`` - is a label of the cell.

        """
        return tuple(enumerate(self._field))

    @property
    def possible_steps(self) -> Tuple[int, ...]:
        return tuple(index for index, cell in self.cells if cell == EMPTY)

    def count(self, label: str) -> int:
        """Returns the number of occurrences of a :param:`label`
        in the current battlefield.

        """
        return self._field.count(label)

    def coordinate_to_index(self, *, column: int, row: int) -> int:
        """Translates :param:`column` and :param:`row` to index.

        Where an example for a 3x3 ``self._field``::

            (1, 3) (2, 3) (3, 3)         0  1  2
            (1, 2) (2, 2) (3, 2)  ==>    3  4  5
            (1, 1) (2, 1) (3, 1)         6  7  8

        Return "-1" if it is impossible to convert.

        """
        if (1 <= column <= self.size) and (1 <= row <= self.size):
            return (column - 1) + self.size * (self.size - row)
        else:
            print(f'Coordinates should be from 1 to {self.size}!')
        return -1

    def index_to_coordinate(self, index: int) -> Coordinate:
        """Convert the index to coordinate.

        For details see :meth:`.coordinate_to_index`.

        """
        if 0 <= index < len(self._field):
            x, y = divmod(index, self.size)
            column = y + 1
            row = self.size - x
            return column, row
        return self.undefined_coordinate

    def get_offset_cell(
            self, coordinate: Coordinate, shift: Coordinate
    ) -> Tuple[Coordinate, str]:
        new_coordinate: Coordinate = cast(
            Tuple[int, int], tuple(x + y for x, y in zip(coordinate, shift))
        )
        label: str = self(*new_coordinate)[1]
        return new_coordinate, label

    def print(self) -> None:
        """Print battlefield"""
        print(self)

    def label(self, coordinate: Coordinate, label: str, *, force: bool = False) -> bool:
        """Mark position of battelfield with :param:`index` with
        :param:`label` if :param:`force` = ``True`` or occupied position
        is **empty** (``EMPTY``). Return ``True``, otherwise return
        ``False``.

        """
        column, row = coordinate
        index: int = self.coordinate_to_index(column=column, row=row)
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
         labeled with param:`label` if at least one of case is ``True``:
          * ``force=True``;
          * value in destination cell is ``EMPTY``and :param:`label` is
            equal "label" in cell with :param:`from_coordinate`.
        :param label: "label" that will be set.
        :param force: Default is ``False``. If ``force=True`` it doesn't
         matter if the position with ``to_coordinate`` is empty or it
         the position wit ``from_coordinate`` contains the same "label"
         as :param:`label`.

        """
        if force or label == self(*from_coordinate)[1]:
            result = self.label(to_coordinate, label, force=force)
            if result:
                self.label(from_coordinate, EMPTY, force=True)
            else:
                return result
        else:
            raise ValueError("You cannot move other player's 'label'")
        return False


class Player:
    """Abstract class :class:`.Player` introduces the player in the
    game.

    """

    def __init__(self, game: 'Game', label: Label) -> None:
        self.game = game
        self.label = label

    def __str__(self) -> str:
        return self.label

    def random_choice(self, field: SquareBattlefield) -> Coordinate:
        possible_steps: Tuple[int, ...] = self.game.possible_steps
        if possible_steps:
            return field.index_to_coordinate(choice(possible_steps))
        return field.undefined_coordinate

    def go(self, field: SquareBattlefield) -> Coordinate:
        """Return random coordinate of any empty (``EMTPY``) cell in
        ``field``.

        This method should be overridden by subclasses if there is a
        more complicated rule for determining coordinates.

        """
        return self.random_choice(field)


class HumanPlayer(Player):
    """HumanPlayer class introduces the user in the game with the
    ability to interact through the CLI.

    """

    def go(self, field: SquareBattlefield) -> Coordinate:
        """Read and return ``row`` and ``column`` coordinate from
        input.

        :return: Return :attr:`.SquareBattlefield.undefined_coordinate`
         if the coordinate are incorrect.

        """
        input_list = input("Enter the coordinate: ").split()
        if len(input_list) >= 2:
            x, y = input_list[:2]
        elif len(input_list) == 1:
            x, y = input_list[0], EMPTY
        else:  # input string is empty
            x = y = EMPTY

        if x.isdigit() and y.isdigit():
            return int(x), int(y)
        else:
            print('You should enter numbers!')
        return field.undefined_coordinate


class EasyPlayer(Player):
    """EasyPlayer class introduces an AI player in the game with ability
    to select a random index of any empty (``EMPTY``) cell on the
    battelfield.

    """

    def go(self, field: SquareBattlefield) -> Coordinate:
        """Return random coordinate of any empty (' ') cell in
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
        """Iterates over all possible combinations of sides (rows,
        columns and diagonals) and check them with :param:`func`.

        If :param:`func` return ``True`` (strategy can be applied to
        side) return coordinate of empty cell in side as next move
        option.  Otherwise return
        :attr:`.SquareBattlefield.undefined_coordinate` if the
        coordinate are incorrect.

        """
        for indexes, side in field.all_sides:
            if func(side):
                return field.index_to_coordinate(indexes[side.index(EMPTY)])
        return field.undefined_coordinate

    def _try_to_win(self, side: str) -> bool:
        """Strategy: If player can win, return ``True``, otherwise
        return ``False``.

        :param side: any side (row, column or diagonal) as string.

        """
        if side.count(EMPTY) == 1 and side.count(self.label) == (len(side) - 1):
            return True
        return False

    def _try_not_to_lose(self, side: str) -> bool:
        """Strategy: If player can lose, return ``True``, otherwise
        return ``False``.

        :param side: any side (row, column or diagonal) as string.

        """
        if side.count(EMPTY) == 1 and side.find(self.label) == -1:
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

    :param field: String contains :attr:`.Game.field_space`
     symbols from set :attr:`.Game.labels` and symbols '_' or ' ' mean
     an empty cell.
    :param player_types: Tuple of strings from
     :attr:`.Game.supported_players` that determine type and count of
     players. Length of tuple must be between :attr:`.min_players` and
     :attr:`max_players`.

    :ivar _active: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar field: The battlefield as as :class:`.SquareBattlefield`.
    :ivar players: The queue with players. Player is an instance of
     :class:`.Player`.


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

        players: Set[Player] = set()
        for num, player_type in enumerate(player_types):
            label: Label = self.labels[num]
            players.add(self.supported_players[player_type](game=self, label=label))

        field_without_underscore = field.replace('_', EMPTY)
        if not frozenset(field_without_underscore).issubset({*self.labels, EMPTY}):
            raise ValueError

        self._active: bool = True
        self.players: Deque[Player] = deque(players)
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
        raise NotImplementedError

    @property
    def possible_steps(self) -> Tuple[int, ...]:
        """Return indexes of empty cells as a tuple.

        This method should be overridden by subclasses if there is a
        more complicated rule for determining which cell is empty.

        """
        return self.field.possible_steps

    def refresh_status(self) -> None:
        raise NotImplementedError

    def step(self, coordinate: Coordinate, **kwargs: Any) -> bool:
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
    """TicTacToe class introduces Tic-Tac-Toe game and supports CLI."""

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

        If all characters on a "side" are the same and equal to ``label``
        of :class:`.Player`, then current player is added to the set of
        winners.

        """
        winners: Set[Player] = set()
        for _, side in self.field.all_sides:
            for player in self.players:
                if frozenset(side).issubset({player.label}):
                    winners.add(player)
        return winners

    def refresh_status(self) -> None:
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
    axis: ClassVar[bool] = True

    default_field: ClassVar[str] = (
            (EMPTY * 27) + 'XO' + (EMPTY * 6) + 'OX' + (EMPTY * 27)
    )

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": EasyPlayer,
    }

    directions: ClassVar[Tuple[Coordinate, ...]] = (
        (0, 1),  # top
        (1, 1),  # right-top
        (1, 0),  # right and so on
        (1, -1),
        (0, -1),
        (-1, -1),
        (-1, 0),
        (-1, 1),
    )

    def __init__(
            self,
            *,
            field: str = default_field,
            player_types: Tuple[str, ...] = ("user", "user"),
    ):
        super().__init__(field=field, player_types=player_types)

    @property
    def winners(self) -> Set[Player]:
        """Define and return the set of all players who has maximum count
        of "label".

        """
        player_scores: List[Tuple[int, Player]] = list()
        for player in self.players:
            player_scores.append((self.field.count(player.label), player))
        player_scores.sort(reverse=True)
        max_score = max(score for score, _ in player_scores)
        return set(player for score, player in player_scores if score == max_score)

    @property
    def possible_steps(self) -> Tuple[int, ...]:
        """Return indexes of empty cells as a tuple."""
        current_player_label: Label = self.players[0].label

        possible_steps: Tuple[int, ...] = self.field.possible_steps
        actual_possible_steps: List[int] = list()
        for index in possible_steps:
            is_successful: bool = False
            coordinate: Coordinate = self.field.index_to_coordinate(index)
            directions: List[Coordinate] = self.enemy_occupied_directions(
                coordinate=coordinate
            )
            for shift in directions:
                analyzed_coordinate, label = self.field.get_offset_cell(
                    coordinate, shift
                )
                while label and label not in (EMPTY, current_player_label):
                    analyzed_coordinate, label = self.field.get_offset_cell(
                        analyzed_coordinate, shift
                    )
                else:
                    if label == current_player_label:
                        is_successful = True
            if is_successful:
                actual_possible_steps.append(index)
        return tuple(actual_possible_steps)

    def enemy_occupied_directions(
            self, coordinate: Coordinate, player_label: str = ''
    ) -> List[Coordinate]:
        """Determine the ``directions`` where adjacent cells are
        occupied by the enemy

        :param coordinate: The coordinate against which adjacent
         cells will be checked.
        :param player_label: Cells with this "friendly" label will
         not be considered an enemy.

        :return: list of offsets relative to the ``coordinate``.

        """
        if not player_label:
            player_label = self.players[0].label
        adjacent_label: str
        directions: List[Coordinate] = list()
        for shift in self.directions:
            _, adjacent_label = self.field.get_offset_cell(coordinate, shift)
            if adjacent_label and adjacent_label not in (EMPTY, player_label):
                directions.append(shift)
        return directions

    def refresh_status(self) -> None:
        if not self.possible_steps:
            skipped_message: str = f"Player '{self.players[0].label}' doesn't have possible steps!"
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
        current_player: Player = self.players[0]
        is_successful: bool = False
        directions: List[Coordinate] = self.enemy_occupied_directions(
            coordinate=coordinate
        )
        while directions:
            shift = directions.pop()
            enemy_occupied_cells: List[Coordinate] = list()
            # extract first cell in this direction
            analyzed_coordinate, label = self.field.get_offset_cell(coordinate, shift)
            # Iterate over all cells in this direction
            while label and label not in (EMPTY, current_player.label):
                # save the coordinate of the current occupied cell
                enemy_occupied_cells.append(analyzed_coordinate)
                # extract next cell in this direction
                analyzed_coordinate, label = self.field.get_offset_cell(
                    analyzed_coordinate, shift
                )
            else:
                # If the last cell is occupied by the current player
                # label all ``enemy_occupied_cells`` with
                # ``player.label``
                if label == current_player.label:
                    is_successful = True
                    while enemy_occupied_cells:
                        self.field.label(
                            coordinate=enemy_occupied_cells.pop(),
                            label=current_player.label,
                            force=True,
                        )
        if is_successful:
            self.field.label(coordinate=coordinate, label=current_player.label)
        # else:
        #     print("You cannot go here!")
        return is_successful


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
