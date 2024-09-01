import socket
from dataclasses import dataclass


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

    GAME_OBJECT_CHECK_SCRIPT: str = """
    (function() {
        if (typeof window.game !== 'undefined' && window.game.players !== undefined) {
            return { status: 'success', message: 'ゲームオブジェクトが利用可能になりました。' };
        }
        if (document.readyState === 'complete') {
            return { status: 'loading', message: 'ページは読み込まれましたが、ゲームオブジェクトはまだ利用できません。' };
        }
        return { status: 'waiting', message: 'ページの読み込み中です。' };
    })()
    """

    @staticmethod
    def get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]
