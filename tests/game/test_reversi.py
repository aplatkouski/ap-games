from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_collections import Coordinate
from ap_games.ap_collections import GameStatus
from ap_games.game.reversi import Reversi
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import Literal
    from typing import Tuple

    from ap_games.ap_typing import Coordinates
    from ap_games.ap_typing import PlayerType


class TestReversi:
    def test_reversi_interface(
        self, reversi_user_user: Reversi, reversi_interface: str
    ) -> None:
        assert hasattr(reversi_user_user, reversi_interface)

    def test_gameboard(self, reversi_gameboard_as_string: str) -> None:
        assert (
            reversi_gameboard_as_string
            == Reversi(
                grid=reversi_gameboard_as_string
            ).gameboard.grid_as_string
        )

    def test_default_gameboard(self, default_gameboard_as_string: str) -> None:
        user: Literal['user'] = 'user'
        assert (
            default_gameboard_as_string
            == Reversi(player_types=(user, user)).gameboard.grid_as_string
        )

    def test_wrong_players_number(self, wrong_players_number: int) -> None:
        user: PlayerType = 'user'
        player_types: tuple[PlayerType, ...] = (user,) * wrong_players_number
        with pytest.raises(ValueError, match='number of players') as e:
            Reversi(player_types=player_types)  # type: ignore
        assert 'The number of players should be 2!' == str(e.value)

    def test_grid_with_underscore(self) -> None:
        user: PlayerType = 'user'
        assert (
            ' ' * 64
            == Reversi(
                grid='_' * 64, player_types=(user, user)
            ).gameboard.grid_as_string
        )

    def test_inappropriate_grid_character(
        self, wrong_grid_symbol: str
    ) -> None:
        user: PlayerType = 'user'
        with pytest.raises(ValueError, match='must contain') as e:
            Reversi(grid=wrong_grid_symbol * 64, player_types=(user, user))
        assert (
            'Gameboard must contain only " ", "_" and symbols '
            "from ('X', 'O')."
        ) == str(e.value)

    @pytest.mark.parametrize(
        ('gameboard_grid', 'player_mark', 'score'),
        [
            ('   OOOXXX', 'X', 0),
            ('   OOXXXX', 'X', 2),
            ('   OOOOXX', 'X', -2),
        ],
        ids=lambda arg: f'{arg}',
    )
    def test_get_score(
        self,
        gameboard_grid: str,
        player_mark: Literal['X'],
        score: int,
        reversi_user_user: Reversi,
    ) -> None:
        gameboard: SquareGameboard = SquareGameboard(grid=gameboard_grid)
        assert score == reversi_user_user.get_score(gameboard, player_mark)

    @pytest.mark.parametrize(
        ('gameboard_grid', 'player_mark', 'available_moves'),
        [
            (
                '   OOOXXX',
                'X',
                (Coordinate(1, 3), Coordinate(3, 3), Coordinate(2, 3)),
            ),
            ('   OXOXXX', 'X', (Coordinate(1, 3), Coordinate(3, 3))),
            ('   OXXXXX', 'X', (Coordinate(1, 3),)),
            (
                '   XXXOOO',
                'X',
                (),
            ),
        ],
        ids=lambda arg: f'{arg}',
    )
    def test_get_available_moves(
        self,
        gameboard_grid: str,
        player_mark: Literal['X'],
        available_moves: Coordinates,
        reversi_user_user: Reversi,
    ) -> None:
        gameboard: SquareGameboard = SquareGameboard(grid=gameboard_grid)
        assert available_moves == reversi_user_user.get_available_moves(
            gameboard, player_mark
        )

    @pytest.mark.parametrize(
        ('gameboard_grid', 'player_mark', 'game_status'),
        [
            (
                '   OOOXXX',
                'X',
                GameStatus(active=True, message='', must_skip=False),
            ),
            (
                '   XXXOOO',
                'X',
                GameStatus(
                    active=False,
                    message='\nThe player [X] has no moves available!\n',
                    must_skip=True,
                ),
            ),
            (
                'XXXXXXOOO',
                'X',
                GameStatus(
                    active=False,
                    message='X wins\n',
                    must_skip=False,
                ),
            ),
            (
                'XXXOOOOOO',
                'X',
                GameStatus(
                    active=False,
                    message='O wins\n',
                    must_skip=False,
                ),
            ),
            (
                ' OOOXXOXX',
                'X',
                GameStatus(
                    active=False,
                    message='Draw\n',
                    must_skip=False,
                ),
            ),
        ],
    )
    def test_get_status(
        self,
        gameboard_grid: str,
        player_mark: Literal['X'],
        game_status: GameStatus,
        reversi_user_user: Reversi,
    ) -> None:
        gameboard: SquareGameboard = SquareGameboard(grid=gameboard_grid)
        assert game_status == reversi_user_user.get_status(
            gameboard, player_mark
        )

    @pytest.mark.parametrize(
        ('coordinate', 'player_mark', 'gameboard_grid', 'score'),
        [
            (
                Coordinate(1, 3),
                'X',
                '   OOOXXX',
                3,
            ),
            (
                Coordinate(2, 3),
                'X',
                '   OOOXXX',
                2,
            ),
            (
                Coordinate(1, 1),
                'X',
                '   OOOXXX',
                0,
            ),
            (
                Coordinate(1, 3),
                'X',
                '   XXXOOO',
                0,
            ),
        ],
        ids=lambda arg: f'{arg}',
    )
    def test_place_mark(
        self,
        coordinate: Coordinate,
        player_mark: Literal['X'],
        gameboard_grid: str,
        score: int,
        reversi_user_user: Reversi,
    ) -> None:
        gameboard: SquareGameboard = SquareGameboard(grid=gameboard_grid)
        assert score == reversi_user_user.place_mark(
            coordinate, player_mark, gameboard
        )

    def test_fill_available_moves_cache(
        self, reversi_user_user: Reversi
    ) -> None:
        coordinate: Coordinate = Coordinate(6, 5)
        player_mark: Literal['X'] = 'X'

        grid: str = reversi_user_user.gameboard.grid_as_string
        reversi_user_user.place_mark(
            coordinate=coordinate,
            player_mark=player_mark,
            gameboard=SquareGameboard(grid=grid),
        )
        assert [
            Coordinate(x=5, y=5)
        ] == reversi_user_user._available_moves_cache[grid, player_mark][
            coordinate
        ]
        reversi_user_user.place_mark(
            coordinate=coordinate,
            player_mark=player_mark,
        )
        assert (
            grid,
            player_mark,
        ) not in reversi_user_user._available_moves_cache
