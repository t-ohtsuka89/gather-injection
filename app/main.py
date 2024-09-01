import argparse
import asyncio
import logging

from app.config import Config
from app.exceptions import GatherInjectionError
from app.gather_controller import GatherController

# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Gatherを開くツール")
    parser.add_argument(
        "-g",
        "--gather-path",
        default=Config.GATHER_APP_NAME,
        help=f"Gatherアプリケーションのパスまたは名前（デフォルト: {Config.GATHER_APP_NAME}）",
    )
    parser.add_argument(
        "-s", "--scripts", nargs="+", help="実行するスクリプトのパス", required=False
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=Config.get_free_port(),
        help="ポート番号（デフォルト: 自動取得）",
    )
    return parser.parse_args()


async def async_main():
    args = parse_arguments()
    logger.info(f"Gatherパス: {args.gather_path}, ポート: {args.port}")
    controller = GatherController(args.gather_path, args.port)
    try:
        logger.info("Gatherコントローラーを開始します")
        await controller.start()
        if args.scripts:
            logger.info(f"スクリプトを実行します: {args.scripts}")
            await controller.execute_scripts(args.scripts)
        else:
            logger.info(
                "スクリプトが指定されていません。ウィンドウの準備が完了しました。"
            )
    except GatherInjectionError as e:
        logger.error(f"エラーが発生しました: {e}")
    finally:
        logger.info("Gatherコントローラーを停止します")
        await controller.stop()


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
