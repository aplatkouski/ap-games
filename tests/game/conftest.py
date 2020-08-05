import pytest  # type: ignore

from ap_games.game.reversi import Reversi


@pytest.fixture()
def reversi_user_user() -> Reversi:
    return Reversi(player_types=('user', 'user'))
