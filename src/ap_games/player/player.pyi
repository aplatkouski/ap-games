from functools import cached_property
from ap_games.game.game_base import GameBase
from ap_games.types import Coordinate
from ap_games.types import Label

TEST_MODE: bool

class Player:
    type: str
    _game: GameBase
    _label: Label
    def __init__(self, type_: str, /, *, game: GameBase, label: Label) -> None: ...
    def __str__(self) -> str: ...
    @cached_property
    def game(self) -> GameBase: ...
    @cached_property
    def label(self) -> Label: ...
    def _random_coordinate(self) -> Coordinate: ...
    def go(self) -> Coordinate: ...
