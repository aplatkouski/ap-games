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
    from ap_games.gameboard.gameboard import SquareGameboard
    from ap_games.player.player import Player
    from ap_games.ap_types import Label

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

    @classmethod
    def _adversary_occupied_directions(
        cls, coordinate: Coordinate, gameboard: SquareGameboard, player_label: str,
    ) -> Tuple[Coordinate, ...]:
        """Determine the ``directions`` where adjacent cells are
        occupied by the adversary.

        :param coordinate: The coordinate against which adjacent
         cells will be checked.
        :param gameboard: Optional.  If undefined, use
         :attr:`.GameBase.gameboard`.
        :param player_label: Cells with this "friendly" label will
         not be considered an adversary.

        :return: Tuple of offsets relative to the :param:`coordinate`.

        """
        return gameboard.offset_directions(
            coordinate=coordinate, exclude_labels=(EMPTY, player_label)
        )

    def _winners(self, *, gameboard: SquareGameboard) -> Tuple[Player, ...]:
        """Define and return the set of all players who have the maximum
        count of player labels on the gameboard.

        """
        # TODO: give a turn to another player if the current player
        #   cannot go
        # if any(self.available_steps(gameboard=gameboard, player=player) for player in self.players):
        #     # winner undefined if there's at least one player who can go
        #     return set()
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

        game_status = GameStatus(active=True, message="")

        if not self.available_steps(gameboard=gameboard, player=player):
            winners: Tuple[Player, ...] = self._winners(gameboard=gameboard)
            if len(winners) == 1:
                game_status = GameStatus(False, f"{winners[0].label} wins\n")
            elif len(winners) > 1:
                game_status = GameStatus(False, "Draw\n")
            else:  # len(winners) == 0
                game_status = GameStatus(False, "Impossible\n")
        return game_status

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

        surface: str = gameboard.surface
        count_empty_cell: int = surface.count(EMPTY)
        if (surface, current_player_label) in self._available_steps_cache[
            count_empty_cell
        ]:
            return self._available_steps_cache[count_empty_cell][
                surface, current_player_label
            ]

        actual_available_steps: List[Coordinate] = list()
        for coordinate in gameboard.available_steps:
            # Iterate over all directions where the cell occupied by
            # the adversary
            for shift in self._adversary_occupied_directions(
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
        self._available_steps_cache[count_empty_cell][
            surface, current_player_label
        ] = tuple(actual_available_steps)
        return self._available_steps_cache[count_empty_cell][
            surface, current_player_label
        ]

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
            for shift in self._adversary_occupied_directions(
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
            if len(self._available_steps_cache) > self.available_steps_cache_size:
                self._clean_cache()
        return score
