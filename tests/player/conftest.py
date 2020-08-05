from __future__ import annotations

import pytest  # type: ignore

from ap_games.game.game_base import TwoPlayerBoardGame
from ap_games.player.player import Player


@pytest.fixture()
def game() -> TwoPlayerBoardGame:
    return TwoPlayerBoardGame(grid='XO X')


@pytest.fixture()
def player_user_x(game: TwoPlayerBoardGame) -> Player:
    return Player('user', mark='X', game=game)
