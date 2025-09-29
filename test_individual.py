#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別機能テスト用スクリプト
各機能を独立してテストできます
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

def setup_environment():
    """環境設定の初期化"""
    try:
        # 環境変数のロード
        EnvironmentUtils.load_env()
        
        # ログ設定
        logging_config = LoggingConfig()
        logging_config.setup_logging()
        
        print("✅ 環境設定完了")
        return True
    except Exception as e:
        print(f"❌ 環境設定エラー: {str(e)}")
        return False

def test_login():
    """ログイン機能のテスト"""
    print("\n🔐 ログインテスト開始")
    try:
        browser = Browser()
        login = Login(browser)
        
        if login.execute():
            print("✅ ログイン成功")
            return browser
        else:
            print("❌ ログイン失敗")
            return None
    except Exception as e:
        print(f"❌ ログインテストエラー: {str(e)}")
        return None

def test_friend_data(browser):
    """友達リストデータのテスト"""
    print("\n📊 友達リストデータテスト開始")
    try:
        csv_downloader = CsvDownloader(browser)
        
        if csv_downloader.execute():
            print("✅ 友達リストデータ取得成功")
            return True
        else:
            print("❌ 友達リストデータ取得失敗")
            return False
    except Exception as e:
        print(f"❌ 友達リストデータテストエラー: {str(e)}")
        return False

def test_questionnaire_data(browser):
    """アンケートデータのテスト"""
    print("\n📋 アンケートデータテスト開始")
    try:
        csv_downloader = CsvDownloader(browser)
        
        if csv_downloader.download_questionnaire():
            print("✅ アンケートデータ取得成功")
            return True
        else:
            print("❌ アンケートデータ取得失敗")
            return False
    except Exception as e:
        print(f"❌ アンケートデータテストエラー: {str(e)}")
        return False

def test_carousel_survey_data(browser):
    """配信タグデータのテスト"""
    print("\n🎠 配信タグデータテスト開始")
    try:
        csv_downloader = CsvDownloader(browser)
        
        if csv_downloader.download_carousel_survey():
            print("✅ 配信タグデータ取得成功")
            return True
        else:
            print("❌ 配信タグデータ取得失敗")
            return False
    except Exception as e:
        print(f"❌ 配信タグデータテストエラー: {str(e)}")
        return False

def test_ag_tag_data(browser):
    """AGタグデータのテスト"""
    print("\n🏷️ AGタグデータテスト開始")
    try:
        csv_downloader = CsvDownloader(browser)
        
        if csv_downloader.download_ag_tag_data():
            print("✅ AGタグデータ取得成功")
            return True
        else:
            print("❌ AGタグデータ取得失敗")
            return False
    except Exception as e:
        print(f"❌ AGタグデータテストエラー: {str(e)}")
        return False

def main():
    """メイン処理"""
    print("🧪 個別機能テスト開始")
    
    # 環境設定
    if not setup_environment():
        return
    
    # ログイン
    browser = test_login()
    if not browser:
        return
    
    try:
        # テスト対象の選択
        print("\n📋 テスト対象を選択してください:")
        print("1. 友達リストデータ")
        print("2. アンケートデータ")
        print("3. 配信タグデータ（新機能）")
        print("4. AGタグデータ（新機能）")
        print("5. 全て実行")
        
        choice = input("選択 (1-5): ").strip()
        
        if choice == "1":
            test_friend_data(browser)
        elif choice == "2":
            test_questionnaire_data(browser)
        elif choice == "3":
            test_carousel_survey_data(browser)
        elif choice == "4":
            test_ag_tag_data(browser)
        elif choice == "5":
            print("\n🔄 全機能テスト開始")
            test_friend_data(browser)
            test_questionnaire_data(browser)
            test_carousel_survey_data(browser)
            test_ag_tag_data(browser)
        else:
            print("❌ 無効な選択です")
            return
        
        print("\n✨ テスト完了")
        
    except KeyboardInterrupt:
        print("\n⏹️ テスト中断")
    except Exception as e:
        print(f"\n❌ 予期せぬエラー: {str(e)}")
    finally:
        # ブラウザ終了
        try:
            browser.quit()
            print("🔚 ブラウザ終了")
        except:
            pass

if __name__ == "__main__":
    main()
