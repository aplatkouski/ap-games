from __future__ import annotations

from typing import cast
from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_constants import EMPTY
from ap_games.game.reversi import Reversi
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import Any
    from typing import Literal


@pytest.fixture(
    scope='session',
    params=[
        'get_status',
        'place_mark',
        'get_available_moves',
        'get_score',
        'default_grid',
        'grid_axis',
        'grid_gap',
        'supported_players',
        'rules',
        'priority_coordinates',
        'players',
    ],
    ids=lambda interface: f'{interface=}',
)
def reversi_interface(request: Any) -> str:
    return cast(str, request.param)


@pytest.fixture(scope='session')
def reversi_gameboard_as_string() -> str:
    return (
        '        '
        '        '
        '   X X  '
        '  OOOO  '
        '  XOO   '
        '    OX  '
        '        '
        '        '
    )


@pytest.fixture(scope='session')
def default_gameboard_as_string() -> str:
    return f'{EMPTY * 27}XO{EMPTY * 6}OX{EMPTY * 27}'


@pytest.fixture(
    scope='session',
    params=[0, 1, 3],
    ids=lambda players_number: f'{players_number=}',
)
def wrong_players_number(request: Any) -> int:
    return cast(int, request.param)


@pytest.fixture(
    scope='session',
    params=['0', 'A', '/'],
    ids=lambda symbol: f'{symbol=}',
)
def wrong_grid_symbol(request: Any) -> str:
    return cast(str, request.param)


@pytest.fixture()
def reversi_user_user(default_gameboard_as_string: str) -> Reversi:
    """Return Reversi game with the default grid and two human players.

    :param default_gameboard_as_string:  The start Reversi board as
        string.

    """
    user: Literal['user'] = 'user'
    return Reversi(grid=default_gameboard_as_string, player_types=(user, user))


@pytest.fixture()
def reversi_gameboard(reversi_gameboard_as_string: str) -> SquareGameboard:
    return SquareGameboard(grid=reversi_gameboard_as_string)


@pytest.fixture(scope='package')
def reversi_medium_x_easy_o(reversi_gameboard_as_string: str) -> Reversi:
    medium: Literal['medium'] = 'medium'
    easy: Literal['easy'] = 'easy'
    return Reversi(
        grid=reversi_gameboard_as_string, player_types=(medium, easy)
    )
