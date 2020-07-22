from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.game.game_base import GameBase
from ap_games.ap_types import GameStatus

if TYPE_CHECKING:
    from typing import Optional
    from typing import List
    from typing import Tuple
    from ap_games.gameboard.gameboard import SquareGameboard
    from ap_games.player.player import Player

__ALL__ = ["TicTacToe"]


class TicTacToe(GameBase):
    """TicTacToe class introduces Tic-Tac-Toe game.

    For details see :class:`.GameBase`.

    """

    rules: str = (
        "Tic-tac-toe, is a paper-and-pencil game for two players, "
        "X and O, who take turns marking the spaces in a 3×3 grid.\n"
        "The player who succeeds in placing three of their marks in "
        "a horizontal, vertical, or diagonal row is the winner."
    )

    def _winners(self, *, gameboard: SquareGameboard) -> Tuple[Player, ...]:
        """Define and return the set of all players who draw solid line.

        If all characters on a "side" are the same and equal to the
        label of player from :attr:`.players`, this player is added to
        the set of winners.

        """
        if gameboard is None:
            gameboard = self.gameboard

        winners: List[Player] = list()
        for player in self.players:
            for side in gameboard.all_sides:
                if all(cell.label == player.label for cell in side):
                    winners.append(player)
                    break
        return tuple(winners)

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

        game_status: GameStatus = GameStatus(
            active=True, message="", must_skip=False
        )
        if (
            abs(
                gameboard.count(self.players[0].label)
                - gameboard.count(self.players[1].label)
            )
            > 1
        ):
            game_status = GameStatus(False, "Impossible\n", must_skip=False)
        else:
            winners: Tuple[Player, ...] = self._winners(gameboard=gameboard)
            if not winners and not self.available_steps(gameboard=gameboard):
                game_status = GameStatus(False, "Draw\n", must_skip=False)
            elif len(winners) == 1:
                game_status = GameStatus(
                    False, f"{winners[0].label} wins\n", must_skip=False
                )
            elif len(winners) > 1:
                game_status = GameStatus(
                    False, "Impossible\n", must_skip=False
                )
        return game_status
