import time
import os
import logging
import argparse
from pathlib import Path
import sys

# 実行ファイルのパスを取得
if getattr(sys, 'frozen', False):
    # exe実行時のパス
    application_path = Path(sys._MEIPASS)
else:
    # 通常実行時のパス
    application_path = Path(__file__).parent.parent

# パスを追加
sys.path.append(str(application_path))

# 相対インポートを絶対インポートに変更
from src.utils.environment import EnvironmentUtils as env
from src.utils.logging_config import get_logger
from src.modules.browser import Browser
from src.modules.login import Login
from src.modules.spreadsheet import Spreadsheet
from src.modules.csv_downloader import CsvDownloader

# ロガーの設定
logger = get_logger(__name__)

def setup_configurations():
    """設定ファイルと機密情報をロードしてデータを取得します。"""
    try:
        # 環境変数のロード
        env.load_env()
        
        # 環境変数の検証
        required_vars = ['ADMIN_URL', 'LOGIN_ID', 'LOGIN_PASSWORD']
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"環境変数 {var} が設定されていません")
            logger.info(f"{var} の設定を確認しました")
        
        # ブラウザ設定の確認
        headless = env.get_config_value("BROWSER", "headless", default=True)
        logger.info(f"ブラウザのヘッドレスモード設定: {headless}")
        
    except Exception as e:
        logger.error(f"設定のロードに失敗: {str(e)}")
        raise

def main():
    """メイン処理"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='L-step データダウンロード自動化システム')
    parser.add_argument('--carousel-only', action='store_true', help='配信タグデータのみ実行')
    parser.add_argument('--ag-tag-only', action='store_true', help='AGタグデータのみ実行')
    parser.add_argument('--friend-only', action='store_true', help='友達リストデータのみ実行')
    parser.add_argument('--questionnaire-only', action='store_true', help='アンケートデータのみ実行')
    
    args = parser.parse_args()
    
    try:
        logger.info("プログラムを開始します")
        
        # 設定のロード
        setup_configurations()
        
        # ブラウザの初期化
        browser = Browser()
        browser.setup()
        logger.info("ブラウザを初期化しました")

        # ログインの実行
        login = Login(browser)
        if not login.execute():
            logger.error("ログインに失敗しました")
            print("ログイン失敗")
            return

        logger.info("ログインに成功しました")
        print("[SUCCESS] ログイン成功")

        # CSVダウンローダーの初期化
        csv_downloader = CsvDownloader(browser)

        # 個別実行の判定
        if args.carousel_only:
            # 配信タグデータのみ実行
            logger.info("[DATA] 配信タグデータの処理を開始します")
            if not csv_downloader.download_carousel_survey():
                logger.error("配信タグデータの処理に失敗しました")
                print("[ERROR] 配信タグデータの処理失敗")
                return
            print("[SUCCESS] 配信タグデータの処理成功")
            
        elif args.ag_tag_only:
            # AGタグデータのみ実行
            logger.info("[DATA] AGタグデータの処理を開始します")
            if not csv_downloader.download_ag_tag_data():
                logger.error("AGタグデータの処理に失敗しました")
                print("[ERROR] AGタグデータの処理失敗")
                return
            print("[SUCCESS] AGタグデータの処理成功")
            
        elif args.friend_only:
            # 友達リストデータのみ実行
            logger.info("[DATA] 会員データの処理を開始します")
            if not csv_downloader.execute():
                logger.error("会員データの処理に失敗しました")
                print("[ERROR] 会員データの処理失敗")
                return
            print("[SUCCESS] 会員データの処理成功")
            
        elif args.questionnaire_only:
            # アンケートデータのみ実行
            logger.info("[DATA] アンケートデータの処理を開始します")
            if not csv_downloader.download_questionnaire():
                logger.error("アンケートデータの処理に失敗しました")
                print("[ERROR] アンケートデータの処理失敗")
                return
            print("[SUCCESS] アンケートデータの処理成功")
            
        else:
            # 全機能実行（デフォルト）
            # 1. アンケートデータのダウンロードとスプレッドシート更新
            logger.info("[DATA] アンケートデータの処理を開始します")
            if not csv_downloader.download_questionnaire():
                logger.error("アンケートデータの処理に失敗しました")
                print("[ERROR] アンケートデータの処理失敗")
                return
            print("[SUCCESS] アンケートデータの処理成功")

            # 2. 会員データのダウンロードとスプレッドシート更新
            logger.info("[DATA] 会員データの処理を開始します")
            if not csv_downloader.execute():
                logger.error("会員データの処理に失敗しました")
                print("[ERROR] 会員データの処理失敗")
                return
            print("[SUCCESS] 会員データの処理成功")

            # 3. 配信タグデータのダウンロードとスプレッドシート更新
            logger.info("[DATA] 配信タグデータの処理を開始します")
            if not csv_downloader.download_carousel_survey():
                logger.error("配信タグデータの処理に失敗しました")
                print("[ERROR] 配信タグデータの処理失敗")
                return
            print("[SUCCESS] 配信タグデータの処理成功")

            # 4. AGタグデータのダウンロードとスプレッドシート更新
            logger.info("[DATA] AGタグデータの処理を開始します")
            if not csv_downloader.download_ag_tag_data():
                logger.error("AGタグデータの処理に失敗しました")
                print("[ERROR] AGタグデータの処理失敗")
                return
            print("[SUCCESS] AGタグデータの処理成功")

        logger.info("[COMPLETE] 全ての処理が完了しました")
        print("[COMPLETE] 処理完了")

    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {str(e)}")
        print(f"[ERROR] エラー: {str(e)}")
    finally:
        # ブラウザを終了
        if 'browser' in locals():
            browser.quit()
            logger.info("ブラウザを終了しました")
        
        # exe実行時は入力待ち
        if getattr(sys, 'frozen', False):
            input("Enterキーを押して終了してください...")

if __name__ == "__main__":
    main() 