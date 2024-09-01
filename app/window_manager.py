import asyncio
import json
import logging

import aiohttp
import websockets

from app.config import Config
from app.exceptions import GameObjectNotFoundError, WindowNotFoundError
from app.utils import connect_to_port

logger = logging.getLogger(__name__)


class WindowManager:
    def __init__(self, port):
        self.port = port
        self.session = None
        self.window = None

    async def initialize(self):
        await self._wait_for_debug_port()
        await self._find_and_connect_window()
        await self._wait_for_game_object()
        return self.window

    async def _find_and_connect_window(self):
        async with aiohttp.ClientSession() as self.session:
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < Config.WINDOW_TIMEOUT:
                try:
                    windows = await self._get_electron_windows()
                    self.window = next(
                        (
                            w
                            for w in windows
                            if w.get("url", "").startswith(Config.TARGET_URL_PREFIX)
                        ),
                        None,
                    )
                    if self.window:
                        return
                except Exception as e:
                    logger.error(f"ウィンドウ検索エラー: {e}")
                await asyncio.sleep(1)
            raise WindowNotFoundError("目的のウィンドウが見つかりません")

    async def _wait_for_debug_port(self):
        if not await connect_to_port(
            self.port, Config.MAX_ATTEMPTS_DEBUG_PORT, Config.DEBUG_PORT_DELAY
        ):
            raise WindowNotFoundError(
                f"デバッグポート {self.port} が利用可能になりませんでした。"
            )

    async def _wait_for_game_object(self):
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < Config.GAME_OBJECT_TIMEOUT:
            if await self._check_game_object():
                return
            await asyncio.sleep(5)
        raise GameObjectNotFoundError("ゲームオブジェクトが利用可能になりませんでした")

    async def get_window(self):
        if not self.window:
            raise WindowNotFoundError("ウィンドウが初期化されていません")
        return self.window

    async def _get_electron_windows(self):
        url = f"http://localhost:{self.port}/json"
        async with self.session.get(url) as response:
            windows = await response.json()

        logger.info(f"取得したウィンドウ情報: {windows}")

        for window in windows:
            websocket_url = window["webSocketDebuggerUrl"]
            try:
                window["websocket"] = await websockets.connect(websocket_url)
                logger.info(f"WebSocket接続が確立されました: {websocket_url}")
            except Exception as e:
                logger.error(f"WebSocket接続の確立に失敗しました: {e}")

        return windows

    async def _eval_js(self, expression):
        if not self.window or "websocket" not in self.window:
            raise ValueError("WebSocket接続が初期化されていません")

        websocket = self.window["websocket"]
        message_id = 1

        try:
            message = {
                "id": message_id,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": expression,
                    "returnByValue": True,
                    "awaitPromise": True,
                },
            }
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            result = json.loads(response)

            return self._parse_eval_result(result)
        except Exception as e:
            logger.error(f"JavaScript評価中に例外が発生しました: {e}")
            return None

    def _parse_eval_result(self, result):
        if "result" in result:
            if "result" in result["result"]:
                value = result["result"]["result"].get("value")
                logger.info(f"JavaScript実行結果: {value}")
                return value
            elif "exceptionDetails" in result["result"]:
                error_message = (
                    result["result"]["exceptionDetails"]
                    .get("exception", {})
                    .get("description", "不明なエラー")
                )
                logger.error(f"JavaScript実行エラー: {error_message}")
        elif "error" in result:
            logger.error(f"JavaScript実行エラー: {result['error']}")
        else:
            logger.error(f"予期しない応答: {result}")
        return None

    async def _reconnect_websocket(self):
        try:
            if "websocket" in self.window:
                await self.window["websocket"].close()
            websocket_url = self.window["webSocketDebuggerUrl"]
            logger.info(f"WebSocket再接続を試みます: {websocket_url}")
            self.window["websocket"] = await websockets.connect(websocket_url)
            logger.info("WebSocket接続が再確立されました。")
        except Exception as e:
            logger.error(f"WebSocket再接続中にエラーが発生しました: {e}")

    async def _ensure_websocket_connection(self):
        if self.window["websocket"].state != websockets.protocol.State.OPEN:
            logger.info("WebSocket接続が開いていません。再接続を試みます。")
            await self._reconnect_websocket()

    async def _check_game_object(self):
        try:
            await self._ensure_websocket_connection()
            result = await self._eval_js(Config.GAME_OBJECT_CHECK_SCRIPT)
            return result.get("status") == "success"
        except Exception as e:
            logger.error(f"ゲームオブジェクト検出中にエラーが発生しました: {e}")
            return False

    async def get_initialized_window(self):
        if not self.window:
            await self.initialize()
        return self.window

    async def close(self):
        if self.window and "websocket" in self.window:
            await self.window["websocket"].close()
        if self.session:
            await self.session.close()
        logger.info("WindowManager: 全接続を閉じました")
