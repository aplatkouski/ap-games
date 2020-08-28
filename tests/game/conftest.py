from typing import Literal

import pytest  # type: ignore

from ap_games.game.reversi import Reversi


@pytest.fixture(scope='package')
def reversi_user_user() -> Reversi:
    """Return Reversi game with the default grid and two human players."""
    user: Literal['user'] = 'user'
    return Reversi(player_types=(user, user))
