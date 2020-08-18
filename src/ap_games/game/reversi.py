from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.ap_types import GameStatus
from ap_games.game.game_base import TwoPlayerBoardGame
from ap_games.log import logger

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Coordinates
    from ap_games.ap_types import Directions
    from ap_games.ap_types import PlayerMark
    from ap_games.gameboard.gameboard import SquareGameboard

__all__ = ('Reversi',)


class Reversi(TwoPlayerBoardGame):
    """Reversi game supports human user and some types of AI.

    For details see :class:`TwoPlayerBoardGame`.

    """

    default_grid: ClassVar[str] = f'{EMPTY * 27}XO{EMPTY * 6}OX{EMPTY * 27}'
    # coordinates with additional score
    priority_coordinates: ClassVar[Dict[Coordinate, int]] = {
        Coordinate(1, 1): 10,
        Coordinate(1, 8): 10,
        Coordinate(8, 8): 10,
        Coordinate(8, 1): 10,
    }

    rules: ClassVar[str] = ''.join(
        (
            "You must place the piece so that an opponent's piece, or a ",
            "row of opponent's pieces, is flanked by your pieces.\nAll of ",
            "the opponent's pieces between your pieces are then turned ",
            'over to become your color. The object of the game is to own ',
            'more pieces than your opponent when the game is over.',
        )
    )

    def get_status(
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
    ) -> GameStatus:
        """Return game status calculated in accordance with game rules.

        .. seealso::

            :meth:`.TwoPlayerBoardGame.get_status`

        :param gameboard: Optional.  If undefined, use
            :attr:`.gameboard`.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).

        :returns: Game status as the instance of namedtuple
            :class:`GameStatus`.
            ``GameStatus.active == False`` if game cannot be continued.
            ``GameStatus.must_skip == True`` means that the game can
            only be continued after the rotation of the players.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_mark is None:
            player_mark = self.players[0].mark

        if self.get_available_moves(gameboard, player_mark):
            return GameStatus(active=True, message='', must_skip=False)

        enemy_mark: PlayerMark = self.get_enemy_mark(player_mark)
        if self.get_available_moves(gameboard, enemy_mark):
            game_status = GameStatus(
                active=False,
                message=(
                    f'\nThe player [{player_mark}] has no moves available!\n'
                ),
                must_skip=True,
            )
        else:
            winners: Tuple[PlayerMark, ...] = self._get_winners(
                gameboard=gameboard
            )
            if len(winners) == 1:
                game_status = GameStatus(
                    active=False,
                    message=f'{winners[0]} wins\n',
                    must_skip=False,
                )
            else:  # len(winners) > 1:
                game_status = GameStatus(
                    active=False, message='Draw\n', must_skip=False
                )
        return game_status

    def place_mark(
        self,
        coordinate: Coordinate,
        player_mark: Optional[PlayerMark] = None,
        gameboard: Optional[SquareGameboard] = None,
    ) -> int:
        """Player's move at given coordinate on the gameboard.

        :param coordinate: The coordinate of cell where player want to
            move.
        :param player_mark: Optional.  If undefined, use mark of current
            player (mark of the player with index ``0`` in
            :attr:`.players`).
        :param gameboard: Optional.  If undefined, use
            :attr:`.gameboard`.

        :returns: Score as count of marked cells.  Return ``0`` if no
            cells were marked.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_mark is None:
            player_mark = self.players[0].mark

        if coordinate not in self.get_available_moves(gameboard, player_mark):
            logger.warning('You cannot go here!')
            return 0

        grid: str = gameboard.grid_as_string
        # the cache was filled in :meth:`.get_available_moves` method.
        enemy_coordinates: Directions = tuple(
            self._available_moves_cache[grid, player_mark][coordinate]
        )
        score: int = gameboard.place_mark(coordinate, player_mark)

        for enemy_coordinate in enemy_coordinates:
            score += gameboard.place_mark(
                coordinate=enemy_coordinate, mark=player_mark, force=True,
            )
        if gameboard is self.gameboard:
            # if gameboard is not fake
            del self._available_moves_cache[grid, player_mark]
        return score

    def get_available_moves(
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
    ) -> Coordinates:
        """Determine available cells, save their coordinates to cache.

        :param gameboard: Optional.  If undefined, use
            :attr:`.gameboard`.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).

        :returns: All coordinates of the given ``gameboard`` where
            player with the ``player_mark`` can move.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_mark is None:
            player_mark = self.players[0].mark

        grid: str = gameboard.grid_as_string

        if (grid, player_mark) not in self._available_moves_cache:
            self._available_moves_cache[grid, player_mark] = defaultdict(list)
            enemy_mark: PlayerMark = self.get_enemy_mark(player_mark)
            for cell in filter(
                lambda x: x.mark != enemy_mark, gameboard.cells
            ):
                self._fill_available_moves_cache(
                    gameboard=gameboard,
                    start_coordinate=cell.coordinate,
                    cache_key=(grid, player_mark),
                    player_mark=player_mark,
                    enemy_mark=enemy_mark,
                    reverse=False if cell.mark == EMPTY else True,
                )
        return tuple(self._available_moves_cache[grid, player_mark])

    def get_score(
        self, gameboard: SquareGameboard, player_mark: PlayerMark
    ) -> int:
        """Return difference in number of marks between players.

        :param gameboard: The gameboard relative to which the score of
            the game will be calculated.
        :param player_mark: The player mark relative to whom the score
            of the game will be calculated.

        :returns: Score of the game as the difference in the scoring of
            ``player`` marks and mark of the another player.

        """
        return gameboard.count(player_mark) - gameboard.count(
            self.get_enemy_mark(player_mark)
        )

    def _get_winners(
        self, *, gameboard: SquareGameboard
    ) -> Tuple[PlayerMark, ...]:
        """Return players who have the maximum count of marks.

        :param gameboard: The gameboard relative to which the winner(s)
            will be determined.

        :returns: Tuple with player marks who were determined as
            winners.

        """
        first_player_score: int = gameboard.count(self.players[0].mark)
        second_player_score: int = gameboard.count(self.players[1].mark)
        if first_player_score > second_player_score:
            return (self.players[0].mark,)
        elif first_player_score < second_player_score:
            return (self.players[1].mark,)
        return (self.players[0].mark, self.players[1].mark)

    def _fill_available_moves_cache(
        self,
        gameboard: SquareGameboard,
        start_coordinate: Coordinate,
        cache_key: Tuple[str, PlayerMark],
        player_mark: PlayerMark,
        enemy_mark: PlayerMark,
        reverse: bool = False,
    ) -> None:
        """Fill cache with available moves.

        :param gameboard:  The gameboard that will be checked.
        :param start_coordinate:  The coordinate relative to which the
            directions will be checked.
        :param cache_key:  The key of cache.
        :param player_mark:  The current player mark.
        :param enemy_mark:  The mark to which all cells should have in
            checked directions between ``start_coordinate`` and cell
            with ``player_mark`` (when ``reverse=False``) or ``EMPTY``
            (when ``reverse=True``).
        :param reverse: Optional.  ``False`` by default. If ``False``,
            ``start_coordinate`` will be saved as an available move,
            otherwise an empty cell in each direction where the rules of
            the Reversi game are executed will be saved as an available
            move.

        """
        for offset in gameboard.get_offsets(start_coordinate):
            if gameboard[offset.coordinate].mark == enemy_mark:
                enemy_coordinates: List[Coordinate] = [offset.coordinate]
                next_coordinate, next_mark = gameboard.get_offset_cell(
                    coordinate=offset.coordinate, direction=offset.direction,
                )
                while next_mark == enemy_mark:
                    enemy_coordinates.append(next_coordinate)
                    next_coordinate, next_mark = gameboard.get_offset_cell(
                        coordinate=next_coordinate, direction=offset.direction,
                    )
                if reverse and next_mark == EMPTY:
                    self._available_moves_cache[cache_key][
                        next_coordinate
                    ].extend(enemy_coordinates)
                elif not reverse and next_mark == player_mark:
                    self._available_moves_cache[cache_key][
                        start_coordinate
                    ].extend(enemy_coordinates)
