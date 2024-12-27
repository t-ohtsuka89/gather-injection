import logging
import asyncio
from typing import List, Optional
from functools import wraps

from app.exceptions import GatherInjectionError
from app.gather_launcher import GatherLauncher
from app.script_executor import ScriptExecutor
from app.window_manager import WindowManager

logger = logging.getLogger(__name__)


def with_retry(retries: int = 3, delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"試行 {attempt + 1}/{retries} 失敗: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception

        return wrapper

    return decorator


class GatherController:
    def __init__(self, gather_path: str, port: int):
        self.launcher = GatherLauncher(gather_path, port)
        self.window_manager = WindowManager(port)
        self.script_executor: Optional[ScriptExecutor] = None
        logger.info(f"GatherController初期化: パス={gather_path}, ポート={port}")

    @with_retry(retries=3)
    async def start(self) -> None:
        try:
            await self.launcher.launch()
            window = await self.window_manager.initialize()
            self.script_executor = ScriptExecutor(window)
            logger.info("Gather起動成功")
        except Exception as e:
            logger.error(f"Gather起動エラー: {e}", exc_info=True)
            await self.stop()
            raise GatherInjectionError(f"Gather起動エラー: {e}") from e

    async def execute_scripts(self, script_paths: List[str]) -> None:
        if not self.script_executor:
            raise GatherInjectionError("ScriptExecutor未初期化")

        try:
            # スクリプトの並列実行
            tasks = [self.script_executor.execute_script(path) for path in script_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # エラーチェック
            for path, result in zip(script_paths, results):
                if isinstance(result, Exception):
                    logger.error(f"スクリプト実行エラー {path}: {result}")
                    raise GatherInjectionError(f"スクリプト実行エラー {path}: {result}")

            logger.info(f"{len(script_paths)}個のスクリプトを正常に実行しました")
        except Exception as e:
            logger.error(f"スクリプト実行中にエラーが発生: {e}", exc_info=True)
            raise GatherInjectionError(f"スクリプト実行エラー: {e}") from e

    async def stop(self) -> None:
        try:
            if self.window_manager:
                await self.window_manager.close()
            self.script_executor = None
            logger.info("Gatherリモートデバッグ接続終了")
        except Exception as e:
            logger.error(f"停止処理中にエラーが発生: {e}", exc_info=True)
            raise GatherInjectionError(f"停止処理エラー: {e}") from e
