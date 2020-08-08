from __future__ import annotations

import logging
from operator import add
from operator import sub
import random
from typing import TYPE_CHECKING

from ap_games.ap_types import Move
from ap_games.gameboard.gameboard import SquareGameboard
from ap_games.log import logger
from ap_games.player.player import Player
from ap_games.player.player import TEST_MODE

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Dict
    from typing import List
    from typing import Optional

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import GameStatus
    from ap_games.ap_types import PlayerMark
    from ap_games.game.game_base import TwoPlayerBoardGame

__all__ = ('AIPlayer',)

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
            return self._minimax().coordinate
        return self._random_coordinate()

    def _minimax(
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
        depth: int = 0,
    ) -> Move:
        """Return the move selected by the minimax algorithm.

        Mini-max algorithm:

            1. Return the selected move with the terminal score, if a
               terminal state is chieved;
            2. Go through available moves on the board. See
               :meth:`._get_terminal_move` docstrings for details;
            3. Call the :meth:`._minimax` method on each available move
               (recursion);
            4. Evaluate returning values from method calls. See next
               methods for details:

               * :meth:`._fix_high_priority_coordinates_score`;
               * :meth:`._extract_desired_moves`;
               * :meth:`._extract_most_likely_moves`.

            5. Return the best ``Move``.

        :param gameboard:  Optional.  If undefined, use
            :attr:`.game.gameboard`.  The gameboard relative to which
            the terminal score of the game will be calculated.
        :param player_mark:  Optional.  If undefined, use ``self.mark``.
            The player relative to whom the terminal score of the game
            will be calculated.
        :param depth:  Optional.  ``0`` by default. The current depth of
            tree.


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
            variable ``last_move_coefficient`` allows the AI to use a
            possible adversary errors in the future.

            With the ``last_move_coefficient``, losing now is worse than
            losing later.  Therefore, the AI is trying not to 'give up'
            now and wait for better chances in the future.
            This is especially important if the 'depth' of analysis is
            limited.

            Run example below with and without variable
            ``last_move_coefficient`` once or twice:

                >>> TicTacToe(
                ...     grid='X_OX_____',
                ...     player_types=('easy', 'hard')
                ... ).play()

            .. note::

                'hard' select cell randomly from all empty cells and
                can lose to 'easy' without ``last_move_coefficient``.

        :returns:  The move is selected according to the minimax
            algorithm as a namedtuple :class:`Move` instance with three
            fields:

                * ``coordinate``.  The coordinate of selected cell or
                  ``undefined_coordinate`` if game status is ``False``;
                * ``score``.  The game score with specified parameters;
                * ``percentage``.  The percentage to reach ``score`` as
                  a number greater 0 and less than or equal to 100.  See
                  description above.

        """
        if gameboard is None:
            gameboard = self.game.gameboard
        if player_mark is None:
            player_mark = self.mark

        last_move_coefficient: int = 1

        game_status: GameStatus = self.game.get_status(gameboard, player_mark)

        if game_status.must_skip:
            player_mark = self.game.get_adversary_mark(player_mark)
            depth -= 1
            game_status = game_status._replace(active=True)

        if game_status.active:
            if depth < self.max_depth:
                # TODO: I need to save only tree of coordinates in cache
                return self._get_terminal_move(
                    gameboard=gameboard,
                    player_mark=player_mark,
                    depth=depth + 1,
                )
        else:
            last_move_coefficient = 10 ** (self.max_depth - depth + 1)

        # in minimax algorithm ``score`` is always computed relative to
        # current (``self``) player
        score: int = self.game.get_score(gameboard, player_mark=self.mark)
        return Move(
            coordinate=self.game.gameboard.undefined_coordinate,
            score=score * last_move_coefficient,
            percentage=100,
        )

    def _get_terminal_move(
        self, gameboard: SquareGameboard, player_mark: PlayerMark, depth: int,
    ) -> Move:
        """Call minimax method on each available move.

        :param gameboard:  The gameboard relative to which the terminal
            score of the game will be calculated.
        :param player_mark:  The mark of player relative to whom the
            terminal score of the game will be calculated.
        :param depth:  The current depth of tree.

        :returns:  The move selected by the minimax algorithm as
            instance of namedtuple :class:`Move`.

        """
        moves: List[Move] = []
        indent: str = '\t' * depth

        for coordinate in self.game.get_available_moves(
            gameboard, player_mark
        ):
            fake_gameboard: SquareGameboard = gameboard.copy()
            fake_gameboard.indent = indent
            self.game.place_mark(coordinate, player_mark, fake_gameboard)

            if logger.level == logging.DEBUG:
                logger.debug(f'\n{indent}[{player_mark}] {coordinate}')
                logger.debug(fake_gameboard)

            next_player_mark: PlayerMark = self.game.get_adversary_mark(
                player_mark
            )

            move: Move = self._minimax(
                gameboard=fake_gameboard,
                player_mark=next_player_mark,
                depth=depth,
            )
            moves.append(move._replace(coordinate=coordinate))

        fixed_moves: List[Move] = self._fix_high_priority_coordinates_score(
            moves=moves, player_mark=player_mark, depth=depth
        )

        desired_moves: List[Move] = self._extract_desired_moves(
            moves=fixed_moves, player_mark=player_mark, depth=depth
        )

        most_likely_moves: List[Move] = self._extract_most_likely_moves(
            moves=desired_moves, player_mark=player_mark, depth=depth
        )

        move = random.choice(most_likely_moves)
        # compute and replace ``percentage`` in the selected move
        move = move._replace(
            percentage=int(len(desired_moves) / len(moves) * 100)
        )

        if logger.level == logging.DEBUG:
            logger.debug(f'{indent}selected move: {move}')

        return move

    def _fix_high_priority_coordinates_score(
        self, moves: List[Move], player_mark: PlayerMark, depth: int,
    ) -> List[Move]:
        """Change score of moves from with high priority coordinates.

        .. note::

            This function only makes sense if the minimax algorithm is
            limited in depth and cannot reach the end of the game.

        Function increases "score" of move if it is the move of the
        current player , and decrease "score" of move if it is move of
        adversary player.

        :param moves:  Possible moves that should be checked.
        :param player_mark:  The mark of player who moves.
        :param depth:  Current depth of tree.

        :return:  The list of input ``moves`` with changed score of moves
            whose coordinates are in :attr:`.high_priority_coordinates`.

        """
        if self.game.high_priority_coordinates:
            if player_mark == self.mark:
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
        self, moves: List[Move], player_mark: PlayerMark, depth: int
    ) -> List[Move]:
        """Calculate min-max score and returning moves with that score.

        Maximize score of self own move or minimize score of adversary
        moves.

        :param moves:  Possible moves that should be checked.
        :param player_mark:  The mark of player who moves.
        :param depth:  Current depth of tree.

        :return:  A new list of moves that is a subset of the input
            moves.

        """
        if player_mark == self.mark:
            score_func = max
        else:
            score_func = min

        desired_score: int = score_func(move.score for move in moves)
        desired_moves: List[Move] = [
            move for move in moves if move.score == desired_score
        ]
        if logger.level == logging.DEBUG:
            indent: str = '\t' * depth
            logger.debug(
                f'{indent}desired score moves ({score_func}) -> '
                f'{desired_moves}'
            )
        return desired_moves

    def _extract_most_likely_moves(
        self, moves: List[Move], player_mark: PlayerMark, depth: int
    ) -> List[Move]:
        """Maximize probability of self own winning or adversary losing.

        .. warning::

            All input moves on this stage must have the same score.

        :param depth:  Current depth of tree.
        :param moves:  Possible moves that should be checked.
        :param player_mark:  The mark of player who moves and relative
            to which ``percentage_func`` will be determined.

        :return:  A new list of moves that is a subset of the input
            moves.

        """
        desired_score: int = moves[0].score

        if (desired_score >= 0 and player_mark == self.mark) or (
            desired_score < 0 and player_mark != self.mark
        ):
            percentage_func = max
        else:
            percentage_func = min
        desired_percentage: int = percentage_func(
            move.percentage for move in moves
        )
        most_likely_moves: List[Move] = [
            move for move in moves if move.percentage == desired_percentage
        ]
        if logger.level == logging.DEBUG:
            indent: str = '\t' * depth
            logger.debug(
                f'{indent}desired percentage moves ({percentage_func}) -> '
                f'{str(most_likely_moves)}'
            )
        return most_likely_moves
