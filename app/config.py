import socket
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    WINDOW_TIMEOUT: int = 60
    GAME_OBJECT_TIMEOUT: int = 20
    TARGET_URL_PREFIX: str = "https://app.gather.town"
    GATHER_APP_NAME: str = "Gather"
    MAX_ATTEMPTS: int = 30
    DELAY: int = 2

    # デバッグポートの疎通確認
    MAX_ATTEMPTS_DEBUG_PORT: int = 30
    DEBUG_PORT_DELAY: int = 1

    _game_object_check_script: str = None

    @classmethod
    def get_game_object_check_script(cls) -> str:
        """game_object_check.jsの内容を読み込んで返します"""
        if cls._game_object_check_script is None:
            js_file_path = Path(__file__).parent / "static/js/game_object_check.js"
            try:
                with open(js_file_path, "r") as f:
                    cls._game_object_check_script = f.read()
            except FileNotFoundError:
                raise ValueError(f"JavaScriptファイルが見つかりません: {js_file_path}")
        return cls._game_object_check_script

    @staticmethod
    def get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]
