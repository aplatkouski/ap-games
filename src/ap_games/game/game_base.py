from __future__ import annotations

from collections import deque
import sys
from typing import TYPE_CHECKING

from ap_games.ap_types import EMPTY
from ap_games.ap_types import GameStatus
from ap_games.ap_types import O_MARK
from ap_games.ap_types import X_MARK
from ap_games.gameboard.gameboard import SquareGameboard
from ap_games.log import logger
from ap_games.player.ai_player import AIPlayer
from ap_games.player.human_player import HumanPlayer

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import DefaultDict
    from typing import Deque
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import Coordinates
    from ap_games.ap_types import OptionalPlayerTypes
    from ap_games.ap_types import PlayerMark
    from ap_games.ap_types import SupportedPlayers
    from ap_games.player.player import Player

__all__ = ('TwoPlayerBoardGame',)


class TwoPlayerBoardGame:
    """TwoPlayerBoardGame class specifies the public methods of game.

    Then concrete classes providing the standard game implementations.

    .. note::

        The base class also provide default implementations of some
        methods in order to help implementation of concrete game class.

    :param grid: String contains symbols from set
        :attr:`.TwoPlayerBoardGame.marks` and symbols '_' or ' ' mean an
        empty cell.
    :param player_types: A tuple of strings with two elements from
        :attr:`.TwoPlayerBoardGame.supported_players.keys` which
        determine the types of players.

    :ivar status: This is current status of the game.  ``False`` if game
        can't be continued.
    :ivar gameboard: The gameboard as instance of
        :class:`SquareGameboard`.
    :ivar players: The queue with players.  Player is an instance of
        :class:`Player`.  Player with index ``0`` is a current player.
    :ivar _available_moves_cache: Cache with available moves as dict.
        Where key of dict is a tuple with two fields:

        * ``grid`` of the gameboard before considered move;
        * ``mark`` of player, who makes move on this turn.

        Value of dict is a sub-dict.  Where the keys are the coordinates
            of all available moves, and the sub-dict value are the tuple
            of coordinates of the cells marked by the enemy, which
            should be marked in the considered move.

    """

    marks: ClassVar[Tuple[PlayerMark, PlayerMark]] = (X_MARK, O_MARK)

    default_grid: ClassVar[str] = EMPTY * 9
    grid_axis: ClassVar[bool] = True
    grid_gap: ClassVar[str] = ' '

    supported_players: ClassVar[SupportedPlayers] = {
        'user': HumanPlayer,
        'easy': AIPlayer,
        'medium': AIPlayer,
        'hard': AIPlayer,
        'nightmare': AIPlayer,
    }

    rules: ClassVar[str] = ''
    priority_coordinates: ClassVar[Dict[Coordinate, int]] = {}

    def __init__(
        self,
        *,
        grid: str = '',
        player_types: Tuple[str, str] = ('user', 'user'),
    ):
        if not grid:
            grid = self.default_grid

        if len(player_types) != 2:
            raise ValueError('The number of players should be 2!')

        self.players: Deque[Player] = deque()
        self._add_players(player_types=player_types)

        grid_without_underscore = grid.replace('_', EMPTY)
        if not set(grid_without_underscore).issubset({*self.marks, EMPTY}):
            raise ValueError(
                'Gameboard must contain only " ", "_" and symbols '
                f'from {self.marks}.'
            )

        self.status: GameStatus = GameStatus(
            active=True, message='', must_skip=False
        )
        self.gameboard: SquareGameboard = SquareGameboard(
            grid=grid_without_underscore,
            gap=self.grid_gap,
            axis=self.grid_axis,
        )

        self._available_moves_cache: Dict[
            Tuple[str, PlayerMark], DefaultDict[Coordinate, List[Coordinate]]
        ] = {}

    def play(self) -> None:
        """Start new game."""
        logger.info(self.gameboard)
        self.status = self.get_status()
        while self.status.active:
            coordinate: Coordinate = self.players[0].move()
            if (
                coordinate != self.gameboard.undefined_coordinate
                and self.place_mark(coordinate)
            ):
                logger.info(self.gameboard)
                self.players.rotate(1)
                self.status = self.get_status()
                if self.status.message:
                    logger.info(self.status.message)
                if self.status.must_skip:
                    self.players.rotate(1)
                    self.status = self.status._replace(active=True)
        self._available_moves_cache.clear()

    def get_status(
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
    ) -> GameStatus:
        """Return game status calculated in accordance with game rules.

        .. warning::

            Must be overridden by subclasses if there is a more complex
            rule for calculating game status.

        .. note::

            If there is no available moves for the ``player`` the method
            must return ``GameStatus.active == False`` and
            ``GameStatus.must_skip == True``.

        :param gameboard: Optional.  If undefined, use
            :attr:`.TwoPlayerBoardGame.gameboard`.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).

        :returns: Game status as the instance of namedtuple
            ``GameStatus`` with three fields: ``active``, ``message``
            and ``must_skip``.   ``GameStatus.active == False`` if game
            cannot be continued.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_mark is None:
            player_mark = self.players[0].mark

        if self.get_available_moves(gameboard, player_mark):
            return GameStatus(active=True, message='', must_skip=False)
        return GameStatus(active=False, message='', must_skip=False)

    def place_mark(
        self,
        coordinate: Coordinate,
        player_mark: Optional[PlayerMark] = None,
        gameboard: Optional[SquareGameboard] = None,
    ) -> int:
        """Change the mark of the cell with coordinate on the gameboard.

        :param coordinate: coordinate of cell which player mark.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).
        :param gameboard: Optional.  If undefined, use
            :attr:`.TwoPlayerBoardGame.gameboard`.

        This method should be overridden by subclasses if there is a
        more complex rule for marking cell(s) in ``gameboard``.

        :returns: Score as count of marked cells.  Return ``0`` if no
            cells were marked.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_mark is None:
            player_mark = self.players[0].mark

        if coordinate not in self.get_available_moves(gameboard):
            logger.warning('You cannot go here!')
            return 0
        return gameboard.place_mark(coordinate, player_mark)

    def get_available_moves(
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
    ) -> Coordinates:
        """Return coordinates of all ``EMPTY`` cells on the gameboard.

        This method should be overridden by subclasses if there is a
        more complex rule for determining which cell is available.

        :param gameboard: Optional.  If undefined, use
            :attr:`.TwoPlayerBoardGame.gameboard`.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).

        :returns: All coordinates of the given ``gameboard`` where
            player with the ``player_mark`` can move.

        """
        if gameboard is None:
            gameboard = self.gameboard
        return gameboard.available_moves

    def get_score(
        self, gameboard: SquareGameboard, player_mark: PlayerMark
    ) -> int:
        """Return the score relative to the given gameboard and player.

        :param gameboard: The gameboard relative to which the score of
            the game will be calculated.
        :param player_mark: The player mark relative to whom the score
            of the game will be calculated.

        :returns: Score of the game from ``-1`` to ``1``, where ``-1``
            corresponds to a loss of ``player``; ``0`` corresponds to
            draw and ``1`` corresponds to win of ``player``.

        """
        winners: Tuple[PlayerMark, ...] = self._get_winners(
            gameboard=gameboard
        )
        if len(winners) == 1:
            if player_mark in winners:
                return 1
            else:
                return -1
        else:  # len(winners) != 1
            return 0

    def get_next_player(self, current_player: Player) -> Player:
        """Return ``player`` who is next to ``current_player``.

        :param current_player: The player relative to whom the another
            player will be calculated.

        :returns: Player who will be move next after ``current_player``.

        """
        return (
            self.players[1]
            if current_player is self.players[0]
            else self.players[0]
        )

    def cli(self, player_types: OptionalPlayerTypes = ()) -> None:
        """Command line interface of the game.

        :param player_types: A tuple of strings with two elements from
            :attr:`.TwoPlayerBoardGame.supported_players.keys` which
            determine the types of players.

        """
        if player_types and len(player_types) == 2:
            command: str = f'start {player_types[0]} {player_types[1]}'
        else:
            logger.info(
                'Type "start user1_type user2_type" to run the game, '
                'where "user1_type" and "user2_type" is one of the '
                f'supported values: {", ".join(self.supported_players)}; '
                'Type "rules" to get game rules or type "exit" to '
                'exit from the game.\nInput command: '
            )
            command = sys.stdin.readline().strip()
        logger.debug(f'{command=}')
        while command != 'exit':
            parameters = command.split()
            if (
                len(parameters) == 3
                and parameters[0] == 'start'
                and parameters[1] in self.supported_players
                and parameters[2] in self.supported_players
            ):
                self._add_players(player_types=(parameters[1], parameters[2]))
                self.gameboard = SquareGameboard(
                    grid=self.default_grid,
                    gap=self.grid_gap,
                    axis=self.grid_axis,
                )
                self.play()
            elif command == 'rules':
                logger.info(self.rules)
            else:
                logger.warning('Bad parameters!')
            logger.info('\nInput command: ')
            command = sys.stdin.readline().strip()
            logger.debug(f'{command=}')

    def _add_players(self, *, player_types: Tuple[str, str]) -> None:
        """Create instances of `Player` and add them to :attr:`.players`.

        :param player_types: A tuple of strings with two elements from
            :attr:`.TwoPlayerBoardGame.supported_players`.keys() which
            determine the types of players.

        """
        self.players.clear()
        for num, player_type in enumerate(player_types):
            self.players.append(
                self.supported_players[player_type](
                    player_type, mark=self.marks[num], game=self  # noqa: T484
                )
            )

    def _get_winners(
        self, *, gameboard: SquareGameboard
    ) -> Tuple[PlayerMark, ...]:
        """Return a tuple of :class:`Player` instances defined as winner(s).

        .. warning::

            This method must be overridden by subclasses.

        :param gameboard: The gameboard relative to which the winner(s)
            will be determined.

        :returns: Tuple with player marks who were determined as
            winners.

        """
        return ()

    def _rotate_players(self) -> None:
        """Move player with the least number of mark to the front of queue."""
        while self.gameboard.count(
            self.players[0].mark
        ) > self.gameboard.count(self.players[1].mark):
            self.players.rotate(1)

    @staticmethod
    def get_enemy_mark(player_mark: PlayerMark) -> PlayerMark:
        """Return enemy mark relatively to ``player_mark``.

        :param player_mark: The player's mark, relative to which the
            enemy player's mark will be determined.

        :returns: The opponent's player's mark.

        """
        return X_MARK if player_mark == O_MARK else O_MARK
