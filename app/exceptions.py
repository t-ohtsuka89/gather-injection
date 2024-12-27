class GatherInjectionError(Exception):
    """基本的な例外クラス"""


class WindowNotFoundError(GatherInjectionError):
    """ウィンドウが見つからない場合の例外"""


class GameObjectNotFoundError(GatherInjectionError):
    """ゲームオブジェクトが見つからない場合の例外"""


class JavaScriptExecutionError(GatherInjectionError):
    """JavaScript実行時のエラー"""


class ScriptValidationError(GatherInjectionError):
    """スクリプトの検証時のエラー"""

    def __init__(self, message: str, script_path: str = None):
        super().__init__(message)
        self.script_path = script_path
