#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特定機能テスト用スクリプト
main.pyの一部を抜粋して特定機能のみをテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.environment import EnvironmentUtils
from src.utils.logging_config import LoggingConfig
from src.modules.browser import Browser
from src.modules.login import Login
from src.modules.csv_downloader import CsvDownloader

def test_carousel_survey_only():
    """配信タグデータのみをテスト"""
    print("🎠 配信タグデータのみテスト")
    
    # 環境設定
    EnvironmentUtils.load_env()
    logging_config = LoggingConfig()
    logging_config.setup_logging()
    
    # ブラウザ初期化
    browser = Browser()
    
    try:
        # ログイン
        login = Login(browser)
        if not login.execute():
            print("❌ ログイン失敗")
            return False
        
        # 配信タグデータのみ実行
        csv_downloader = CsvDownloader(browser)
        if csv_downloader.download_carousel_survey():
            print("✅ 配信タグデータ取得成功")
            return True
        else:
            print("❌ 配信タグデータ取得失敗")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False
    finally:
        browser.quit()

def test_ag_tag_only():
    """AGタグデータのみをテスト"""
    print("🏷️ AGタグデータのみテスト")
    
    # 環境設定
    EnvironmentUtils.load_env()
    logging_config = LoggingConfig()
    logging_config.setup_logging()
    
    # ブラウザ初期化
    browser = Browser()
    
    try:
        # ログイン
        login = Login(browser)
        if not login.execute():
            print("❌ ログイン失敗")
            return False
        
        # AGタグデータのみ実行
        csv_downloader = CsvDownloader(browser)
        if csv_downloader.download_ag_tag_data():
            print("✅ AGタグデータ取得成功")
            return True
        else:
            print("❌ AGタグデータ取得失敗")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False
    finally:
        browser.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='特定機能テスト')
    parser.add_argument('--carousel', action='store_true', help='配信タグデータのみテスト')
    parser.add_argument('--ag-tag', action='store_true', help='AGタグデータのみテスト')
    
    args = parser.parse_args()
    
    if args.carousel:
        test_carousel_survey_only()
    elif args.ag_tag:
        test_ag_tag_only()
    else:
        print("使用方法:")
        print("python test_specific.py --carousel  # 配信タグデータのみ")
        print("python test_specific.py --ag-tag    # AGタグデータのみ")
