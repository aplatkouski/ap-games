from __future__ import annotations

import logging
from operator import add
from operator import sub
import random
from typing import TYPE_CHECKING

from ap_games.ap_types import Step
from ap_games.gameboard.gameboard import SquareGameboard
from ap_games.log import logger
from ap_games.player.player import Player
from ap_games.player.player import TEST_MODE

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import PlayerMark
    from ap_games.game.game_base import TwoPlayerBoardGame

__ALL__ = ('AIPlayer',)

if TEST_MODE:
    random.seed(42)


class AIPlayer(Player):
    """AIPlayer in the game."""

    _max_depth: ClassVar[Dict[str, int]] = {
        'easy': 0,
        'medium': 2,
        'hard': 4,
        'nightmare': 6,
    }

    def __init__(
        self, type_: str, /, *, mark: PlayerMark, game: TwoPlayerBoardGame
    ) -> None:
        super().__init__(type_, mark=mark, game=game)
        self.max_depth = self._max_depth[type_]

    def move(self) -> Coordinate:
        """Define coordinate of the next move and return it.

        :returns: Coordinate chosen according to the minimax algorithm
            when :attr:`.max_depth` is not equal to 0.

        """
        logger.info(f'Making move level "{self.type_}" [{self.mark}]')

        if self.max_depth:
            return self._minimax(depth=1).coordinate
        return self._random_coordinate()

    def _minimax(
        self,
        *,
        depth: int,
        gameboard: Optional[SquareGameboard] = None,
        player: Optional[Player] = None,
    ) -> Step:
        """Mini-max algorithm.

        TODO: swap the first and second item.
            In the current implementation, there may be an error if
            running the method with the ``gameboard`` without the
            available moves.

        1. Go through available spots on the board;
        2. Return a value (score) if a terminal state is found
           (``_get_terminal_score``);
        3. or call the minimax function on each available spot
           (recursion).
        4. Evaluate returning values from function calls
           (``_fix_high_priority_coordinates_score``,
           ``_extract_desired_moves`` and
           ``_extract_most_likely_moves``);
        5. And return the best value (Step).

        :param depth:  Current depth of tree.
        :param gameboard:  Optional.  If undefined, use
            :attr:`.game.gameboard`.
        :param player:  Optional.  If undefined, use ``self``.

        :returns:  Step chosen according to the minimax algorithm.

        """
        if gameboard is None:
            gameboard = self.game.gameboard
        if player is None:
            player = self

        moves: List[Step] = []
        for coordinate in self.game.get_available_moves(
            gameboard, player.mark
        ):
            fake_gameboard: SquareGameboard = gameboard.copy()
            self.game.place_mark(coordinate, player.mark, fake_gameboard)

            if logger.level == logging.DEBUG:
                indent: str = '\t' * depth
                logger.debug(f'\n{indent}[{player.mark}] {coordinate}')
                logger.debug(
                    '\n'.join(
                        f'{indent}{line}'
                        for line in str(fake_gameboard).split('\n')
                    )
                )

            next_player: Player = self.game.get_next_player(player)

            terminal_score, percentage = self._get_terminal_score(
                depth=depth, gameboard=fake_gameboard, player=next_player
            )
            moves.append(
                Step(
                    coordinate=coordinate,
                    score=terminal_score,
                    percentage=percentage,
                )
            )

        fixed_moves: List[Step] = self._fix_high_priority_coordinates_score(
            depth=depth, moves=moves, player=player
        )

        desired_moves: List[Step] = self._extract_desired_moves(
            depth=depth, moves=fixed_moves, player=player
        )

        most_likely_moves: List[Step] = self._extract_most_likely_moves(
            depth=depth, moves=desired_moves, player=player
        )

        move = random.choice(most_likely_moves)
        # compute and replace ``percentage`` in the selected move
        move = move._replace(
            percentage=int(len(desired_moves) / len(moves) * 100)
        )

        if logger.level == logging.DEBUG:
            indent = '\t' * depth
            logger.debug(f'{indent}selected move: {move}')

        return move

    def _get_terminal_score(
        self, *, depth: int, gameboard: SquareGameboard, player: Player
    ) -> Tuple[int, int]:
        """Return ``score`` and ``percentage`` of terminal state.

        :param depth: The current depth of tree.
        :param gameboard: The gameboard relative to which the terminal
            score of the game will be calculated.
        :param player: The player relative to whom the terminal score
            of the game will be calculated.

        ``Percentage``::

            In the minimax algorithm, it doesn't matter how many ways
            to win AI at the end of the game. Therefore, the AI
            'stops fighting' and is not trying to 'steal' one of them.
            With the variable ``percentage``, the case with two
            possible moves to lose are worse than case with one move.
            This is especially important if the 'depth' of analysis is
            limited.

            Run example below with and without variable percentage once
            or twice::

                >>> from ap_games.game.tictactoe import TicTacToe
                >>> TicTacToe(
                ...     grid='X_OXX_O__',
                ...     player_types=('easy', 'hard')
                ... ).play()

            .. note::

                "hard" select cell randomly from all empty cells and can
                lose to "easy" without ``percentage``.

        ``Factor``::

            In the minimax algorithm, it doesn't matter when you lose:
            now or later. Therefore, the AI 'stops fighting' if it
            in any case loses the next moves, regardless of how it takes
            the move now. In this case, the AI considers that all the
            moves are the same bad, but this is wrong.

            Because the adversary can make a mistake, and adding the
            variable ``factor`` allows the AI to use a possible
            adversary errors in the future.

            With the ``factor``, losing now is worse than losing later.
            Therefore, the AI is trying not to 'give up' now and wait
            for better chances in the future.
            This is especially important if the 'depth' of analysis is
            limited.

            Run example below with and without variable factor once or
            twice:

                >>> TicTacToe(
                ...     grid='X_OX_____',
                ...     player_types=('easy', 'hard')
                ... ).play()

            .. note::

                'hard' select cell randomly from all empty cells and
                can lose to 'easy' without ``factor``.

        :returns: ``score`` and ``percentage``.  Where ``score`` is the
            score of the game with the given parameters, and ``percentage``
            is a number greater 0 and less than or equal to 100.

        """
        score: int
        percentage: int
        factor: int = 1

        depth_correction: int = 0
        game_status = self.game.get_status(
            gameboard=gameboard, player_mark=player.mark
        )
        if game_status.must_skip:
            player = self.game.get_next_player(player)
            depth_correction = 1
            game_status = game_status._replace(active=True)

        if game_status.active:
            if depth < self.max_depth:
                _, score, percentage = self._minimax(
                    depth=depth + 1 - depth_correction,
                    gameboard=gameboard,
                    player=player,
                )
            else:
                score = self.game.get_score(
                    gameboard=gameboard, player_mark=self.mark
                )
                percentage = 100
        else:
            factor *= self.max_depth + 1 - depth
            score = self.game.get_score(
                gameboard=gameboard, player_mark=self.mark
            )
            percentage = 100
        return score * factor, percentage

    def _fix_high_priority_coordinates_score(
        self, depth: int, moves: List[Step], player: Player
    ) -> List[Step]:
        """Change score of coordinates from high_priority_coordinates.

        TODO: FIx function with "switch off" it if there was reached
            the end of the game.

        .. note::

            This function only makes sense if the minimax algorithm is
            limited in depth and cannot reach the end of the game.

        Function increases "score" of move if it is the move of the
        current player , and decrease "score" of move if it is move of
        adversary player.

        :param depth: Current depth of tree.
        :param moves: Possible moves that should be checked.
        :param player: The player who moves.

        :return: The list of input ``moves`` with changed score of moves
            whose coordinates are in :attr:`.high_priority_coordinates`.

        """
        if self.game.high_priority_coordinates:
            if player is self:
                op = add
            else:
                op = sub
            return [
                move._replace(
                    score=op(
                        move.score,
                        self.game.high_priority_coordinates.get(
                            move.coordinate, 0
                        ),
                    )
                )
                for move in moves
            ]
        return moves

    def _extract_desired_moves(
        self, depth: int, moves: List[Step], player: Player
    ) -> List[Step]:
        """Calculate minimax score and returning moves with that score.

        Maximize score of self own move or minimize score of adversary
        moves.

        :param depth:  Current depth of tree.
        :param moves:  Possible moves that should be checked.
        :param player:  The player who moves.

        :return: A new list of moves that is a subset of the input
            moves.

        """
        if player is self:
            score_func = max
        else:
            score_func = min

        desired_score: int = score_func(move.score for move in moves)
        desired_moves: List[Step] = [
            move for move in moves if move.score == desired_score
        ]
        if logger.level == logging.DEBUG:
            indent: str = '\t' * depth
            logger.debug(
                f'{indent}desired score moves ({score_func}) -> '
                '{desired_moves}'
            )
        return desired_moves

    def _extract_most_likely_moves(
        self, depth: int, moves: List[Step], player: Player
    ) -> List[Step]:
        """Maximize probability of self own winning or adversary losing.

        .. warning::

            All input moves on this stage must have the same score.

        :param depth:  Current depth of tree.
        :param moves:  Possible moves that should be checked.
        :param player:  The player that moves and relative to which
            ``percentage_func`` will be determined.

        :return: A new list of moves that is a subset of the input
            moves.

        """
        desired_score: int = moves[0].score

        if (desired_score >= 0 and player is self) or (
            desired_score < 0 and player is not self
        ):
            percentage_func = max
        else:
            percentage_func = min
        desired_percentage: int = percentage_func(
            move.percentage for move in moves
        )
        most_likely_moves: List[Step] = [
            move for move in moves if move.percentage == desired_percentage
        ]
        if logger.level == logging.DEBUG:
            indent: str = '\t' * depth
            logger.debug(
                f'{indent}desired percentage moves ({percentage_func}) -> '
                f'{str(most_likely_moves)}'
            )
        return most_likely_moves
