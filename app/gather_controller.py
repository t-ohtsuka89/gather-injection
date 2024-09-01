import logging

from app.exceptions import GatherInjectionError
from app.gather_launcher import GatherLauncher
from app.script_executor import ScriptExecutor
from app.window_manager import WindowManager

logger = logging.getLogger(__name__)


class GatherController:
    def __init__(self, gather_path, port):
        self.launcher = GatherLauncher(gather_path, port)
        self.window_manager = WindowManager(port)
        self.script_executor = None
        logger.info(f"GatherController初期化: パス={gather_path}, ポート={port}")

    async def start(self):
        try:
            await self.launcher.launch()
            window = await self.window_manager.initialize()
            self.script_executor = ScriptExecutor(window)
            logger.info("Gather起動成功")
        except Exception as e:
            logger.error(f"Gather起動エラー: {e}", exc_info=True)
            await self.stop()
            raise GatherInjectionError(f"Gather起動エラー: {e}") from e

    async def execute_scripts(self, script_paths):
        if not self.script_executor:
            raise GatherInjectionError("ScriptExecutor未初期化")
        await self.script_executor.execute_scripts(script_paths)

    async def stop(self):
        if self.window_manager:
            await self.window_manager.close()
        self.script_executor = None
        logger.info("Gatherリモートデバッグ接続終了")
