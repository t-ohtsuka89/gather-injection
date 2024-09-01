import asyncio
import logging
from abc import ABC, abstractmethod

from app.chromium_debug_protocol_executor import ChromiumDebugProtocolExecutor
from app.exceptions import JavaScriptExecutionError

logger = logging.getLogger(__name__)


class ScriptExecutorInterface(ABC):
    @abstractmethod
    async def execute_script(self, window, script_path):
        pass


class ScriptExecutor:
    def __init__(self, window, executor: ScriptExecutorInterface = None):
        self.window = window
        self.executor = executor or ChromiumDebugProtocolExecutor()

    async def execute_scripts(self, script_paths):
        tasks = [self.execute_script(script_path) for script_path in script_paths]
        await asyncio.gather(*tasks)

    async def execute_script(self, script_path):
        try:
            result = await self.executor.execute_script(self.window, script_path)
            logger.info(f"スクリプト {script_path} の実行結果: {result}")
        except Exception as e:
            raise JavaScriptExecutionError(
                f"スクリプト {script_path} の実行中にエラーが発生しました: {e}"
            )
