import argparse


def main():
    parser = argparse.ArgumentParser(description="複数のファイルパスを処理するツール")
    parser.add_argument(
        "-s", "--scripts", nargs="+", help="実行するスクリプトのパス", required=False
    )

    args = parser.parse_args()

    for script_path in args.scripts:
        print(f"実行中のスクリプト: {script_path}")


if __name__ == "__main__":
    main()
