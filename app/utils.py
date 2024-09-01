import asyncio
import socket
import logging

logger = logging.getLogger(__name__)


async def connect_to_port(port, max_attempts=10, delay=1) -> bool:
    for attempt in range(max_attempts):
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: socket.create_connection(("localhost", port), timeout=5)
            )
            logger.info(f"ポート {port} に接続しました。")
            return True
        except (socket.timeout, ConnectionRefusedError):
            logger.debug(f"接続試行 {attempt + 1}/{max_attempts}...")
            await asyncio.sleep(delay)
    logger.error(f"エラー: ポート {port} に接続できませんでした。")
    return False
