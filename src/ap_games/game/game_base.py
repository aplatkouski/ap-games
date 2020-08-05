from __future__ import annotations

from collections import defaultdict
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
from ap_games.player.player import TEST_MODE

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import DefaultDict
    from typing import Deque
    from typing import Dict
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import Coordinates
    from ap_games.ap_types import PlayerMark
    from ap_games.ap_types import SupportedPlayers
    from ap_games.player.player import Player

__ALL__ = ('TwoPlayerBoardGame', 'TwoPlayerBoardGame')


class TwoPlayerBoardGame:
    """TwoPlayerBoardGame class specifies the public methods of game.

    TODO: Separate business logic from develop features. Implement cache
      as decorator of methods.

    TODO: move ``_available_moves_cache`` to :class:`.player.AIPlayer`

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
        :class:`.SquareGameboard`.
    :ivar players: The queue with players.  Player is an instance of
        :class:`.Player`.  Player with index ``0`` is a current player.
    :ivar _available_moves_cache: Cache with available moves as dict.
        Where key of dict is integer corresponding to the number of
        empty cell, and value is a dict where key is tuple with two
        field:

        * ``grid`` of the gameboard in considered move;
        * ``mark`` of player, who should make move on this turn.

        Value of sub-dict is tuple with coordinates of all available moves.

    :ivar available_moves_cache_size: Limit len of
        ``_available_moves_cache`` dict.

    """

    marks: ClassVar[Tuple[PlayerMark, PlayerMark]] = (X_MARK, O_MARK)

    default_grid: ClassVar[str] = ' OXXXO XO'  # EMPTY * 9
    axis: ClassVar[bool] = True
    gap: ClassVar[str] = ' '

    supported_players: ClassVar[SupportedPlayers] = {
        'user': HumanPlayer,
        'easy': AIPlayer,
        'medium': AIPlayer,
        'hard': AIPlayer,
        'nightmare': AIPlayer,
    }

    rules: ClassVar[str] = ''
    high_priority_coordinates: ClassVar[Dict[Coordinate, int]] = {}

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
        for num, player_type in enumerate(player_types):
            self.players.append(
                self.supported_players[player_type](
                    player_type, mark=self.marks[num], game=self  # noqa: T484
                )
            )

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
            grid=grid_without_underscore, gap=self.gap, axis=self.axis
        )

        self._available_moves_cache: DefaultDict[
            int, Dict[Tuple[str, PlayerMark], Coordinates]
        ] = defaultdict(dict)
        self.available_moves_cache_size: int = 7  # depth
        self._rotate_players()

    def play(self) -> None:
        """Start new game.

        TODO: add clean cache after success ``place_mark``.

        """
        self.gameboard.print_grid()
        self.status = self.get_status()
        while self.status.active:
            coordinate: Coordinate = self.players[0].move()
            if (
                coordinate != self.gameboard.undefined_coordinate
                and self.place_mark(coordinate)
            ):
                self.gameboard.print_grid()
                self.players.rotate(1)
                self.status = self.get_status()
                if self.status.message:
                    logger.info(self.status.message)
                if self.status.must_skip:
                    self.players.rotate(1)
                    self.status = self.status._replace(active=True)

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

            If there is no available move for the ``player`` the method
            must return ``GameStatus.active == False`` and
            ``GameStatus.must_skip == True``.

        :param gameboard: Optional.  If undefined, use
            :attr:`.TwoPlayerBoardGame.gameboard`.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).

            .. versionchanged:: 0.0.2  Change argument ``player`` to
                ``player mark``. ``gameboard`` and ``player_mark`` are
                not keyword-only arguments.

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
        self, *, gameboard: SquareGameboard, player_mark: PlayerMark
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

    @classmethod
    def cli(  # noqa: C901
        cls, user1_type: str = '', user2_type: str = ''
    ) -> None:
        """Create an instance of the game with the given parameters.

        TODO: Fix C901

        :param user1_type: Type of first user as string from
            :attr:`.supported_players`.
        :param user2_type: Type of second user.

        """
        if user1_type and user2_type:
            command: str = f'start {user1_type} {user2_type}'
        elif TEST_MODE:
            command = 'start medium hard'
        else:
            logger.info(
                'Type "start user1_type user2_type" to run the selected '
                'game, where "user1_type" and "user2_type" is one of the '
                f'supported values: {", ".join(cls.supported_players)}; '
                'Type "rules" to get game rules or type "exit" to '
                'return to the main menu.\nInput command: '
            )
            command = sys.stdin.readline().strip()
        logger.debug(f'{command=}')
        while command != 'exit':
            parameters = command.split()
            if (
                len(parameters) == 3
                and parameters[0] == 'start'
                and parameters[1] in cls.supported_players
                and parameters[2] in cls.supported_players
            ):
                game = cls(player_types=(parameters[1], parameters[2]))
                game.play()
            elif command == 'rules':
                logger.info(cls.rules)
            else:
                logger.warning('Bad parameters!')
            if TEST_MODE:
                command = 'exit'
            else:
                logger.info('\nInput command: ')
                command = sys.stdin.readline().strip()
            logger.debug(f'{command=}')

    def _get_winners(
        self, *, gameboard: SquareGameboard
    ) -> Tuple[PlayerMark, ...]:
        """Return a tuple of :class:`.Player` instances defined as winner(s).

        .. warning::

            This method must be overridden by subclasses.

        :param gameboard: The gameboard relative to which the winner(s)
            will be determined.

        :returns: Tuple with player marks who were determined as
            winners.

        """
        return ()

    def _clean_cache(self) -> None:
        """Delete outdated items.

        Remove all items from ``_available_moves_cache`` where
        key (count of empty cell) greater than current count of empty
        cell.

        """
        outdated: int = self.gameboard.count(EMPTY) + 1
        while outdated in self._available_moves_cache:
            del self._available_moves_cache[outdated]
            outdated += 1

    def _rotate_players(self) -> None:
        """Move player with the least number of mark to the front of queue."""
        while self.gameboard.count(
            self.players[0].mark
        ) > self.gameboard.count(self.players[1].mark):
            self.players.rotate(1)

    @staticmethod
    def _get_adversary_mark(player_mark: PlayerMark) -> PlayerMark:
        return X_MARK if player_mark == O_MARK else O_MARK
