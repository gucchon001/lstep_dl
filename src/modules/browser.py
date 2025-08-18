from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from pathlib import Path
import pandas as pd
import logging

# Seleniumとurllib3の全ログを無効化
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('WDM').setLevel(logging.ERROR)

from ..utils.environment import EnvironmentUtils as env
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class Browser:
    def __init__(self, settings_path='config/settings.ini', selectors_path='config/selectors.csv'):
        self.driver = None
        self.settings = env
        self.selectors = self._load_selectors(selectors_path)
        self.wait = None

    def _load_selectors(self, selectors_path):
        """セレクター設定の読み込み"""
        try:
            # ファイルの存在確認
            if not Path(selectors_path).exists():
                logger.error(f"セレクターファイルが見つかりません: {selectors_path}")
                return {}

            df = pd.read_csv(selectors_path)
            
            # 必要なカラムの確認
            required_columns = ['page', 'element', 'selector_type', 'selector_value']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"必要なカラムが不足しています: {missing_columns}")
                return {}

            selectors = {}
            for _, row in df.iterrows():
                if row['page'] not in selectors:
                    selectors[row['page']] = {}
                selectors[row['page']][row['element']] = {
                    'type': row['selector_type'],
                    'value': row['selector_value']
                }
            return selectors
            
        except Exception as e:
            logger.error(f"セレクター設定の読み込みに失敗: {str(e)}")
            logger.debug("詳細なエラー情報:", exc_info=True)
            return {}

    def _get_element(self, page, element, wait=30):
        """指定された要素を取得"""
        try:
            logger.info(f"🔍 _get_element開始: {page}.{element} (wait={wait}秒)")
            selector = self.selectors[page][element]
            logger.info(f"🔍 セレクタ取得: {selector}")
            by_type = getattr(By, selector['type'].upper())
            logger.info(f"🔍 WebDriverWait開始: {by_type}, {selector['value']}")
            element_found = WebDriverWait(self.driver, wait).until(
                EC.visibility_of_element_located((by_type, selector['value']))
            )
            logger.info(f"🔍 _get_element成功: {page}.{element}")
            return element_found
        except Exception as e:
            logger.error(f"要素の取得に失敗: {str(e)}")
            logger.error(f"要求されたセレクタ: {page}.{element}")
            try:
                logger.error(f"現在のURL: {self.driver.current_url}")
                logger.error(f"ページタイトル: {self.driver.title}")
            except:
                logger.error("現在のページ情報取得失敗")
            raise

    def findShadowElements(self, host_css: str, inner_css: str):
        """
        Shadow DOM 内の要素一覧を取得
        
        引数:
            host_css (str): Shadow ホスト要素の CSS セレクタ
            inner_css (str): Shadow Root 内部で検索する CSS セレクタ
        戻り値:
            list[selenium.webdriver.remote.webelement.WebElement]: 見つかった要素のリスト
        例外:
            例外発生時は詳細をログに出力して再送出
        """
        try:
            host_element = self.driver.find_element(By.CSS_SELECTOR, host_css)
            shadow_root = host_element.shadow_root
            return shadow_root.find_elements(By.CSS_SELECTOR, inner_css)
        except Exception as e:
            logger.error(f"Shadow DOM要素一覧の取得に失敗: host='{host_css}', inner='{inner_css}', error={str(e)}")
            raise

    def waitForShadowElementsPresent(self, host_css: str, inner_css: str, wait_seconds: int = 20):
        """
        Shadow DOM 内で指定セレクタの要素が出現するまで待機
        
        引数:
            host_css (str): Shadow ホスト要素の CSS セレクタ
            inner_css (str): Shadow Root 内部で検索する CSS セレクタ
            wait_seconds (int): 最大待機秒数
        戻り値:
            list[WebElement]: 見つかった要素一覧
        例外:
            Timeout 等発生時はログ出力後に再送出
        """
        try:
            WebDriverWait(self.driver, wait_seconds).until(
                lambda d: len(self.findShadowElements(host_css, inner_css)) > 0
            )
            return self.findShadowElements(host_css, inner_css)
        except Exception as e:
            logger.error(f"Shadow DOM待機に失敗: host='{host_css}', inner='{inner_css}', error={str(e)}")
            raise

    def clickShadowItemByText(self, host_css: str, inner_css: str, expected_substring: str, scroll_into_view: bool = True) -> bool:
        """
        Shadow DOM 内のテキスト一致要素の親LIをクリック
        
        引数:
            host_css (str): Shadow ホスト要素の CSS セレクタ
            inner_css (str): Shadow Root 内部で検索する CSS セレクタ（例: "div.itempool ul li span:nth-child(2)")
            expected_substring (str): 含まれていれば一致とみなす部分文字列
            scroll_into_view (bool): クリック前にスクロールするか
        戻り値:
            bool: クリック成功なら True
        """
        try:
            candidates = self.findShadowElements(host_css, inner_css)
            logger.info(f"🔍 Shadow内候補数: {len(candidates)} (inner='{inner_css}')")
            for span in candidates:
                try:
                    text_value = (span.text or "").strip()
                except Exception:
                    text_value = ""
                if expected_substring and expected_substring in text_value:
                    parent_li = span.find_element(By.XPATH, "./..")
                    if scroll_into_view:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent_li)
                    try:
                        parent_li.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", parent_li)
                    logger.info(f"✓ Shadow DOM内クリック成功: '{text_value}'")
                    return True
            logger.warning(f"⚠ Shadow DOM内クリック対象が見つかりません: 部分文字列='{expected_substring}'")
            return False
        except Exception as e:
            logger.error(f"Shadow DOM内クリックに失敗: host='{host_css}', inner='{inner_css}', text='{expected_substring}', error={str(e)}")
            return False

    def setup(self):
        """ChromeDriverのセットアップ"""
        try:
            options = webdriver.ChromeOptions()
            
            # 基本設定
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('start-maximized')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            
            # GPUエラー対策
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            
            # 直接bool型として扱う
            headless = self.settings.get_config_value('BROWSER', 'headless', default=False)
            
            if headless:
                options.add_argument('--headless=new')
                logger.info("ヘッドレスモードで実行します")
            else:
                logger.info("通常モードで実行します")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.maximize_window()
            
        except Exception as e:
            logger.error(f"ブラウザのセットアップに失敗: {str(e)}")
            self.driver = None  # 確実にNoneに設定
            raise

    def get_url(self):
        """現在のURLを取得"""
        return self.driver.current_url

    def access_site(self, url):
        """指定したURLにアクセス"""
        self.driver.get(url)

    def open_csv_download_page(self):
        """CSVダウンロードページを開く"""
        try:
            csv_url = self.settings.get_config_value('URL', 'csv_download_url')
            self.driver.get(csv_url)
            time.sleep(2)  # ページの読み込みを待機
            return True
        except Exception as e:
            return False

    def quit(self):
        """ブラウザを終了"""
        try:
            if hasattr(self, 'driver') and self.driver is not None:
                self.driver.quit()
                logger.info("ブラウザを正常に終了しました")
        except Exception as e:
            logger.error(f"ブラウザの終了に失敗: {str(e)}") 