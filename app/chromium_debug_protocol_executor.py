import json
import logging

logger = logging.getLogger(__name__)


class ChromiumDebugProtocolExecutor:
    async def execute_script(self, window, script_content: str):
        """
        JavaScriptコードを実行します。

        Args:
            window: デバッグウィンドウの情報
            script_content: 実行するJavaScriptコードの内容

        Returns:
            実行結果

        Raises:
            RuntimeError: JavaScriptの実行中にエラーが発生した場合
        """
        try:
            return await self._eval_js(window, script_content)
        except Exception as e:
            logger.error(f"JavaScriptの実行中にエラーが発生: {e}")
            raise RuntimeError(f"JavaScriptの実行中にエラーが発生しました: {e}")

    async def _eval_js(self, window, expression):
        if "websocket" not in window:
            raise ValueError("WebSocket接続が初期化されていません")

        websocket = window["websocket"]
        data = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        }

        try:
            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            response_data = json.loads(response)

            if "result" in response_data:
                return self._parse_result(response_data["result"]["result"])
            elif "error" in response_data:
                error_message = response_data["error"].get("message", "不明なエラー")
                logger.error(f"JavaScript実行エラー: {error_message}")
                raise RuntimeError(
                    f"JavaScriptの実行中にエラーが発生しました: {error_message}"
                )
            else:
                raise ValueError("予期しないレスポンス形式です")
        except Exception as e:
            logger.exception(f"JavaScript実行中に例外が発生しました: {e}")
            raise

    @staticmethod
    def _parse_result(result):
        if "value" in result:
            return result["value"]
        if result.get("type") == "undefined":
            return None
        if result.get("type") == "object" and "objectId" in result:
            logger.info(f"オブジェクトID: {result['objectId']}")
            return None
        logger.warning(f"予期しない結果形式: {result}")
        return None
