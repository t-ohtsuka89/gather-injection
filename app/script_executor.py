import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.chromium_debug_protocol_executor import ChromiumDebugProtocolExecutor
from app.config import Config
from app.exceptions import JavaScriptExecutionError, ScriptValidationError

logger = logging.getLogger(__name__)


class ScriptExecutor:
    def __init__(
        self,
        window: Dict[str, Any],
        executor: Optional[ChromiumDebugProtocolExecutor] = None,
        config: Optional[Config] = None,
    ):
        self.window = window
        self.executor = executor or ChromiumDebugProtocolExecutor()
        self.config = config or Config()
        self._script_cache: Dict[str, str] = {}

    async def execute_scripts(self, script_paths: List[str]) -> None:
        logger.info(f"{len(script_paths)}個のスクリプトの実行を開始します")

        # スクリプトの事前検証
        await self._validate_scripts(script_paths)

        # 並列実行とエラーハンドリング
        tasks = [self.execute_script(script_path) for script_path in script_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # エラーチェックと結果の集約
        errors = []
        for script_path, result in zip(script_paths, results):
            if isinstance(result, Exception):
                errors.append((script_path, result))

        if errors:
            error_messages = "\n".join([f"- {path}: {err}" for path, err in errors])
            raise JavaScriptExecutionError(
                f"スクリプト実行中にエラーが発生:\n{error_messages}"
            )

        logger.info("すべてのスクリプトの実行が完了しました")

    async def execute_script(self, script_path: str) -> Any:
        logger.debug(f"スクリプト {script_path} の実行を開始します")
        try:
            # スクリプトの読み込み（キャッ��ュを使用）
            script_content = await self._get_script_content(script_path)

            # タイムアウト付きでスクリプトを実行
            try:
                async with asyncio.timeout(self.config.script.EXECUTION_TIMEOUT):
                    result = await self.executor.execute_script(
                        self.window, script_content
                    )
            except asyncio.TimeoutError:
                raise JavaScriptExecutionError(
                    f"スクリプト {script_path} の実行がタイムアウトしました"
                )

            logger.info(f"スクリプト {script_path} の実行が成功しました")
            logger.debug(f"スクリプト {script_path} の実行結果: {result}")
            return result

        except Exception as e:
            logger.error(
                f"スクリプト {script_path} の実行中にエラーが発生しました: {e}"
            )
            raise JavaScriptExecutionError(
                f"スクリプト {script_path} の実行中にエラーが発生しました: {e}"
            ) from e

    async def _validate_scripts(self, script_paths: List[str]) -> None:
        """スクリプトの事前検証を行います"""
        for script_path in script_paths:
            path = Path(script_path)
            if not path.exists():
                raise ScriptValidationError(f"スクリプトが存在しません: {script_path}")
            if path.suffix[1:] not in self.config.script.ALLOWED_EXTENSIONS:
                raise ScriptValidationError(
                    f"不正なファイル形式です: {script_path}、許可された拡張子: {self.config.script.ALLOWED_EXTENSIONS}"
                )

            # ファイルサイズチェック
            if path.stat().st_size > self.config.script.MAX_SIZE_BYTES:
                raise ScriptValidationError(
                    f"スクリプトサイズが大きすぎます: {script_path}、"
                    f"最大サイズ: {self.config.script.MAX_SIZE_BYTES / 1024:.1f}KB"
                )

    async def _get_script_content(self, script_path: str) -> str:
        """スクリプトの内容を取得（キャッシュ付き）"""
        if script_path not in self._script_cache:
            try:
                async with asyncio.Lock():
                    with open(script_path, "r", encoding="utf-8") as f:
                        self._script_cache[script_path] = f.read()
            except Exception as e:
                raise ScriptValidationError(f"スクリプトの読み込みに失敗: {e}")

        return self._script_cache[script_path]
