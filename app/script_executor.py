import asyncio
import logging

from app.chromium_debug_protocol_executor import ChromiumDebugProtocolExecutor
from app.exceptions import JavaScriptExecutionError

logger = logging.getLogger(__name__)


class ScriptExecutor:
    def __init__(self, window, executor=None):
        self.window = window
        self.executor = executor or ChromiumDebugProtocolExecutor()

    async def execute_scripts(self, script_paths):
        logger.info(f"{len(script_paths)}個のスクリプトの実行を開始します")
        tasks = [self.execute_script(script_path) for script_path in script_paths]
        await asyncio.gather(*tasks)
        logger.info("すべてのスクリプトの実行が完了しました")

    async def execute_script(self, script_path):
        logger.debug(f"スクリプト {script_path} の実行を開始します")
        try:
            result = await self.executor.execute_script(self.window, script_path)
            logger.info(f"スクリプト {script_path} の実行が成功しました")
            logger.debug(f"スクリプト {script_path} の実行結果: {result}")
        except Exception as e:
            logger.error(
                f"スクリプト {script_path} の実行中にエラーが発生しました: {e}"
            )
            raise JavaScriptExecutionError(
                f"スクリプト {script_path} の実行中にエラーが発生しました: {e}"
            )
