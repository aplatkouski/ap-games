from __future__ import annotations
from collections import deque
from functools import cached_property
from itertools import cycle
from random import choice
from typing import ClassVar
from typing import Deque
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type

import logging.handlers
import os

from typing_extensions import Literal

Coordinate = NamedTuple("Coordinate", [("x", int), ("y", int)])
Cell = NamedTuple("Cell", [("coordinate", Coordinate), ("label", str)])
Side = Tuple[Cell, ...]

Step = NamedTuple(
    "Step", [("coordinate", Coordinate), ("score", int), ("percentage", int)]
)
GameStatus = NamedTuple("GameStatus", [("active", bool), ("message", str)])

Label = Literal["X", "O"]
SupportedPlayers = Dict[str, Type["Player"]]

EMPTY: Literal[" "] = " "


handler = logging.handlers.WatchedFileHandler(
    os.environ.get("TICTACTOE_LOGFILE", "./tictactoe.log")
)
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("TICTACTOE_LOGLEVEL", "ERROR"))
log.addHandler(handler)


class SquareGameboard:
    """Implementation square game board with size from 2 to 9.

    :param surface: The surface or board, represented as a string, where
     each character is mapped to a cell left to right top to bottom.
    :param gap: ``" "`` by default.  Defines the gap that will be
     printed between cells in a row.
    :param axis: ``False`` by default.  If ``True`` print axis.

    :ivar _size: The size of gameboard from 2 to 9.

    """

    undefined_coordinate: ClassVar[Coordinate] = Coordinate(x=-1, y=-1)
    undefined_cell: ClassVar[Cell] = Cell(coordinate=undefined_coordinate, label="")

    def __init__(
        self, *, surface: str = EMPTY * 9, gap: str = " ", axis: bool = False
    ) -> None:

        size = int(len(surface) ** (1 / 2))
        if 1 > size > 9:
            raise ValueError("The size of the gameboard must be between 2 and 9!")
        if size ** 2 != len(surface):
            raise ValueError(
                f"The gameboard must be square ({size}^2 != {len(surface)})!"
            )
        self._size: int = size

        self._surface: str = surface
        self._gap: str = gap
        self._axis: bool = axis

    def __str__(self) -> str:
        horizontal_border: str = (
            ("  " if self._axis else "")
            + "-" * (self._size + len(self._gap) * (self._size + 1) + 2)
        )

        surface: str = f"\n".join(
            (f"{self._size - num} " if self._axis else "")
            + f"|{self._gap}"
            + f"{self._gap}".join(cell.label for cell in row)
            + f"{self._gap}|"
            for num, row in enumerate(self.rows)
        )

        col_nums: str = f"{self._gap}".join(map(str, range(1, self._size + 1)))

        board: str = (
            f"{horizontal_border}\n"
            f"{surface}\n"
            f"{horizontal_border}"
            + (f"\n   {self._gap}{col_nums}{self._gap}" if self._axis else "")
        )
        return board

    def __iter__(self) -> Iterable[str]:
        return iter(self._surface)

    def __len__(self) -> int:
        return len(self._surface)

    def __call__(self, x: int, y: int) -> Cell:
        """Return cell by coordinates as namedtuple with two fields:
        ``coordinate`` and ``label``.

        :param x: Column number starts with 1 from left side of
         gameboard.
        :param y: Row number starts with 1 from bottom of gameboard.

        :return: The cell by the coordinates or
         :attr:`.SquareGameboard.undefined_cell` if coordinates are
         incorrect.

        """
        if (1 <= y <= self._size) and (1 <= x <= self._size):
            index: int = self._coordinate_to_index(x=x, y=y)
            return Cell(coordinate=Coordinate(x, y), label=self._surface[index])
        return self.undefined_cell

    @cached_property
    def size(self) -> int:
        return self._size

    @property
    def surface(self) -> str:
        return self._surface

    @property
    def columns(self) -> Tuple[Side, ...]:
        """Return all columns of gameboard as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        first_index_of_each_column = range(self._size)
        columns: List[Side] = list()
        for index in first_index_of_each_column:
            columns.append(self.cells[index :: self._size])
        return tuple(columns)

    @property
    def rows(self) -> Tuple[Side, ...]:
        """Return all rows of gameboard as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        first_index_of_each_row = range(0, self._size ** 2 - 1, self._size)
        rows: List[Side] = list()
        for index in first_index_of_each_row:
            rows.append(self.cells[index : index + self._size])
        return tuple(rows)

    @property
    def diagonals(self) -> Tuple[Side, ...]:
        """Return main and reverse diagonals as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        main_diagonal: Side = tuple(
            self.cells[i * (self._size + 1)] for i in range(self._size)
        )
        reverse_diagonal: Side = tuple(
            self.cells[(i + 1) * (self._size - 1)] for i in range(self._size)
        )
        return main_diagonal, reverse_diagonal

    @property
    def all_sides(self) -> Tuple[Side, ...]:
        """Return all rows, columns and diagonals as a tuple of all
        sides.  Where each side is a tuple of cells of the corresponding
        side.

        """
        return self.rows + self.columns + self.diagonals

    @property
    def cells(self) -> Tuple[Cell, ...]:
        """Return tuple of cells of the gameboard where each cell is
        a namedtuple with two fields:
         * ``coordinate``;
         * ``label`` (as string).

        """
        return tuple(
            Cell(coordinate=self._index_to_coordinate(index), label=label)
            for index, label in enumerate(self._surface)
        )

    @property
    def available_steps(self) -> Tuple[Coordinate, ...]:
        """Return coordinates of all available steps.  By default,
        coordinates of all ``EMPTY`` cells.

        """
        return tuple(cell.coordinate for cell in self.cells if cell.label == EMPTY)

    def count(self, label: str) -> int:
        """Returns the number of occurrences of a :param:`label` on the
        gameboard.

        """
        return self._surface.count(label)

    def _coordinate_to_index(self, x: int, y: int) -> int:
        """Translates the cell coordinates represented by :param:`x` and
        :param:`y` into the index of this cell.

        :param x: Column number from left to right;
        :param y: Row number from bottom to top.

        Where an example for a 3x3 ``self._surface``::

            (1, 3) (2, 3) (3, 3)         0  1  2
            (1, 2) (2, 2) (3, 2)  ==>    3  4  5
            (1, 1) (2, 1) (3, 1)         6  7  8

        :return: the index of the corresponding cell between 1 and the
        size of the gameboard, or "-1" if the coordinates are incorrect.

        """
        if (1 <= x <= self._size) and (1 <= y <= self._size):
            return (x - 1) + self._size * (self._size - y)
        else:
            print(f"Coordinates should be from 1 to {self._size}!")
        return -1

    def _index_to_coordinate(self, index: int) -> Coordinate:
        """Convert the index to the coordinate.

        For details see :meth:`.SquareGameboard._coordinate_to_index`.

        """
        if 0 <= index < len(self._surface):
            x, y = divmod(index, self._size)
            column = y + 1
            row = self._size - x
            return Coordinate(column, row)
        return self.undefined_coordinate

    def get_offset_cell(self, coordinate: Coordinate, shift: Coordinate) -> Cell:
        """Return "Cell" (as tuple of coordinate and label) by
        coordinate calculated as algebraic sum of vectors:
        :param:`coordinate` and :param:`shift`.

        """
        return self(x=coordinate.x + shift.x, y=coordinate.y + shift.y)

    def print(self, indent: str = "") -> None:
        """Print gameboard."""
        if indent:
            result: str = "\n".join(f"{indent}{line}" for line in str(self).split("\n"))
        else:
            result = str(self)
        log.info(result)
        print(result)

    def label(self, coordinate: Coordinate, label: str, *, force: bool = False,) -> int:
        """Label cell of the gameboard with the ``coordinate``.

        :param coordinate: Position of cell as instance of namedtuple
         Coordinate(x, y).
        :param label: New label.  It will be set if ``force=True`` or
         cell with :param:`coordinate` is **empty** (``EMPTY``).
        :param force: ``False`` by default.  When ``True`` it doesn't
         matter if cell is **empty** or not.

        :return: count of labeled cell with :param:`label`.

        """
        index: int = self._coordinate_to_index(*coordinate)
        if 0 <= index < len(self._surface):
            if force or self._surface[index] == EMPTY:
                self._surface = label.join(
                    (self._surface[:index], self._surface[index + 1 :])
                )
                return 1
            print("This cell is occupied! Choose another one!")
        return 0


class Player:
    """Class introduces the player in the game."""

    def __init__(self, type_: str, /, *, game: Game, label: Label) -> None:
        self.type: str = type_
        self._game: Game = game
        self._label: Label = label

    def __str__(self) -> str:
        return self._label

    @cached_property
    def game(self) -> Game:
        return self._game

    @cached_property
    def label(self) -> Label:
        return self._label

    def _random_coordinate(self) -> Coordinate:
        """Return the coordinates of randomly selected available cell on
        the gameboard.

        """
        available_steps: Tuple[Coordinate, ...] = self.game.available_steps()
        if available_steps:
            return choice(available_steps)
        return self.game.gameboard.undefined_coordinate

    def go(self) -> Coordinate:
        """Return the randomly selected coordinates.

        This method should be overridden by subclasses if there is a
        more complex rule for determining coordinates.

        """
        return self._random_coordinate()


class HumanPlayer(Player):
    """HumanPlayer class introduces the user in the game with the
    ability to interact through the CLI.

    """

    def go(self) -> Coordinate:
        """Read coordinate from the input and return them.

        :return: Return :attr:`.SquareGameboard.undefined_coordinate`
         if the coordinate is incorrect.

        """
        input_list = input("Enter the coordinate: ").split()
        if len(input_list) >= 2:
            x, y = input_list[:2]
        else:
            x, y = EMPTY, EMPTY
        if x.isdigit() and y.isdigit():
            return Coordinate(int(x), int(y))
        print("You should enter numbers!")
        return self.game.gameboard.undefined_coordinate


class AIPlayer(Player):

    max_depth: ClassVar[Dict[str, int]] = {
        "easy": 0,
        "medium": 2,
        "hard": 4,
    }

    def _get_terminal_score(
        self, *, depth: int, gameboard: SquareGameboard, player: Player
    ) -> Tuple[int, int]:
        """Return ``score`` and ``percentage`` of terminal state."""

        score: int
        """In the minimax algorithm, it doesn't matter how many ways
        to win AI at the end of the game. Therefore, the AI
        "stops fighting" and​is not trying to "steal" one of them.
        With the variable ``percentage``, the case with two
        possible steps to lose are worse than one.
        This is especially important if the "depth" of analysis is
        limited.

        Run example below with and without ``percentage`` once or twice:
        TicTacToe(surface="X_OXX_O__", player_types=("easy", "hard")).play()

        hint: "hard" select cell randomly from all empty cells and
        can lose to "easy" without ``percentage``."""
        percentage: int
        """In the minimax algorithm, it doesn't matter when you lose:
        now or later. Therefore, the AI "stops fighting" if it
        in any case loses the next steps, regardless of how it takes
        the step now. In this case, the AI considers that all the
        steps are the same bad, but this is wrong.
        Because the adversary can make a mistake, and adding the
        variable ``factor`` allows the AI to use a possible
        adversary errors in the future.
        With the ``factor``, losing now is worse than losing later.
        Therefore, the AI is trying not to "give up" now and wait
        for better chances in the future.
        This is especially important if the "depth" of analysis is
        limited.

        Run example below with and without ``factor`` once or twice:
        TicTacToe(surface="X_OX_____", player_types=("easy", "hard")).play()

        hint: "hard" select cell randomly from all empty cells and
        can lose to "easy" without ``factor``."""
        factor: int = 1

        if self.game.get_status(gameboard=gameboard, player=player).active:
            if depth < self.max_depth[self.type]:
                _, score, percentage = self._minimax(
                    depth=depth + 1, gameboard=gameboard, player=player
                )
            else:
                score = self.game.get_score(gameboard=gameboard, player=self)
                percentage = 100
        else:
            factor *= self.max_depth[self.type] + 1 - depth
            score = self.game.get_score(gameboard=gameboard, player=self)
            percentage = 100
        return score * factor, percentage

    def _get_next_player(self, current_player: Player) -> Player:
        players_cycle: Iterator[Player] = cycle(self.game.players)
        while next(players_cycle) != current_player:
            pass
        return next(players_cycle)

    def _extract_desired_steps(
        self, depth: int, steps: List[Step], player: Player
    ) -> List[Step]:
        if player == self:
            score_func = max
        else:
            score_func = min

        desired_score: int = score_func(step.score for step in steps)
        desired_steps: List[Step] = [
            step for step in steps if step.score == desired_score
        ]
        log.debug(
            "\t" * depth + f"desired score steps ({score_func}) -> {desired_steps}"
        )
        return desired_steps

    def _extract_most_likely_steps(
        self, depth: int, steps: List[Step], player: Player
    ) -> List[Step]:
        # Note: all Steps on this stage have the same score
        desired_score: int = steps[0].score

        if (desired_score >= 0 and player == self) or (
            desired_score < 0 and player != self
        ):
            # maximize the probability of self own winning or adversary
            # losing
            percentage_func = max
        else:
            percentage_func = min
        desired_percentage: int = percentage_func(step.percentage for step in steps)
        most_likely_steps: List[Step] = [
            step for step in steps if step.percentage == desired_percentage
        ]
        log.debug(
            "\t" * depth
            + f"desired percentage steps ({percentage_func}) -> "
            + str(most_likely_steps)
        )
        return most_likely_steps

    def _minimax(
        self,
        *,
        depth: int,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> Step:
        """Algorithm:

        1. Go through available spots on the board;
        2. Return a value (score) if a terminal state is found
           (:meth:`._get_terminal_score`);
        3. or call the minimax function on each available spot
           (recursion).
        4. Evaluate returning values from function calls
           (:meth:`._extract_desired_steps` and
           :meth:`._extract_most_likely_steps`);
        5. And return the best value (Step).

        TODO: swap the first and second item.
         In the current implementation, there may be an error if
         running the method with the ``gameboard`` without the available
         steps.

        """
        if gameboard is None:
            gameboard = self.game.gameboard
        if player is None:
            player = self

        steps: List[Step] = list()
        for coordinate in player.game.available_steps(
            gameboard=gameboard, player=player
        ):
            fake_gameboard: SquareGameboard = SquareGameboard(
                surface=gameboard.surface, gap=self.game.gap, axis=self.game.axis
            )
            self.game.step(coordinate, gameboard=fake_gameboard, player=player)

            log.debug("\n " + ("\t" * depth) + f"[{player.label}] {coordinate}")
            log.debug(
                "\n".join(
                    '\t' * depth + line for line in str(fake_gameboard).split("\n")
                )
            )

            next_player = self._get_next_player(current_player=player)

            terminal_score, percentage = self._get_terminal_score(
                depth=depth, gameboard=fake_gameboard, player=next_player
            )
            steps.append(Step(coordinate, terminal_score, percentage))

        desired_steps: List[Step] = self._extract_desired_steps(
            depth=depth, steps=steps, player=player
        )

        most_likely_steps: List[Step] = self._extract_most_likely_steps(
            depth=depth, steps=desired_steps, player=player
        )

        step: Step = choice(most_likely_steps)
        # compute and replace ``percentage`` in the selected step
        step = step._replace(percentage=int(len(desired_steps) / len(steps) * 100))
        log.debug("\t" * depth + f"selected step: {step}")

        return step

    def go(self) -> Coordinate:
        print(f'Making move level "{self.type}" [{self.label}]')

        depth: int = 0
        if depth < self.max_depth[self.type]:
            return self._minimax(depth=depth + 1).coordinate
        return self._random_coordinate()


class Game:
    """Game class.

    :param surface: String contains symbols from set :attr:`.Game.labels`
     and symbols "_" or " " mean an empty cell.
    :param player_types: A tuple of strings with two elements from
     :attr:`.Game.supported_players.keys` which determine the types of
     players.

    :ivar status: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar gameboard: The gameboard as instance of
     :class:`.SquareGameboard`.
    :ivar players: The queue with players.  Player is an instance of
     :class:`.Player`.  Player with index ``0`` is a current player.


    """

    _X: Literal["X"] = "X"
    _O: Literal["O"] = "O"
    labels: ClassVar[Tuple[Label, ...]] = (_X, _O)

    default_surface: ClassVar[str] = EMPTY * 9
    axis: ClassVar[bool] = False
    gap: ClassVar[str] = " "

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": AIPlayer,
        "medium": AIPlayer,
        "hard": AIPlayer,
    }

    def __init__(
        self, *, surface: str = '', player_types: Tuple[str, ...] = ("user", "user"),
    ):
        if not surface:
            surface = self.default_surface

        if len(player_types) != 2:
            raise ValueError(f"The number of players should be 2!")

        self.players: Deque[Player] = deque()
        for num, player_type in enumerate(player_types):
            label: Label = self.labels[num]
            self.players.append(
                self.supported_players[player_type](player_type, game=self, label=label)
            )

        surface_without_underscore = surface.replace("_", EMPTY)
        if not frozenset(surface_without_underscore).issubset({*self.labels, EMPTY}):
            raise ValueError(
                f"Gameboard must contain only ' ', '_' and symbols from {self.labels}."
            )

        self.status: GameStatus = GameStatus(active=True, message="")
        self.gameboard: SquareGameboard = SquareGameboard(
            surface=surface_without_underscore, gap=self.gap, axis=self.axis
        )
        # move the player with the least number of "label" to the front
        # of the queue
        while self.gameboard.count(self.players[0].label) > self.gameboard.count(
            self.players[1].label
        ):
            self.players.rotate(1)

    def winners(self, *, gameboard: Optional[SquareGameboard] = None) -> Set[Player]:
        """Must be overridden by subclasses and must return
        a set of instance(s) ot the :class:`.Player` defined as
        winner(s).

        :param gameboard: Optional.  If undefined, use
         :attr:`.Game.gameboard`.

        """
        return set()

    def available_steps(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> Tuple[Coordinate, ...]:
        """Return a tuple of coordinates of all available cells on the
        :param:`gameboard` for the :param:`player`.

        This method should be overridden by subclasses if there is a
        more complex rule for determining which cell is available.

        :param gameboard: Optional.  If undefined, use
         :attr:`.Game.gameboard`.
        :param player: Optional.  If undefined, user current user
         :attr:`.Game.players[0]`.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]
        return gameboard.available_steps

    def get_score(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> int:

        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        winners: Set[Player] = self.winners(gameboard=gameboard)
        if len(winners) == 1:
            if player in winners:
                return 1
            else:
                return -1
        else:  # len(winners) != 1
            return 0

    def get_status(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> GameStatus:
        """Return the current game status calculated for the
        :param:`gameboard` in accordance with the game rule.

        :param gameboard: Optional.  If undefined, use
         :attr:`.Game.gameboard`.
        :param player: Optional.  If undefined, user current user
         :attr:`.Game.players[0]`.

        :return: Game status as the instance of namedtuple
         ``GameStatus`` with two fields: ``active`` and ``message``.
         ``GameStatus.active == False`` if game cannot be continued.

        Must be overridden by subclasses if there is a more complex rule
        for calculating game status.

        Note: If there is no available step for the ``player`` and the
        game cannot be continued, the method must return
        ``GameStatus.active == False``.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        if self.available_steps(gameboard=gameboard, player=player):
            return GameStatus(active=True, message="")
        return GameStatus(active=False, message="")

    def step(
        self,
        coordinate: Coordinate,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> int:
        """Change the label of the cell with ``coordinate`` on the
        gameboard.

        :param coordinate: coordinate of cell which player label.
        :param gameboard: Optional.  If undefined, use
         :attr:`.Game.gameboard`.
        :param player: Optional.  If undefined, user current user
         :attr:`.Game.players[0]`.

        This method should be overridden by subclasses if there is a
        more complex rule for labeling cell(s) in ``gameboard``.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        if coordinate not in self.available_steps(gameboard=gameboard):
            print("You cannot go here!")
            return 0
        return gameboard.label(coordinate, player.label)

    def play(self) -> None:
        """The main public interface that run the game."""
        self.gameboard.print()
        self.status = self.get_status()
        while self.status.active:
            coordinate: Coordinate = self.players[0].go()
            if self.step(coordinate=coordinate):
                log.info(str(self.gameboard))
                self.gameboard.print()
                self.players.rotate(1)
                self.status = self.get_status()
                if self.status.message:
                    print(self.status.message)


class TicTacToe(Game):
    """TicTacToe class introduces Tic-Tac-Toe game.

    For details see :class:`.Game`.

    """

    def winners(self, *, gameboard: Optional[SquareGameboard] = None) -> Set[Player]:
        """Define and return the set of all players who draw solid line.

        If all characters on a "side" are the same and equal to the
        label of player from :attr:`.players`, this player is added to
        the set of winners.

        :param gameboard: Optional.  If undefined, use
         :attr:`.Game.gameboard`.

        """
        if gameboard is None:
            gameboard = self.gameboard

        winners: Set[Player] = set()
        for player in self.players:
            for side in gameboard.all_sides:
                if all(cell.label == player.label for cell in side):
                    winners.add(player)
                    break
        return winners

    def get_status(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> GameStatus:
        """Return the Tic-Tac-Toe game status calculated for the
        :param:`gameboard` in accordance with the game rule.

        :return: Game status as the instance of namedtuple
         ``GameStatus`` with two fields: ``active`` and ``message``.
         ``GameStatus.active == False`` if game cannot be continued.

        """
        if gameboard is None:
            gameboard = self.gameboard

        game_status: GameStatus = GameStatus(active=True, message="")
        if (
            abs(
                gameboard.count(self.players[0].label)
                - gameboard.count(self.players[1].label)
            )
            > 1
        ):
            game_status = GameStatus(False, "Impossible\n")
        else:
            winners: Set[Player] = self.winners(gameboard=gameboard)
            if not winners and not self.available_steps(gameboard=gameboard):
                game_status = GameStatus(False, "Draw\n")
            elif len(winners) == 1:
                game_status = GameStatus(False, f"{winners.pop().label} wins\n")
            elif len(winners) > 1:
                game_status = GameStatus(False, "Impossible\n")
        return game_status


class Reversi(Game):
    """Reversi game supports human user and three types of AI (easy,
    medium, hard).

    For details see :class:`.Game`.

    """

    axis: ClassVar[bool] = True

    default_surface: ClassVar[str] = (
        (EMPTY * 27) + "XO" + (EMPTY * 6) + "OX" + (EMPTY * 27)
    )

    directions: ClassVar[Set[Coordinate]] = {
        Coordinate(0, 1),  # top
        Coordinate(1, 1),  # right-top
        Coordinate(1, 0),  # right and so on
        Coordinate(1, -1),
        Coordinate(0, -1),
        Coordinate(-1, -1),
        Coordinate(-1, 0),
        Coordinate(-1, 1),
    }

    def winners(self, *, gameboard: Optional[SquareGameboard] = None) -> Set[Player]:
        """Define and return the set of all players who have the maximum
        count of player labels on the gameboard.

        """
        if gameboard is None:
            gameboard = self.gameboard
        # TODO: give a turn to another player if the current player
        #   cannot go
        # if any(self.available_steps(gameboard=gameboard, player=player) for player in self.players):
        #     # winner undefined if there's at least one player who can go
        #     return set()
        player_scores: List[Tuple[Player, int]] = [
            (player, gameboard.count(player.label)) for player in self.players
        ]
        max_score = max(score for _, score in player_scores)
        return set(player for player, score in player_scores if score == max_score)

    def available_steps(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> Tuple[Coordinate, ...]:
        """Return coordinates of only that cells where ``player`` can
        flip at least one another player label using Reversi game's
        rule.

        TODO: add max priority to corner cells.

        """

        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        current_player_label: Label = player.label

        actual_available_steps: List[Coordinate] = list()
        for coordinate in gameboard.available_steps:
            # Iterate over all directions where the cell occupied by
            # the adversary
            for shift in self.adversary_occupied_directions(
                coordinate=coordinate,
                gameboard=gameboard,
                player_label=current_player_label,
            ):
                analyzed_coordinate, label = gameboard.get_offset_cell(
                    coordinate, shift
                )
                # Iterate over all cells in this direction
                while label and label not in (EMPTY, current_player_label):
                    analyzed_coordinate, label = gameboard.get_offset_cell(
                        analyzed_coordinate, shift
                    )
                else:
                    # Check there is the cell occupied by the current
                    # player behind the adversary cells
                    if label == current_player_label:
                        actual_available_steps.append(coordinate)
                        # if successful, other directions can be not
                        # checked
                        break
        return tuple(actual_available_steps)

    def adversary_occupied_directions(
        self,
        coordinate: Coordinate,
        gameboard: Optional[SquareGameboard] = None,
        player_label: str = "",
    ) -> Set[Coordinate]:
        """Determine the ``directions`` where adjacent cells are
        occupied by the adversary.

        :param coordinate: The coordinate against which adjacent
         cells will be checked.
        :param gameboard: Optional.  If undefined, use
         :attr:`.Game.gameboard`.
        :param player_label: Cells with this "friendly" label will
         not be considered an adversary.

        :return: Set of offsets relative to the :param:`coordinate`.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if not player_label:
            player_label = self.players[0].label

        adjacent_label: str
        directions: List[Coordinate] = list()
        for shift in self.directions:
            _, adjacent_label = gameboard.get_offset_cell(coordinate, shift)
            if adjacent_label and adjacent_label not in (EMPTY, player_label):
                directions.append(shift)
        return set(directions)

    def get_score(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> int:

        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        player_score: int = 0
        other_players_score: int = 0
        for p in self.players:
            if p == player:
                player_score += gameboard.count(p.label)
            else:
                other_players_score += gameboard.count(p.label)
        return player_score - other_players_score

    def get_status(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> GameStatus:
        """Return the Reversi game status calculated for the
        :param:`gameboard` in accordance with the game rule.

        :return: Game status as the instance of namedtuple
         ``GameStatus`` with two fields: ``active`` and ``message``.
         ``GameStatus.active == False`` if game cannot be continued.

        TODO: implement the rotation of the players, if only the current
         player doesn't have available steps.

        Draft::

            if not self.available_steps(gameboard=gameboard, player=self.players[1]):
                pass
            else:
                print(f"Player '{self.players[0].label}' doesn't have available steps!")
                self.players.rotate(1)

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        game_status = GameStatus(active=True, message="")

        if not self.available_steps(gameboard=gameboard, player=player):
            winners: Set[Player] = self.winners(gameboard=gameboard)
            if len(winners) == 1:
                game_status = GameStatus(False, f"{winners.pop().label} wins\n")
            elif len(winners) > 1:
                game_status = GameStatus(False, "Draw\n")
            else:  # len(winners) == 0
                game_status = GameStatus(False, "Impossible\n")
        return game_status

    def step(
        self,
        coordinate: Coordinate,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> int:
        if gameboard is None:
            gameboard = self.gameboard
        if player is None:
            player = self.players[0]

        score: int = 0

        if coordinate not in self.available_steps(gameboard=gameboard, player=player):
            print("You cannot go here!")
            return score

        current_player_label: Label = player.label
        score += gameboard.label(coordinate=coordinate, label=current_player_label)
        if score:
            for shift in self.adversary_occupied_directions(
                coordinate=coordinate, gameboard=gameboard, player_label=player.label
            ):
                adversary_occupied_cells: List[Coordinate] = list()
                analyzed_coordinate, label = gameboard.get_offset_cell(
                    coordinate, shift
                )
                # Iterate over all cells in this direction while label is
                # occupied adversary
                while label and label not in (EMPTY, current_player_label):
                    # Save the coordinate of the current occupied cell
                    adversary_occupied_cells.append(analyzed_coordinate)
                    analyzed_coordinate, label = gameboard.get_offset_cell(
                        analyzed_coordinate, shift
                    )
                else:
                    # Label all adversary cells if there is a cell behind
                    # them occupied by the current player
                    if label == current_player_label:
                        while adversary_occupied_cells:
                            score += gameboard.label(
                                coordinate=adversary_occupied_cells.pop(),
                                label=current_player_label,
                                force=True,
                            )
        return score


def cli(game_class: Type[Game] = TicTacToe) -> None:
    command: str = input("Input command: ")
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


if __name__ == "__main__":
    # cli()
    cli(game_class=Reversi)
