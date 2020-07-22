from __future__ import annotations

import logging
from collections import defaultdict
from collections import deque
from itertools import cycle
from typing import TYPE_CHECKING

from ap_games.ap_types import EMPTY
from ap_games.ap_types import GameStatus
from ap_games.ap_types import O
from ap_games.ap_types import X
from ap_games.gameboard.gameboard import SquareGameboard
from ap_games.log import log
from ap_games.player.ai_player import AIPlayer
from ap_games.player.human_player import HumanPlayer
from ap_games.player.player import TEST_MODE

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import DefaultDict
    from typing import Deque
    from typing import Dict
    from typing import Iterator
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import Label
    from ap_games.ap_types import SupportedPlayers
    from ap_games.player.player import Player

__ALL__ = ["GameBase"]


class GameBase:
    """Base class which are used to specify the various categories of
    games.

    Then concrete classes providing the standard game implementations.

    Note::

      The base class also provide default implementations of some
      methods in order to help implementation of concrete game class.

    :param surface: String contains symbols from set
     :attr:`.GameBase.labels` and symbols "_" or " " mean an empty
     cell.
    :param player_types: A tuple of strings with two elements from
     :attr:`.GameBase.supported_players.keys` which determine the types
     of players.

    :ivar status: This is current status of the game.  ``False`` if game
     can't be continued.
    :ivar gameboard: The gameboard as instance of
     :class:`.SquareGameboard`.
    :ivar players: The queue with players.  Player is an instance of
     :class:`.Player`.  Player with index ``0`` is a current player.


    """

    labels: ClassVar[Tuple[Label, ...]] = (X, O)

    default_surface: ClassVar[str] = EMPTY * 9
    axis: ClassVar[bool] = True
    gap: ClassVar[str] = " "

    supported_players: ClassVar[SupportedPlayers] = {
        "user": HumanPlayer,
        "easy": AIPlayer,
        "medium": AIPlayer,
        "hard": AIPlayer,
        "nightmare": AIPlayer,
    }

    rules: str = ""

    def __init__(
        self,
        *,
        surface: str = '',
        player_types: Tuple[str, ...] = ("user", "user"),
    ):
        if not surface:
            surface = self.default_surface

        if len(player_types) != 2:
            raise ValueError("The number of players should be 2!")

        self.players: Deque[Player] = deque()
        for num, player_type in enumerate(player_types):
            label: Label = self.labels[num]
            self.players.append(
                self.supported_players[player_type](
                    player_type, game=self, label=label
                )
            )

        surface_without_underscore = surface.replace("_", EMPTY)
        if not frozenset(surface_without_underscore).issubset(
            {*self.labels, EMPTY}
        ):
            raise ValueError(
                "Gameboard must contain only ' ', '_' and symbols "
                f"from {self.labels}."
            )

        self.status: GameStatus = GameStatus(
            active=True, message="", must_skip=False
        )
        self.gameboard: SquareGameboard = SquareGameboard(
            surface=surface_without_underscore, gap=self.gap, axis=self.axis
        )
        # move the player with the least number of "label" to the front
        # of the queue
        while self.gameboard.count(
            self.players[0].label
        ) > self.gameboard.count(self.players[1].label):
            self.players.rotate(1)

        self._available_steps_cache: DefaultDict[
            int, Dict[Tuple[str, Label], Tuple[Coordinate, ...]]
        ] = defaultdict(dict)
        self.available_steps_cache_size: int = 7  # depth

    @staticmethod
    def _get_adversary_label(player_label: Label) -> Label:
        return X if player_label == O else O

    def _clean_cache(self) -> None:
        outdated: int = self.gameboard.surface.count(EMPTY) + 1
        while outdated in self._available_steps_cache:
            del self._available_steps_cache[outdated]
            outdated += 1

    def _winners(self, *, gameboard: SquareGameboard) -> Tuple[Player, ...]:
        """Must be overridden by subclasses and must return
        a set of instance(s) ot the :class:`.Player` defined as
        winner(s).

        """
        return tuple()

    def get_next_player(self, current_player: Player) -> Player:
        players_cycle: Iterator[Player] = cycle(self.players)
        while next(players_cycle) != current_player:
            pass
        return next(players_cycle)

    def get_score(self, *, gameboard: SquareGameboard, player: Player,) -> int:
        winners: Tuple[Player, ...] = self._winners(gameboard=gameboard)
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
         :attr:`.GameBase.gameboard`.
        :param player: Optional.  If undefined, user current user
         :attr:`.GameBase.players[0]`.

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

        if self.available_steps(
            gameboard=gameboard, player_label=player.label
        ):
            return GameStatus(active=True, message="", must_skip=False)
        return GameStatus(active=False, message="", must_skip=False)

    def available_steps(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player_label: Optional[Label] = None,
    ) -> Tuple[Coordinate, ...]:
        """Return a tuple of coordinates of all available cells on the
        :param:`gameboard` for the :param:`player`.

        This method should be overridden by subclasses if there is a
        more complex rule for determining which cell is available.

        :param gameboard: Optional.  If undefined, use
         :attr:`.GameBase.gameboard`.
        :param player_label: Optional.  If undefined, user label of
         current user :attr:`.GameBase.players[0].label`.

        """
        if gameboard is None:
            gameboard = self.gameboard
        return gameboard.available_steps

    def step(
        self,
        coordinate: Coordinate,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player_label: Optional[Label] = None,
    ) -> int:
        """Change the label of the cell with ``coordinate`` on the
        gameboard.

        :param coordinate: coordinate of cell which player label.
        :param gameboard: Optional.  If undefined, use
         :attr:`.GameBase.gameboard`.
        :param player_label: Optional.  If undefined, user label of
         current user :attr:`.GameBase.players[0].label`.

        This method should be overridden by subclasses if there is a
        more complex rule for labeling cell(s) in ``gameboard``.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_label is None:
            player_label = self.players[0].label

        if coordinate not in self.available_steps(gameboard=gameboard):
            print("You cannot go here!")
            return 0
        return gameboard.label(coordinate, player_label)

    def play(self) -> None:
        """The main public interface that run the game."""
        self.gameboard.print()
        self.status = self.get_status()
        while self.status.active:
            coordinate: Coordinate = self.players[0].go()
            if (
                coordinate != self.gameboard.undefined_coordinate
                and self.step(coordinate=coordinate)
            ):
                if logging.INFO >= log.level:
                    log.info(str(self.gameboard))
                self.gameboard.print()
                self.players.rotate(1)
                self.status = self.get_status()
                if self.status.message:
                    print(self.status.message)
                if self.status.must_skip:
                    self.players.rotate(1)
                    self.status = self.status._replace(active=True)

    @classmethod
    def cli(cls, user_1_type: str = "", user_2_type: str = "") -> None:
        if not (user_1_type and user_2_type):
            if TEST_MODE:
                command: str = "start medium hard"
            else:
                print(
                    "Type 'start user_1_type user_2_type' "
                    "to run the selected game, where user_X_type "
                    "is one of the supported values: "
                    "user, easy, hard and nightmare; "
                    "Type 'rules' to get game rules or "
                    "type 'exit' to return to the main menu."
                )
                command = input("\nInput command: ").strip()
        else:
            command = f"start {user_1_type} {user_2_type}"
        while command != "exit":
            parameters = command.split()
            if (
                len(parameters) == 3
                and parameters[0] == "start"
                and parameters[1] in cls.supported_players
                and parameters[2] in cls.supported_players
            ):
                game = cls(player_types=(parameters[1], parameters[2]))
                game.play()
            elif command == "rules":
                print(cls.rules)
            else:
                print("Bad parameters!")
            if TEST_MODE:
                command = "exit"
            else:
                command = input("\nInput command: ").strip()
