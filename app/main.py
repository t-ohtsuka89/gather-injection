import argparse
import subprocess
import socket
import shlex
import asyncio
import aiohttp
import json
import websockets


async def wait_for_window_and_load(session, port, url_prefix, timeout=60):
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        windows = await get_electron_windows(session, port)
        for window in windows:
            if window.get("url", "").startswith(url_prefix):
                print(f"目的のウィンドウが見つかりました: {window['url']}")
                while True:
                    result = await eval_js(window, "document.readyState")
                    if result == "interactive" or result == "complete":
                        print(f"ウィンドウのDOMが読み込まれました (状態: {result})")
                        return window
                    await asyncio.sleep(0.5)
        await asyncio.sleep(1)
    raise TimeoutError(f"{timeout}秒以内に目的のウィンドウが見つかりませんでした")


def open_gather(gather_path, port):
    try:
        args = f"--remote-allow-origins=http://localhost:{port} --remote-debugging-port={port}"
        full_command = f"open -a '{gather_path}' --args {args}"
        subprocess.run(shlex.split(full_command), check=True)
        print(f"Gatherを開きました: {gather_path} (ポート: {port})")
    except subprocess.CalledProcessError as e:
        print(f"エラー: Gatherを開けませんでした: {gather_path}")
        print(f"エラーの詳細: {e}")
        exit(1)


async def connect_to_port(port, max_attempts=10, delay=1):
    for attempt in range(max_attempts):
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: socket.create_connection(("localhost", port), timeout=5)
            )
            print(f"ポート {port} に接続しました。")
            return True
        except (socket.timeout, ConnectionRefusedError):
            print(f"接続試行 {attempt + 1}/{max_attempts}...")
            await asyncio.sleep(delay)
    print(f"エラー: ポート {port} に接続できませんでした。")
    return False


def get_free_port():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]
    except Exception as e:
        print(f"エラー: ポートの取得に失敗しました: {e}")
        exit(1)


async def prepare_websocket(window):
    websocket_url = window["webSocketDebuggerUrl"]
    websocket = await websockets.connect(websocket_url)
    window["websocket"] = websocket
    return window


async def get_electron_windows(session, port):
    url = f"http://localhost:{port}/json"
    async with session.get(url) as response:
        windows = await response.json()

    # WebSocket接続を非同期で準備
    tasks = [prepare_websocket(window) for window in windows]
    windows = await asyncio.gather(*tasks)

    return windows


async def reconnect_websocket(window):
    try:
        if "websocket" in window:
            await window["websocket"].close()
        websocket_url = window["webSocketDebuggerUrl"]
        window["websocket"] = await websockets.connect(websocket_url)
        print("WebSocket接続を再確立しました。")
    except Exception as e:
        print(f"WebSocket再接続エラー: {e}")
        return None
    return window


async def eval_js(window, expression, max_retries=3):
    for attempt in range(max_retries):
        try:
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

            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            response_data = json.loads(response)

            if "result" in response_data:
                return response_data["result"]["result"].get("value")
            elif "error" in response_data:
                error_message = response_data["error"].get("message", "不明なエラー")
                if response_data["error"].get("code") == -32000:
                    print("実行コンテキストが破棄されました。再接続を試みます。")
                    window = await reconnect_websocket(window)
                    if window is None:
                        return None
                    continue
                else:
                    print(f"JavaScriptの実行中にエラーが発生しました: {error_message}")
                    return None
            else:
                print("予期しないレスポンス形式です。")
                return None

        except Exception as e:
            print(f"eval_js実行中に例外が発生しました: {e}")
            window = await reconnect_websocket(window)
            if window is None:
                return None

    print(f"{max_retries}回の試行後も失敗しました。")
    return None


async def load_and_execute_js(window, js_file_path):
    try:
        with open(js_file_path, "r") as file:
            js_code = file.read()
        result = await eval_js(window, js_code)
        print(f"JavaScriptの実行結果: {result}")
        return result
    except FileNotFoundError:
        print(f"エラー: JavaScriptファイルが見つかりません: {js_file_path}")
    except Exception as e:
        print(f"JavaScriptの実行中にエラーが発生しました: {e}")
    return None


async def wait_for_game_object(window, timeout=60):
    wait_script = """
    (function waitForGameObject() {
        return new Promise((resolve) => {
            const checkInterval = 1000;
            const maxWaitTime = %d;
            let elapsedTime = 0;

            const intervalId = setInterval(() => {
                if (typeof window.game !== 'undefined' && window.game.players !== undefined) {
                    clearInterval(intervalId);
                    resolve({ status: 'success', message: 'ゲームオブジェクトが利用可能になりました。' });
                } else {
                    elapsedTime += checkInterval;
                    if (elapsedTime >= maxWaitTime) {
                        clearInterval(intervalId);
                        resolve({ status: 'timeout', message: 'ゲームオブジェクトの待機がタイムアウトしました。' });
                    }
                }
            }, checkInterval);
        });
    })();
    """ % (timeout * 1000)  # Convert seconds to milliseconds

    result = await eval_js(window, wait_script)
    if result is None:
        return {
            "status": "error",
            "message": "ゲームオブジェクトの待機中にエラーが発生しました。",
        }
    return result


async def async_main(args):
    async with aiohttp.ClientSession() as session:
        if not await connect_to_port(args.port):
            print("Gatherへの接続に失敗しました。")
            return

        try:
            target_window = await wait_for_window_and_load(
                session, args.port, "https://app.gather.town"
            )
            print(f"ウィンドウのURL: {target_window['url']}")

            wait_result = await wait_for_game_object(target_window, timeout=120)
            if wait_result["status"] != "success":
                print(
                    f"ゲームオブジェクトが利用可能になりませんでした: {wait_result['message']}"
                )
                return

            if args.scripts:
                for js_file in args.scripts:
                    await load_and_execute_js(target_window, js_file)
            else:
                print(
                    "スクリプトが指定されていません。ウィンドウの準備が完了しました。"
                )

        except TimeoutError as e:
            print(f"タイムアウトエラー: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
        finally:
            if target_window and "websocket" in target_window:
                await target_window["websocket"].close()

    # ClientSessionは自動的にクローズされます


def main():
    parser = argparse.ArgumentParser(description="Gatherを開くツール")
    parser.add_argument(
        "-g",
        "--gather-path",
        default="Gather",
        help="Gatherアプリケーションのパスまたは名前（デフォルト: Gather）",
    )
    parser.add_argument(
        "-s", "--scripts", nargs="+", help="実行するスクリプトのパス", required=False
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=get_free_port(),
        help="ポート番号（デフォルト: 自動取得）",
    )
    args = parser.parse_args()

    open_gather(args.gather_path, args.port)

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
