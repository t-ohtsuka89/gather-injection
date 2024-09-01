import asyncio
import logging
import sys
from typing import Callable

from app.config import Config
from app.exceptions import GatherInjectionError
from app.utils import connect_to_port

logger = logging.getLogger(__name__)


class GatherLauncher:
    def __init__(self, gather_path: str, port: int):
        self.gather_path = gather_path
        self.port = port

    async def launch(self):
        try:
            logger.info(f"Gatherの起動を開始します: {self.gather_path}")
            await self._open_gather()
            await self._wait_for_debug_port()
            logger.info("Gatherの起動が完了しました")
        except Exception as e:
            logger.error(f"Gatherの起動中にエラーが発生しました: {e}")
            raise GatherInjectionError(
                f"Gatherの起動中にエラーが発生しました: {e}"
            ) from e

    async def _wait_for_debug_port(self):
        logger.info(f"デバッグポート {self.port} の待機を開始します")
        if not await connect_to_port(
            self.port,
            Config.MAX_ATTEMPTS_DEBUG_PORT,
            Config.DEBUG_PORT_DELAY,
        ):
            logger.error(f"デバッグポート {self.port} が利用可能になりませんでした")
            raise GatherInjectionError(
                f"デバッグポート {self.port} が利用可能になりませんでした。"
            )
        logger.info(f"デバッグポート {self.port} が利用可能になりました")

    async def _open_gather(self):
        command = self._get_platform_specific_command()
        logger.info(f"実行するコマンド: {command}")

        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise GatherInjectionError(f"Gatherを開けませんでした: {stderr.decode()}")

        logger.info(f"Gatherを開きました: {self.gather_path} (ポート: {self.port})")

    def _get_platform_specific_command(self) -> str:
        commands: dict[str, Callable[[], str]] = {
            "darwin": lambda: f"open -a '{self.gather_path}' --args --remote-debugging-port={self.port}",
            "win32": lambda: f'start "" "{self.gather_path}" --remote-debugging-port={self.port}',
        }
        command = commands.get(sys.platform)
        if not command:
            raise GatherInjectionError(
                f"プラットフォーム '{sys.platform}' はサポートされていません。"
            )
        return command()
