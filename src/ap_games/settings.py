from __future__ import annotations

from configparser import ConfigParser
import os
from pathlib import Path
from typing import final
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from typing import Optional

    from ap_games.ap_collections import Config

__all__ = ('Settings',)


@final
class Settings:
    """Class introduces the settings of the `ap_games` module."""

    _singleton: Settings | None = None

    def __new__(cls, **kwargs: Any) -> Any:
        """Return one "single" instance of current class.

        :param kwargs: constructor arguments.

        """
        if not cls._singleton:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(
        self,
        *,
        config_file: str = '',
        log_file: str = '',
        log_level: str = '',
        test_mode: bool | None = None,
    ) -> None:
        self.base_dir: Path = Path(__file__).parent.resolve(strict=True)

        config_file = config_file or os.environ.get(
            'AP_GAMES_CONFIGFILE', 'config.ini'
        )
        self.path_to_config_file: Path = self.base_dir / config_file
        self.config_ini: Config = {}
        self.read_config()

        log_file = (
            log_file
            or os.environ.get('AP_GAMES_LOGFILE')
            or self.config_ini['log_file']
        )
        self.path_to_log_file: Path = self.base_dir / log_file

        self.log_level: str = (
            log_level
            or os.environ.get('AP_GAMES_LOGLEVEL')
            or self.config_ini['log_level']
        )

        self.test_mode: bool = (
            test_mode
            if (test_mode is not None)
            else self.config_ini['test_mode']
        )

    def read_config(self) -> None:
        """Read the configuration from `config.ini` and set it."""
        if self.path_to_config_file.exists():
            cfg = ConfigParser()
            cfg.read_file(open(self.path_to_config_file))
            log_level: str = cfg.get(
                'ap-games', 'log_level', fallback='INFO'
            ).upper()
            self.config_ini['log_level'] = (
                log_level if log_level == 'DEBUG' else 'INFO'
            )
            self.config_ini['log_file'] = cfg.get(
                'ap-games', 'log_file', fallback='ap_games.log'
            )
            self.config_ini['test_mode'] = cfg.getboolean(
                'ap-games', 'test_mode', fallback=False
            )
