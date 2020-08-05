from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.ap_types import GameStatus
from ap_games.game.game_base import TwoPlayerBoardGame
from ap_games.log import logger

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Counter as TypingCounter
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Coordinates
    from ap_games.ap_types import Mark
    from ap_games.ap_types import PlayerMark
    from ap_games.gameboard.gameboard import SquareGameboard

__ALL__ = ('Reversi',)


class Reversi(TwoPlayerBoardGame):
    """Reversi game supports human user and some types of AI.

    For details see :class:`.TwoPlayerBoardGame`.

    """

    axis: ClassVar[bool] = True
    default_grid: ClassVar[str] = f'{EMPTY * 27}XO{EMPTY * 6}OX{EMPTY * 27}'
    # coordinate with additional score
    high_priority_coordinates: ClassVar[Dict[Coordinate, int]] = {
        Coordinate(1, 1): 5,
        Coordinate(1, 8): 5,
        Coordinate(8, 8): 5,
        Coordinate(8, 1): 5,
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
            :class:`GameStatus`.  ``GameStatus.active == False`` if game
            cannot be continued.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_mark is None:
            player_mark = self.players[0].mark

        if self.get_available_moves(gameboard, player_mark):
            return GameStatus(active=True, message='', must_skip=False)

        adversary_mark: PlayerMark = self._get_adversary_mark(player_mark)
        if self.get_available_moves(gameboard, adversary_mark):
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

    def place_mark(  # noqa: C901
        self,
        coordinate: Coordinate,
        player_mark: Optional[PlayerMark] = None,
        gameboard: Optional[SquareGameboard] = None,
    ) -> int:
        """Player's move at given coordinate on the gameboard.

        TODO: Fix C901

        Algorithm::

            1. Iterate over all directions where the cell occupied by
               the "adversary mark";
            2. Iterate over the cells in selected direction;
            3. Save the coordinates of all cells with "adversary mark";
            4. Mark all adversary cells if there is a cell behind them
               occupied by the current player.

        :param coordinate: The coordinate of cell where player want to
            go.
        :param player_mark: Optional.  If undefined, use mark of player
            with index ``0`` in :attr:`.players` (current player mark).
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

        score: int = gameboard.place_mark(coordinate, player_mark)
        adversary_mark: PlayerMark = self._get_adversary_mark(player_mark)

        for direction in gameboard.get_directions(
            start_coordinate=coordinate, offset_cell_mark=adversary_mark
        ):
            adversary_occupied_cells: List[Coordinate] = []
            next_coordinate, mark = gameboard.get_offset_cell(
                coordinate, direction
            )
            while mark == adversary_mark:
                adversary_occupied_cells.append(next_coordinate)
                next_coordinate, mark = gameboard.get_offset_cell(
                    next_coordinate, direction
                )
            if mark == player_mark:
                while adversary_occupied_cells:
                    score += gameboard.place_mark(
                        coordinate=adversary_occupied_cells.pop(),
                        mark=player_mark,
                        force=True,
                    )
        if len(self._available_moves_cache) > self.available_moves_cache_size:
            self._clean_cache()
        return score

    def get_available_moves(  # noqa: C901
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
    ) -> Coordinates:
        """Return coordinates of available cells using Reversi game's rule.

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

        grid: str = gameboard.grid
        count_empty_cell: int = grid.count(EMPTY)

        if (grid, player_mark) not in self._available_moves_cache[
            count_empty_cell
        ]:
            actual_available_moves: List[Coordinate] = []
            adversary_mark: PlayerMark = self._get_adversary_mark(player_mark)

            mark_counter: TypingCounter[str] = gameboard.counter
            if mark_counter[EMPTY] <= mark_counter[player_mark]:
                start_mark: Mark = EMPTY
                end_mark: Mark = player_mark
                reverse: bool = False
            else:
                start_mark = player_mark
                end_mark = EMPTY
                reverse = True

            for coordinate in gameboard.get_marked_coordinates(
                mark=start_mark
            ):
                available_coordinates: Tuple[
                    Coordinate, ...
                ] = self._check_directions(
                    gameboard,
                    start_coordinate=coordinate,
                    mid_mark=adversary_mark,
                    end_mark=end_mark,
                    reverse=reverse,
                )
                if available_coordinates:
                    actual_available_moves.extend(available_coordinates)
            # use ``set`` to remove possible duplicates
            self._available_moves_cache[count_empty_cell][
                grid, player_mark
            ] = tuple(set(actual_available_moves))
        return self._available_moves_cache[count_empty_cell][grid, player_mark]

    def get_score(
        self, *, gameboard: SquareGameboard, player_mark: PlayerMark
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
            self._get_adversary_mark(player_mark)
        )

    def _get_winners(
        self, *, gameboard: SquareGameboard
    ) -> Tuple[PlayerMark, ...]:
        """Return players who have the maximum count of marks.

        TODO: Use ``gameboard.counter`` except ``gameboard.count``,
            this method should return player_mark, not Player.

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

    @staticmethod
    def _check_directions(
        gameboard: SquareGameboard,
        *,
        start_coordinate: Coordinate,
        mid_mark: Mark,
        end_mark: Mark,
        reverse: bool = False,
    ) -> Coordinates:
        """Determine and return coordinates of available moves.

        Algorithm::

            1. Iterate over all directions where the cell occupied by
               the ``mid_mark``;
            2. Iterate over the cells in selected direction;
            3. Check there is the cell occupied by the ``end_mark``
               behind the cells with ``mid_mark``;
            4. if successful, return ``start_coordinate``. Other
               directions can be not checked.

        :param gameboard:  The gameboard that will be checked.
        :param start_coordinate:  The coordinate relative to which the
            directions will be checked.
        :param mid_mark:  The mark to which all cells should have in
            checked directions between ``start_coordinate`` and cell
            with ``end_mark``.
        :param end_mark:  The mark of cell that should be behind cells
            with ``mid_mark`` in parsed direction.
        :param reverse:  The default is ``False``.  If ``True``,
            the coordinate of the cell with ``end_mark`` in the parsed
            direction is added to return tuple, otherwise
            ``start_coordinate`` will be returned.

        :returns: A tuple of coordinates of available steps.

        """
        available_moves: List[Coordinate] = []
        for direction in gameboard.get_directions(
            start_coordinate=start_coordinate, offset_cell_mark=mid_mark
        ):
            next_coordinate, mark = gameboard.get_offset_cell(
                start_coordinate, direction
            )
            while mark == mid_mark:
                next_coordinate, mark = gameboard.get_offset_cell(
                    next_coordinate, direction
                )
            if mark == end_mark:
                if reverse:
                    available_moves.append(next_coordinate)
                else:
                    return (start_coordinate,)
        return tuple(available_moves)
