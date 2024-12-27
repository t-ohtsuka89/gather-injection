import os
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ScriptConfig:
    """スクリプト実行に関する設定"""

    MAX_SIZE_BYTES: int = field(
        default_factory=lambda: int(
            os.getenv("GATHER_SCRIPT_MAX_SIZE", str(1024 * 1024))
        )
    )
    ALLOWED_EXTENSIONS: set[str] = field(default_factory=lambda: {"js"})
    EXECUTION_TIMEOUT: float = field(
        default_factory=lambda: float(os.getenv("GATHER_SCRIPT_TIMEOUT", "30.0"))
    )


@dataclass
class NetworkConfig:
    """ネットワーク関連の設定"""

    WINDOW_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv("GATHER_WINDOW_TIMEOUT", "60"))
    )
    GAME_OBJECT_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv("GATHER_GAME_OBJECT_TIMEOUT", "20"))
    )
    TARGET_URL_PREFIX: str = field(
        default_factory=lambda: os.getenv(
            "GATHER_TARGET_URL", "https://app.gather.town"
        )
    )
    MAX_ATTEMPTS_DEBUG_PORT: int = field(
        default_factory=lambda: int(os.getenv("GATHER_MAX_ATTEMPTS_DEBUG_PORT", "30"))
    )
    DEBUG_PORT_DELAY: int = field(
        default_factory=lambda: int(os.getenv("GATHER_DEBUG_PORT_DELAY", "1"))
    )


@dataclass
class AppConfig:
    """アプリケーション全般の設定"""

    GATHER_APP_NAME: str = field(
        default_factory=lambda: os.getenv("GATHER_APP_NAME", "Gather")
    )
    LOG_LEVEL: str = field(
        default_factory=lambda: os.getenv("GATHER_LOG_LEVEL", "INFO")
    )
    RETRY_COUNT: int = field(
        default_factory=lambda: int(os.getenv("GATHER_RETRY_COUNT", "3"))
    )
    RETRY_DELAY: float = field(
        default_factory=lambda: float(os.getenv("GATHER_RETRY_DELAY", "1.0"))
    )


@dataclass
class Config:
    """設定の統合管理クラス"""

    script: ScriptConfig = field(default_factory=ScriptConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    app: AppConfig = field(default_factory=AppConfig)

    # JavaScriptの実行に関する定数
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
    def get_free_port() -> int:
        """利用可能なポート番号を取得します"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """環境変数から設定を読み込みます"""
        if env_file and Path(env_file).exists():
            # .envファイルが存在する場合は読み込む
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value

        return cls()
