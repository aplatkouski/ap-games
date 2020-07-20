from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.game.game_base import GameBase
from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.ap_types import GameStatus

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import List
    from typing import Optional
    from typing import Tuple
    from ap_games.ap_types import Labels
    from ap_games.gameboard.gameboard import SquareGameboard
    from ap_games.player.player import Player

__ALL__ = ['Reversi']


class Reversi(GameBase):
    """Reversi game supports human user and three types of AI (easy,
    medium, hard).

    For details see :class:`.GameBase`.

    """

    axis: ClassVar[bool] = True

    default_surface: ClassVar[str] = (
        (EMPTY * 27) + "XO" + (EMPTY * 6) + "OX" + (EMPTY * 27)
    )

    def _winners(self, *, gameboard: SquareGameboard) -> Tuple[Player, ...]:
        """Define and return the set of all players who have the maximum
        count of player labels on the gameboard.

        """
        player_scores: List[Tuple[Player, int]] = [
            (player, gameboard.count(player.label)) for player in self.players
        ]
        max_score = max(score for _, score in player_scores)
        return tuple(player for player, score in player_scores if score == max_score)

    def get_score(self, *, gameboard: SquareGameboard, player: Player,) -> int:
        player_score: int = 0
        another_players_score: int = 0
        for p in self.players:
            if p == player:
                player_score += gameboard.count(p.label)
            else:
                another_players_score += gameboard.count(p.label)
        return player_score - another_players_score

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

        game_status = GameStatus(active=True, message="", must_skip=False)

        if not self.available_steps(gameboard=gameboard, player_label=player.label):
            next_player: Player = self.get_next_player(player)
            if not self.available_steps(
                gameboard=gameboard, player_label=next_player.label
            ):
                winners: Tuple[Player, ...] = self._winners(gameboard=gameboard)
                if len(winners) == 1:
                    game_status = GameStatus(
                        False, f"{winners[0].label} wins\n", must_skip=False
                    )
                elif len(winners) > 1:
                    game_status = GameStatus(False, "Draw\n", must_skip=False)
                else:  # len(winners) == 0
                    game_status = GameStatus(False, "Impossible\n", must_skip=False)
            else:
                game_status = GameStatus(
                    active=False,
                    message=f"The player [{player.label}] has no steps available!\n",
                    must_skip=True,
                )
        return game_status

    def available_steps(
        self,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player_label: Optional[Labels] = None,
    ) -> Tuple[Coordinate, ...]:
        """Return coordinates of only that cells where ``player`` can
        flip at least one another player label using Reversi game's
        rule.

        TODO: add max priority to corner cells.

        """
        if gameboard is None:
            gameboard = self.gameboard
        if player_label is None:
            player_label = self.players[0].label

        surface: str = gameboard.surface
        count_empty_cell: int = surface.count(EMPTY)

        if (surface, player_label) not in self._available_steps_cache[count_empty_cell]:
            actual_available_steps: List[Coordinate] = list()
            adversary_label = self._get_adversary_label(player_label)
            counter = gameboard.counter
            if counter[EMPTY] <= counter[player_label]:
                reverse: bool = False
                start_label: str = EMPTY
                end_label: str = player_label
            else:
                reverse = True
                start_label = player_label
                end_label = EMPTY
            for coordinate in gameboard.coordinates_with_label(start_label):
                result = self._check_directions(
                    gameboard,
                    start_coordinate=coordinate,
                    mid_label=adversary_label,
                    end_label=end_label,
                    reverse=reverse,
                )
                if result:
                    actual_available_steps.extend(result)
            # use ``set`` to remove possible duplicates
            self._available_steps_cache[count_empty_cell][
                surface, player_label
            ] = tuple(set(actual_available_steps))
        return self._available_steps_cache[count_empty_cell][surface, player_label]

    @staticmethod
    def _check_directions(
        gameboard: SquareGameboard,
        *,
        start_coordinate: Coordinate,
        mid_label: str,
        end_label: str,
        reverse: bool = False,
    ) -> Tuple[Coordinate, ...]:
        available_steps: List[Coordinate] = list()
        # Iterate over all directions where the cell occupied by
        # the ``mid_label``
        for direction in gameboard.offset_directions(
            coordinate=start_coordinate, label=mid_label
        ):
            next_coordinate, label = gameboard.get_offset_cell(
                start_coordinate, direction
            )
            # Iterate over all cells in this direction
            while label == mid_label:
                next_coordinate, label = gameboard.get_offset_cell(
                    next_coordinate, direction
                )
            else:
                # Check there is the cell occupied by the ``end_label``
                # behind the cells with ``mid_label``
                if label == end_label:
                    if reverse:
                        available_steps.append(next_coordinate)
                    else:
                        # if successful, other directions can be not
                        # checked
                        return (start_coordinate,)
        return tuple(available_steps)

    def step(
        self,
        coordinate: Coordinate,
        *,
        gameboard: Optional[SquareGameboard] = None,
        player_label: Optional[str] = None,
    ) -> int:
        if gameboard is None:
            gameboard = self.gameboard
        if player_label is None:
            player_label = self.players[0].label

        score: int = 0

        if coordinate not in self.available_steps(gameboard=gameboard, player_label=player_label):
            print("You cannot go here!")
            return score

        score += gameboard.label(coordinate=coordinate, label=player_label)
        if score:
            for shift in gameboard.offset_directions(
                coordinate=coordinate, label=self._get_adversary_label(player_label)
            ):
                adversary_occupied_cells: List[Coordinate] = list()
                analyzed_coordinate, label = gameboard.get_offset_cell(
                    coordinate, shift
                )
                # Iterate over all cells in this direction while label is
                # occupied adversary
                while label and label not in (EMPTY, player_label):
                    # Save the coordinate of the current occupied cell
                    adversary_occupied_cells.append(analyzed_coordinate)
                    analyzed_coordinate, label = gameboard.get_offset_cell(
                        analyzed_coordinate, shift
                    )
                else:
                    # Label all adversary cells if there is a cell behind
                    # them occupied by the current player
                    if label == player_label:
                        while adversary_occupied_cells:
                            score += gameboard.label(
                                coordinate=adversary_occupied_cells.pop(),
                                label=player_label,
                                force=True,
                            )
            if len(self._available_steps_cache) > self.available_steps_cache_size:
                self._clean_cache()
        return score
