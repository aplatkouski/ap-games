from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.ap_types import GameStatus
from ap_games.game.game_base import TwoPlayerBoardGame

if TYPE_CHECKING:
    from typing import Any
    from typing import ClassVar
    from typing import List
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import PlayerMark
    from ap_games.gameboard.gameboard import SquareGameboard

__all__ = ('TicTacToe',)


class TicTacToe(TwoPlayerBoardGame):
    """Tic-Tac-Toe game supports human user and some types of AI.

    .. seealso::

        :class:`TwoPlayerBoardGame`

    """

    rules: ClassVar[str] = ''.join(
        (
            'Tic-tac-toe, is a paper-and-pencil game for two players, ',
            'X and O, who take turns marking the spaces in a 3×3 grid.\n',
            'The player who succeeds in placing three of their marks in ',
            'a horizontal, vertical, or diagonal row is the winner.',
        )
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._rotate_players()

    def get_status(
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
    ) -> GameStatus:
        """Return difference in number of marks between players.

        :param gameboard: Optional.  If undefined, use
            :attr:`.TwoPlayerBoardGame.gameboard`.
        :param player_mark: This parameter is not used in this
            implementation.

        :returns: Game status as the instance of namedtuple
            ``GameStatus`` with two fields: ``active`` and ``message``.
            ``GameStatus.active == False`` if game cannot be continued.

        """
        if gameboard is None:
            gameboard = self.gameboard

        game_status: GameStatus = GameStatus(
            active=True, message='', must_skip=False
        )
        if (
            abs(
                gameboard.count(self.players[0].mark)
                - gameboard.count(self.players[1].mark)
            )
            > 1
        ):
            game_status = GameStatus(
                active=False, message='Impossible\n', must_skip=False
            )
        else:
            winners: Tuple[PlayerMark, ...] = self._get_winners(
                gameboard=gameboard
            )
            if (not winners) and not self.get_available_moves(gameboard):
                game_status = GameStatus(
                    active=False, message='Draw\n', must_skip=False
                )
            elif len(winners) == 1:
                game_status = GameStatus(
                    active=False,
                    message=f'{winners[0]} wins\n',
                    must_skip=False,
                )
            elif len(winners) > 1:
                game_status = GameStatus(
                    active=False, message='Impossible\n', must_skip=False
                )
        return game_status

    def _get_winners(
        self, *, gameboard: SquareGameboard
    ) -> Tuple[PlayerMark, ...]:
        """Return players who draw solid line.

        If all characters on a 'side' are the same and equal to the
        mark of player from :attr:`.players`, this player is added to
        the set of winners.

        :param gameboard: The gameboard relative to which the winner(s)
            will be determined.

        :returns: Tuple with player marks who were determined as
            winners.

        """
        if gameboard is None:
            gameboard = self.gameboard

        winners: List[PlayerMark] = []
        all_sides_as_strings: List[str] = [
            ''.join(cell.mark for cell in side) for side in gameboard.all_sides
        ]
        first_player_side: str = self.players[0].mark * gameboard.size
        second_player_side: str = self.players[1].mark * gameboard.size
        if first_player_side in all_sides_as_strings:
            winners.append(self.players[0].mark)
        if second_player_side in all_sides_as_strings:
            winners.append(self.players[1].mark)
        return tuple(winners)
