from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.game.game_base import GameBase
from ap_games.ap_types import GameStatus

if TYPE_CHECKING:
    from typing import Optional
    from typing import Set
    from ap_games.gameboard.gameboard import SquareGameboard
    from ap_games.player.player import Player

__ALL__ = ['TicTacToe']


class TicTacToe(GameBase):
    """TicTacToe class introduces Tic-Tac-Toe game.

    For details see :class:`.GameBase`.

    """

    def winners(self, *, gameboard: Optional[SquareGameboard] = None) -> Set[Player]:
        """Define and return the set of all players who draw solid line.

        If all characters on a "side" are the same and equal to the
        label of player from :attr:`.players`, this player is added to
        the set of winners.

        :param gameboard: Optional.  If undefined, use
         :attr:`.GameBase.gameboard`.

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
