import argparse
import subprocess


def open_gather(gather_path):
    try:
        subprocess.run(["open", "-a", gather_path], check=True)
        print(f"Gatherを開きました: {gather_path}")
    except subprocess.CalledProcessError:
        print(f"エラー: Gatherを開けませんでした: {gather_path}")


def main():
    parser = argparse.ArgumentParser(
        description="複数のファイルパスを処理し、Gatherを開くツール"
    )
    parser.add_argument(
        "-p",
        "--path",
        default="Gather",
        help="Gatherアプリケーションのパスまたは名前（デフォルト: Gather）",
    )
    parser.add_argument(
        "-s", "--scripts", nargs="+", help="実行するスクリプトのパス", required=False
    )

    args = parser.parse_args()

    open_gather(args.path)

    if args.scripts:
        for script_path in args.scripts:
            print(f"実行中のスクリプト: {script_path}")


if __name__ == "__main__":
    main()
