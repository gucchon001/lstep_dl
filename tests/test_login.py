from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import logging
from pathlib import Path
import pandas as pd
import sys
import urllib3

sys.path.append(str(Path(__file__).parent.parent))

from src.utils.environment import EnvironmentUtils as env
from src.utils.logging_config import get_logger

# ロガーの設定
logger = get_logger(__name__)

# ログレベルの設定を追加
urllib3.disable_warnings()
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('WDM').setLevel(logging.ERROR)

class Browser:
    _instance = None  # シングルトンパターンのためのクラス変数
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, settings_path='config/settings.ini', selectors_path='config/selectors.csv'):
        # 初期化が既に完了している場合は何もしない
        if hasattr(self, 'driver') and self.driver is not None:
            return
            
        self.driver = None
        self.settings = env
        self.selectors = self._load_selectors(selectors_path)
        self.wait = None
        
        # ユーザーデータディレクトリの設定
        self.user_data_dir = Path(os.getcwd()) / 'chrome_data'
        self.profile_dir = self.user_data_dir / 'Default'
        self.cookies_file = self.profile_dir / 'Cookies'  # ここで定義
        
        # ディレクトリが存在しない場合は作成
        if not self.profile_dir.exists():
            self.profile_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ プロファイルディレクトリを作成: {self.profile_dir}")
        
        # 初回ログイン判定（プロファイルディレクトリの存在で判断）
        self.is_first = not self.profile_dir.exists() or not any(self.profile_dir.iterdir())
        
        if self.is_first:
            logger.info("🆕 初回ログインとして設定")
        else:
            logger.info("🔄 通常ログインとして設定")
        
        logger.info(f"🔧 ユーザーデータディレクトリを設定: {self.user_data_dir}")
        logger.debug(f"  └ 初回ログイン判定: {self.is_first}")

    def _load_selectors(self, selectors_path):
        """セレクター設定の読み込み"""
        df = pd.read_csv(selectors_path)
        selectors = {}
        for _, row in df.iterrows():
            if row['page'] not in selectors:
                selectors[row['page']] = {}
            selectors[row['page']][row['element']] = {
                'type': row['selector_type'],
                'value': row['selector_value']
            }
        return selectors

    def _get_element(self, page, element, wait=30):
        """指定された要素を取得"""
        try:
            selector = self.selectors[page][element]
            by_type = getattr(By, selector['type'].upper())
            logger.debug(f"要素を探索中: page={page}, element={element}, type={selector['type']}, value={selector['value']}")
            element = WebDriverWait(self.driver, wait).until(
                EC.visibility_of_element_located((by_type, selector['value']))
            )
            logger.info(f"✓ 要素を発見: {element.tag_name}({element.get_attribute('id') or element.get_attribute('class')})")
            return element
        except Exception as e:
            logger.error(f"❌ 要素の取得に失敗: page={page}, element={element}, error={str(e)}")
            raise

    def setup(self):
        """ChromeDriverのセットアップ"""
        options = webdriver.ChromeOptions()
        
        # プロファイルディレクトリの作成を確実に
        if not self.profile_dir.exists():
            self.profile_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ プロファイルディレクトリを作成: {self.profile_dir}")
        
        # セッション関連の設定を最優先
        options.add_argument(f'--user-data-dir={str(self.user_data_dir)}')
        options.add_argument('--profile-directory=Default')
        options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
        
        # セッション永続化の設定
        prefs = {
            'profile.default_content_settings.popups': 0,
            'credentials_enable_service': True,
            'profile.password_manager_enabled': True,
            'profile.persistent_storage_type': 1,  # 永続化を有効に
            'profile.cookie_controls_mode': 0  # Cookieの制限を解除
        }
        options.add_experimental_option('prefs', prefs)
        
        # その他の設定
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('start-maximized')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        # GPUエラー対策
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        
        logger.info(f"🔗 Chrome起動時のユーザーデータパス: {str(self.user_data_dir)}")
        logger.debug(f"  └ Default dir: {self.profile_dir}")
        
        # ヘッドレスモードの設定
        headless = env.get_config_value("BROWSER", "headless", default=True)
        if headless:
            options.add_argument('--headless=new')
            logger.info("ヘッドレスモードで実行します")
        else:
            logger.info("通常モードで実行します")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.maximize_window()

        # セッションファイルの作成は初回のみ
        if not self.cookies_file.exists():
            self.cookies_file.touch()
            logger.info("✓ Cookieファイルを作成しました")

    def access_site(self, url):
        """指定されたURLにアクセスする"""
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"❌ サイトアクセスエラー: {str(e)}")
            return False
            
    def get_url(self):
        """現在のURLを取得する"""
        return self.driver.current_url

    def is_already_logged_in(self, admin_home_url):
        try:
            logger.info("🔍 ログイン状態チェック開始")
            
            # アクセス前のURL
            logger.debug(f"アクセス前のURL: {self.get_url()}")
            
            # LMEと同じ方式でアクセス
            logger.debug("ホームページにアクセス試行")
            self.access_site("https://manager.linestep.net/")
            time.sleep(2)  # リダイレクトの完了を待つ
            
            # アクセス後のURL
            current_url = self.get_url()
            logger.debug(f"アクセス後のURL: {current_url}")
            
            # Cookieの状態確認
            cookies = self.driver.get_cookies()
            logger.debug(f"現在のCookie数: {len(cookies)}")
            for cookie in cookies:
                logger.debug(f"Cookie: {cookie.get('name')} = {cookie.get('value')[:10]}...")
            
            # セッションの有効性を確認（URLベースの判定）
            if 'login' not in current_url:
                logger.info("✅ 既存セッションが有効です")
                return True
            
            # セッションが無効な場合、Cookieをクリア
            logger.info("🗑️ 無効なセッションをクリア")
            self.driver.delete_all_cookies()
            if self.cookies_file.exists():
                self.cookies_file.unlink()
                logger.info("🗑️ ログインクッキーをクリアしました")
            
            logger.info("❌ セッションが無効です")
            logger.debug(f"リダイレクト先URL: {current_url}")
            return False
            
        except Exception as e:
            logger.error(f"❌ セッション確認でエラー: {str(e)}")
            logger.exception("詳細なエラー情報:")
            return False

