from __future__ import annotations

import logging
from operator import add
from operator import sub
import random
from typing import TYPE_CHECKING

from ap_games.ap_types import Move
from ap_games.ap_types import Node
from ap_games.ap_types import UNDEFINED_MOVE
from ap_games.gameboard.gameboard import SquareGameboard
from ap_games.log import logger
from ap_games.player.player import Player

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Dict
    from typing import List
    from typing import Optional
    from typing import Set

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import GameStatus
    from ap_games.ap_types import PlayerMark
    from ap_games.ap_types import Tree
    from ap_games.game.game_base import TwoPlayerBoardGame

__all__ = ('AIPlayer',)


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
        self.tree: Tree = {}

    def move(self) -> Coordinate:
        """Define coordinate of the next move and return it.

        :returns: Coordinate chosen according to the minimax algorithm
            when :attr:`.max_depth` is not equal to 0.

        """
        logger.info(f'Making move level "{self.type_}" [{self.mark}]')

        if self.max_depth:
            return self._minimax().coordinate
        return self._random_coordinate()

    def _minimax(  # noqa: C901
        self,
        gameboard: Optional[SquareGameboard] = None,
        player_mark: Optional[PlayerMark] = None,
        depth: int = 0,
        tree: Optional[Tree] = None,
    ) -> Move:
        """Return the move selected by the minimax algorithm.

        Mini-max algorithm:

            1. Return the selected move with the terminal score, if a
               terminal state is achieved;
            2. Go through available moves on the board
               (:meth:`._go_through_available_moves`) or go through
               cached moves in :attr:`.tree`
               (:meth:`._go_through_subtree`). See docstrings
               corresponding method for details;
            3. Call the :meth:`._minimax` method on each available move
               (recursion) (:meth:`._get_terminal_score`);
            4. Evaluate returning values from minimax-method calls
               (:meth:`._choose_best_move`).  See next methods for
               details:

               * :meth:`._correct_priority_coordinates`;
               * :meth:`._extract_desired_moves`;
               * :meth:`._extract_most_likely_moves`.

            5. Return the best ``Move``.

        :param gameboard:  Optional.  If undefined, use
            :attr:`.game.gameboard`.  The gameboard relative to which
            the terminal score of the game will be calculated.
        :param player_mark:  Optional.  If undefined, use ``self.mark``.
            The player relative to whom the terminal score of the game
            will be calculated.
        :param depth:  Optional.  ``0`` by default.  The current depth
            of tree.
        :param tree:  Optional.  If undefined, use ``self.tree``.  It is
            cached tree possible cases as ``dict``.  Where key is a grid
            of the gameboard (as string), value is a nemedtuple ``Node``
            three fields.

            .. seealso::

                :class:`Node`.

        ``Percentage``::

            .. note::

                This is only important when the 'depth' of analysis is
                limited.

            In the minimax algorithm, it doesn't matter how many ways
            to win AI at the end of the game. Therefore, the AI
            'stops fighting' and is not trying to 'steal' one of them.
            With the variable ``percentage``, the case with two
            possible moves to lose are worse than case with one.

            Run example below with and without variable ``percentage``
            once or twice::

                >>> from ap_games.game.tictactoe import TicTacToe
                >>> TicTacToe(
                ...     grid='X_OXX_O__',
                ...     player_types=('easy', 'hard')
                ... ).play()

            .. note::

                "hard" select cell randomly from all empty cells and can
                lose to "easy" without ``percentage``.

        ``Factor``::

            .. note::

                This is only important when the 'depth' of analysis is
                limited.

            In the minimax algorithm, it doesn't matter when you lose:
            now or later. Therefore, the AI 'stops fighting' if it
            in any case loses the next moves, regardless of how it takes
            the move now. In this case, the AI considers that all the
            moves are the same bad.

            Because the enemy can make a mistake, and adding the
            variable ``last_move_coefficient`` allows the AI to use a
            possible enemy errors in the future.

            With the ``last_move_coefficient``, losing now is worse than
            losing later.  Therefore, the AI is trying not to 'give up'
            now and wait for better chances in the future.

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
            algorithm as a namedtuple :class:`Move` instance.

            .. seealso::

                :class:`Move`.

        """
        if gameboard is None:
            gameboard = self.game.gameboard
        if player_mark is None:
            player_mark = self.mark
        if tree is None:
            self._unpack_tree()
            tree = self.tree

        node: Node = tree.setdefault(
            gameboard.grid_as_string,
            Node(player_mark=player_mark, move=UNDEFINED_MOVE, sub_tree={},),
        )
        last_move_coefficient: int = 1
        last: bool = False

        game_status: GameStatus = self.game.get_status(gameboard, player_mark)

        if game_status.must_skip:
            player_mark = self.game.get_enemy_mark(player_mark)
            depth -= 1
            game_status = game_status._replace(active=True)

        if game_status.active:
            if depth < self.max_depth:
                if node.sub_tree:
                    return self._go_through_subtree(
                        depth=depth + 1, tree=node.sub_tree,
                    )
                else:  # node.sub_tree == {}
                    return self._go_through_available_moves(
                        gameboard=gameboard,
                        player_mark=player_mark,
                        depth=depth + 1,
                        tree=node.sub_tree,
                    )
        else:
            # 10 >= max possible self.game.gameboard.size
            last_move_coefficient = 10 * 10 ** (self.max_depth - depth + 1)
            last = True

        # in minimax algorithm ``score`` is always computed relative to
        # current (``self``) player
        score: int = self.game.get_score(gameboard, player_mark=self.mark)
        return Move(
            coordinate=self.game.gameboard.undefined_coordinate,
            score=score * last_move_coefficient,
            percentage=100,
            last=last,
        )

    def _go_through_available_moves(
        self,
        gameboard: SquareGameboard,
        player_mark: PlayerMark,
        depth: int,
        tree: Tree,
    ) -> Move:
        """Call minimax method on each available move.

        :param gameboard:  The gameboard relative to which the terminal
            score of the game will be calculated.
        :param player_mark:  The mark of player relative to whom the
            terminal score of the game will be calculated.
        :param depth:  The current depth of tree.
        :param tree:  The cache that will be filled up by this method.

            .. warning::

                ``tree`` is always an empty dict.

        :returns:  The move selected by the minimax algorithm as
            instance of namedtuple :class:`Move`.

        """
        moves: List[Move] = []
        for coordinate in self.game.get_available_moves(
            gameboard, player_mark
        ):
            fake_gameboard: SquareGameboard = gameboard.copy(
                indent='\t' * depth
            )
            self.game.place_mark(coordinate, player_mark, fake_gameboard)

            move: Move = self._get_terminal_score(
                coordinate=coordinate,
                player_mark=player_mark,
                gameboard=fake_gameboard,
                depth=depth,
                tree=tree,
            )
            moves.append(move)
        return self._choose_best_move(moves, player_mark, depth)

    def _go_through_subtree(self, depth: int, tree: Tree) -> Move:
        """Call minimax method on each node of tree.

        :param depth:  The current depth of tree.
        :param tree:  The tree of cached moves.

            .. warning::  ``tree`` is always not empty dict.

        :raises ValueError: When there are nodes in the same level with
            different ``player_mark``.

        :returns:  The move selected by the minimax algorithm as
            instance of namedtuple :class:`Move`.

        """
        player_marks: Set[PlayerMark] = set()
        moves: List[Move] = []
        for grid, node in tree.items():
            if node.move.last:
                moves.append(node.move)
            else:
                coordinate: Coordinate = node.move.coordinate
                player_mark: PlayerMark = node.player_mark
                indent: str = '\t' * depth
                if node.sub_tree:
                    if logger.level == logging.DEBUG:
                        logger.debug(f'\n{indent}[{player_mark}] {coordinate}')
                        logger.debug(f'{indent}[{grid}]')
                    move: Move = self._go_through_subtree(
                        depth=depth + 1, tree=node.sub_tree
                    )
                    move = move._replace(coordinate=coordinate)
                    tree[grid] = Node(
                        player_mark=player_mark,
                        move=move,
                        sub_tree=node.sub_tree,
                    )
                    moves.append(move)
                else:  # node.sub_tree == {}:
                    # don't compare ``depth`` and ``max_depth``, because
                    # ``max_depth`` doesn't change during game.
                    # Therefore cached ``tree`` will never be deeper
                    # than ``max_depth``.
                    fake_gameboard: SquareGameboard = SquareGameboard(
                        grid=grid, indent=indent, colorized=False,
                    )

                    move = self._get_terminal_score(
                        coordinate=coordinate,
                        player_mark=player_mark,
                        gameboard=fake_gameboard,
                        depth=depth,
                        tree=tree,
                    )
                    moves.append(move)
            player_marks.add(node.player_mark)
        if len(player_marks) > 1:
            raise ValueError("Impossible!")
        return self._choose_best_move(moves, player_marks.pop(), depth)

    def _get_terminal_score(
        self,
        coordinate: Coordinate,
        player_mark: PlayerMark,
        gameboard: SquareGameboard,
        depth: int,
        tree: Tree,
    ) -> Move:
        if logger.level == logging.DEBUG:
            indent: str = '\t' * depth
            logger.debug(f'\n{indent}[{player_mark}] {coordinate}')
            logger.debug(gameboard)

        next_player_mark: PlayerMark = self.game.get_enemy_mark(player_mark)
        move: Move = self._minimax(
            gameboard=gameboard,
            player_mark=next_player_mark,
            depth=depth,
            tree=tree,
        )
        grid: str = gameboard.grid_as_string
        move = move._replace(coordinate=coordinate)
        sub_tree: Tree = tree[grid].sub_tree
        tree[grid] = Node(
            player_mark=player_mark, move=move, sub_tree=sub_tree
        )
        return move

    def _unpack_tree(self) -> None:
        node: Node
        grid: str = self.game.gameboard.grid_as_string
        while self.tree and (grid not in self.tree):
            new_tree: Tree = {}
            for node in self.tree.values():
                if node.sub_tree:
                    new_tree.update(node.sub_tree)
            self.tree = new_tree

    def _choose_best_move(
        self, moves: List[Move], player_mark: PlayerMark, depth: int,
    ) -> Move:
        indent: str = '\t' * depth

        if logger.level == logging.DEBUG:
            logger.debug(
                f'{indent}Choose the best move from moves -> ' f'{str(moves)}'
            )

        corrected_moves: List[Move] = self._correct_priority_coordinates(
            moves=moves, player_mark=player_mark, depth=depth
        )

        desired_moves: List[Move] = self._extract_desired_moves(
            moves=corrected_moves, player_mark=player_mark, depth=depth
        )

        most_likely_moves: List[Move] = self._extract_most_likely_moves(
            moves=desired_moves, player_mark=player_mark, depth=depth
        )

        move: Move = random.choice(most_likely_moves)
        # compute and replace ``percentage`` in the selected move
        move = move._replace(
            percentage=int(len(desired_moves) / len(moves) * move.percentage)
        )

        if logger.level == logging.DEBUG:
            logger.debug(f'{indent}Selected move: {move}')

        return move

    def _correct_priority_coordinates(
        self, moves: List[Move], player_mark: PlayerMark, depth: int,
    ) -> List[Move]:
        """Change score of moves from with high priority coordinates.

        .. note::

            This function only makes sense if the minimax algorithm is
            limited in depth and cannot reach the end of the game.

        Function increases "score" of move if it is the move of the
        current player , and decrease "score" of move if it is move of
        enemy player.

        :param moves:  Possible moves that should be checked.
        :param player_mark:  The mark of player who moves.
        :param depth:  Current depth of tree.

        :return:  The list of input ``moves`` with changed score of moves
            whose coordinates are in :attr:`.priority_coordinates`.

        """
        if not self.game.priority_coordinates:
            return moves

        if player_mark == self.mark:
            op = add
        else:
            op = sub
        corrected_moves: List[Move] = []
        for move in moves:
            if move.coordinate in self.game.priority_coordinates:
                corrected_moves.append(
                    move._replace(
                        score=op(
                            move.score,
                            self.game.priority_coordinates[move.coordinate],
                        )
                    )
                )
            else:
                corrected_moves.append(move)
        return corrected_moves

    def _extract_desired_moves(
        self, moves: List[Move], player_mark: PlayerMark, depth: int
    ) -> List[Move]:
        """Calculate min-max score and returning moves with that score.

        Maximize score of self own move or minimize score of enemy
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
                f'{indent}Desired score moves ({score_func}) -> '
                f'{desired_moves}'
            )
        return desired_moves

    def _extract_most_likely_moves(
        self, moves: List[Move], player_mark: PlayerMark, depth: int
    ) -> List[Move]:
        """Maximize probability of self own winning or enemy losing.

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

        if (desired_score > 0 and player_mark == self.mark) or (
            desired_score <= 0 and player_mark != self.mark
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
                f'{indent}Desired percentage moves ({percentage_func}) -> '
                f'{str(most_likely_moves)}'
            )
        return most_likely_moves
