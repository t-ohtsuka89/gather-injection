import argparse
import subprocess
import socket


def open_gather(gather_path, port):
    try:
        subprocess.run(["open", "-a", gather_path], check=True)
    except subprocess.CalledProcessError:
        print(f"エラー: Gatherを開けませんでした: {gather_path}")
        exit(1)


def get_free_port():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]
    except Exception as e:
        print(f"エラー: ポートの取得に失敗しました: {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="複数のファイルパスを処理し、Gatherを開くツール"
    )
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

    if args.scripts:
        for script_path in args.scripts:
            print(f"実行中のスクリプト: {script_path}")


if __name__ == "__main__":
    main()