class Login:
    def __init__(self, browser):
        """
        ログイン機能を管理するクラス
        
        Args:
            browser: Browserクラスのインスタンス
        """
        self.browser = browser
        logger.info("=== ログインプロセスを開始 ===")

    def execute(self):
        try:
            admin_home_url = "https://manager.linestep.net/"
            logger.info("👤 新規ログインを開始します")
            return self._perform_login(admin_home_url)
            
        except Exception as e:
            logger.error(f"❌ ログイン処理でエラー: {str(e)}")
            return False, None

    def _perform_login(self, admin_home_url):
        """実際のログイン処理を実行"""
        try:
            login_url = "https://manager.linestep.net/account/login"
            self.browser.driver.get(login_url)
            logger.info(f"📍 ログインページにアクセス: {login_url}")
            time.sleep(2)

            login_credentials = {
                'id': env.get_env_var('LOGIN_ID'),
                'password': env.get_env_var('LOGIN_PASSWORD')
            }
            logger.debug(f"ログイン情報を取得: ID={login_credentials['id'][:3]}***")

            # ログインフォームの入力
            logger.info("ユーザー名フィールドを探索中...")
            username_field = self.browser._get_element('login', 'username')
            username_field.clear()
            username_field.send_keys(login_credentials['id'])
            logger.info(f"✓ ユーザー名を入力: {login_credentials['id'][:3]}***")
            time.sleep(1)

            logger.info("パスワードフィールドを探索中...")
            password_field = self.browser._get_element('login', 'password')
            password_field.clear()
            password_field.send_keys(login_credentials['password'])
            logger.info("✓ パスワードを入力: ********")
            time.sleep(1)

            logger.info("⚠️ reCAPTCHA認証を待機中...")
            print("\n⚠️ reCAPTCHA認証を手動で完了し、ログインボタンをクリックしてください")
            
            # URLの変更を監視
            current_url = self.browser.driver.current_url
            for _ in range(300):  # 5分間待機
                time.sleep(1)
                try:
                    new_url = self.browser.driver.current_url
                    if new_url != current_url and 'login' not in new_url:
                        logger.info("✅ ログイン成功")
                        return True, admin_home_url
                except Exception as e:
                    logger.error(f"URL確認でエラー: {str(e)}")
                    continue
            
            logger.error("ログインタイムアウト")
            return False, None

        except Exception as e:
            logger.error(f"❌ ログイン処理でエラー: {str(e)}")
            return False, None

def setup_configurations():
    """設定ファイルと機密情報をロードしてデータを取得します。"""
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

def main():
    """メイン処理"""
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
        success, admin_url = login.execute()

        if success:
            logger.info("ログインに成功しました")
            print("✅ ログイン成功")
            # ここに追加の処理を記述
            time.sleep(2)  # 画面遷移を待機
        else:
            logger.error("ログインに失敗しました")
            print("❌ ログイン失敗")

    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
    finally:
        # ブラウザを終了
        if 'browser' in locals():
            browser.driver.quit()
            logger.info("ブラウザを終了しました")

if __name__ == "__main__":
    main() 