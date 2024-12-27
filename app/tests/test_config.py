import os

import pytest

from app.config import (
    AppConfig,
    Config,
    ConfigValidationError,
    NetworkConfig,
    ScriptConfig,
)


@pytest.fixture
def clean_env():
    """環境変数をクリーンな状態にするフィクスチャ"""
    # テスト前に関連する環境変数を保存
    saved_env = {}
    env_vars = [
        "GATHER_SCRIPT_MAX_SIZE",
        "GATHER_SCRIPT_TIMEOUT",
        "GATHER_WINDOW_TIMEOUT",
        "GATHER_GAME_OBJECT_TIMEOUT",
        "GATHER_TARGET_URL",
        "GATHER_MAX_ATTEMPTS_DEBUG_PORT",
        "GATHER_DEBUG_PORT_DELAY",
        "GATHER_APP_NAME",
        "GATHER_LOG_LEVEL",
        "GATHER_RETRY_COUNT",
        "GATHER_RETRY_DELAY",
    ]
    for var in env_vars:
        if var in os.environ:
            saved_env[var] = os.environ[var]
            del os.environ[var]

    yield

    # テスト後に環境変数を復元
    for var in env_vars:
        if var in saved_env:
            os.environ[var] = saved_env[var]
        elif var in os.environ:
            del os.environ[var]


class TestScriptConfig:
    def test_default_values(self, clean_env):
        """デフォルト値の検証"""
        config = ScriptConfig()
        assert config.MAX_SIZE_BYTES == 1024 * 1024
        assert config.ALLOWED_EXTENSIONS == {"js"}
        assert config.EXECUTION_TIMEOUT == 30.0

    def test_custom_values_from_env(self, clean_env):
        """環境変数からの値の読み込み"""
        os.environ["GATHER_SCRIPT_MAX_SIZE"] = "2097152"  # 2MB
        os.environ["GATHER_SCRIPT_TIMEOUT"] = "60.0"
        config = ScriptConfig()
        assert config.MAX_SIZE_BYTES == 2097152
        assert config.EXECUTION_TIMEOUT == 60.0

    def test_invalid_max_size(self, clean_env):
        """不正なMAX_SIZE_BYTESの検証"""
        os.environ["GATHER_SCRIPT_MAX_SIZE"] = "0"
        with pytest.raises(
            ConfigValidationError, match="MAX_SIZE_BYTESは正の値である必要があります"
        ):
            ScriptConfig().validate()

    def test_invalid_timeout(self, clean_env):
        """不正なEXECUTION_TIMEOUTの検証"""
        os.environ["GATHER_SCRIPT_TIMEOUT"] = "-1.0"
        with pytest.raises(
            ConfigValidationError, match="EXECUTION_TIMEOUTは正の値である必要があります"
        ):
            ScriptConfig().validate()


class TestNetworkConfig:
    def test_default_values(self, clean_env):
        """デフォルト値の検証"""
        config = NetworkConfig()
        assert config.WINDOW_TIMEOUT == 60
        assert config.GAME_OBJECT_TIMEOUT == 20
        assert config.TARGET_URL_PREFIX == "https://app.gather.town"
        assert config.MAX_ATTEMPTS_DEBUG_PORT == 30
        assert config.DEBUG_PORT_DELAY == 1

    def test_custom_values_from_env(self, clean_env):
        """環境変数からの値の読み込み"""
        os.environ["GATHER_WINDOW_TIMEOUT"] = "120"
        os.environ["GATHER_TARGET_URL"] = "https://custom.gather.town"
        config = NetworkConfig()
        assert config.WINDOW_TIMEOUT == 120
        assert config.TARGET_URL_PREFIX == "https://custom.gather.town"

    def test_invalid_url_prefix(self, clean_env):
        """不正なTARGET_URL_PREFIXの検証"""
        os.environ["GATHER_TARGET_URL"] = "invalid-url"
        with pytest.raises(
            ConfigValidationError,
            match="TARGET_URL_PREFIXは有効なURLプレフィックスである必要があります",
        ):
            NetworkConfig().validate()


class TestAppConfig:
    def test_default_values(self, clean_env):
        """デフォルト値の検証"""
        config = AppConfig()
        assert config.GATHER_APP_NAME == "Gather"
        assert config.LOG_LEVEL == "INFO"
        assert config.RETRY_COUNT == 3
        assert config.RETRY_DELAY == 1.0

    def test_custom_values_from_env(self, clean_env):
        """環境変数からの値の読み込み"""
        os.environ["GATHER_APP_NAME"] = "CustomGather"
        os.environ["GATHER_LOG_LEVEL"] = "DEBUG"
        config = AppConfig()
        assert config.GATHER_APP_NAME == "CustomGather"
        assert config.LOG_LEVEL == "DEBUG"

    def test_invalid_log_level(self, clean_env):
        """不正なLOG_LEVELの検証"""
        os.environ["GATHER_LOG_LEVEL"] = "INVALID"
        with pytest.raises(ConfigValidationError, match="LOG_LEVELは"):
            AppConfig().validate()

    def test_empty_app_name(self, clean_env):
        """空のGATHER_APP_NAMEの検証"""
        os.environ["GATHER_APP_NAME"] = ""
        with pytest.raises(
            ConfigValidationError, match="GATHER_APP_NAMEは空であってはいけません"
        ):
            AppConfig().validate()


class TestConfig:
    def test_integration(self, clean_env):
        """統合テスト"""
        config = Config()
        assert isinstance(config.script, ScriptConfig)
        assert isinstance(config.network, NetworkConfig)
        assert isinstance(config.app, AppConfig)

    def test_validation_error_propagation(self, clean_env):
        """バリデーショ��エラーの伝播テスト"""
        os.environ["GATHER_SCRIPT_MAX_SIZE"] = "-1"
        with pytest.raises(
            ConfigValidationError, match="MAX_SIZE_BYTESは正の値である必要があります"
        ):
            Config()

    def test_from_env_file(self, tmp_path):
        """環境変数ファイルからの読み込みテスト"""
        env_file = tmp_path / ".env"
        env_file.write_text(
            """
GATHER_APP_NAME=TestGather
GATHER_LOG_LEVEL=DEBUG
""".strip()
        )

        config = Config.from_env(str(env_file))
        assert config.app.GATHER_APP_NAME == "TestGather"
        assert config.app.LOG_LEVEL == "DEBUG"
