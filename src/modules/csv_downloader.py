from datetime import datetime
import time
from pathlib import Path
from ..utils.logging_config import get_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from ..modules.spreadsheet import Spreadsheet
from .log_spreadsheet import LogSpreadsheet  # 新しいインポート

logger = get_logger(__name__)

class CsvDownloader:
    def __init__(self, browser):
        """CSVダウンロードを管理するクラス"""
        self.browser = browser

    def execute(self):
        """CSVダウンロードの実行"""
        spreadsheet = Spreadsheet()
        log_sheet = LogSpreadsheet()  # ログ用インスタンスを作成
        try:
            # 友達リストをクリック
            logger.info("📋 友達リストページに遷移します")
            friend_list = self.browser._get_element('menu', 'friend_list')
            if not friend_list:
                logger.error("❌ 友達リストの要素が見つかりません")
                return False
            friend_list.click()
            time.sleep(2)
            
            # CSV操作をクリック（スクロールしてから）
            logger.info("📊 CSV操作メニューを開きます")
            csv_operation = self.browser._get_element('menu', 'csv_operation')
            if not csv_operation:
                logger.error("❌ CSV操作メニューの要素が見つかりません")
                return False
            # 要素が見えるようにスクロール
            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", csv_operation)
            time.sleep(1)
            # 要素をクリック
            ActionChains(self.browser.driver).move_to_element(csv_operation).click().perform()
            time.sleep(1)
            
            # CSVエクスポートをクリック
            logger.info("📥 CSVエクスポートページに遷移します")
            csv_export = self.browser._get_element('menu', 'csv_export_mover')
            if not csv_export:
                logger.error("❌ CSVエクスポートの要素が見つかりません")
                return False
            csv_export.click()
            time.sleep(2)
            
            # チェックボックスの処理
            logger.info("✓ チェックボックスの選択を開始")
            checkboxes = [
                'name', 'short_name', 'nickname', 'status_message', 'memo',
                'created_at', 'notify', 'rate_text', 'is_blocked',
                'last_message', 'last_message_at', 'scenario', 'scenario_time'
            ]
            
            for checkbox_id in checkboxes:
                try:
                    checkbox = self.browser.driver.find_element(By.ID, checkbox_id)
                    if not checkbox.is_selected():
                        checkbox.click()
                        time.sleep(0.5)
                        logger.info(f"✓ チェックボックス {checkbox_id} を選択")
                except Exception as e:
                    logger.warning(f"チェックボックス {checkbox_id} の選択に失敗: {str(e)}")
            
            # 流入経路をクリック
            logger.info("✓ 流入経路を選択")
            
            # 流入経路セレクタを取得
            host_css = "v3-item-selector"
            inner_css = self.browser.selectors['csv']['tag_list']['value'].replace(host_css, '').strip()
            self.browser.waitForShadowElementsPresent(host_css, inner_css, wait_seconds=20)
            logger.info("✓ Shadow DOM内候補の出現を確認")

            # 設定から流入経路ラベルの候補を取得（なければ既定の文字列を使用）
            inflow_label = self.browser.settings.get_config_value('TAGS', 'inflow_label', default='【24年10月～】流入経路')
            # Shadow DOM 内のテキスト一致でクリック
            self.browser.clickShadowItemByText(host_css, inner_css, inflow_label, scroll_into_view=True)
            
            # タグリストの取得（セレクタCSVの定義を使用）
            host_css = "v3-item-selector"
            inner_css = self.browser.selectors['csv']['tag_list']['value'].replace(host_css, '').strip()
            self.browser.waitForShadowElementsPresent(host_css, inner_css, wait_seconds=20)
            tag_elements = self.browser.findShadowElements(host_css, inner_css)
            logger.info(f"✓ {len(tag_elements)} 個のタグ要素を取得しました")
            
            # 設定ファイルから選択するタグを取得
            selected_tags_str = self.browser.settings.get_config_value('TAGS', 'selected_tags', default='')
            selected_tags2_str = self.browser.settings.get_config_value('TAGS', 'selected_tags2', default='')
            
            # 両方のタグパターンをリストに変換
            tag_patterns = [
                ('selected_tags', [tag.strip() for tag in selected_tags_str.split(',') if tag.strip()]),
                ('selected_tags2', [tag.strip() for tag in selected_tags2_str.split(',') if tag.strip()])
            ]

            # 各タグパターンセットに対して処理を実行
            for pattern_name, selected_tags in tag_patterns:
                if selected_tags:
                    logger.info(f"✓ {pattern_name}から {len(selected_tags)} 個のタグパターンを検索します")
                    
                    host_css = "v3-item-selector"
                    inner_css = "div.itempool ul li span:nth-child(2)"
                    selected_count = 0
                    for pattern in selected_tags:
                        logger.info(f"✓ タグ「{pattern}」を選択します (パターン: {pattern})")
                        # Shadow DOM 内のテキスト一致でクリック
                        if self.browser.clickShadowItemByText(host_css, inner_css, pattern, scroll_into_view=True):
                            selected_count += 1
                            logger.info(f"✓ タグ「{pattern}」のクリックに成功")
                    
                    logger.info(f"✓ {pattern_name}から合計 {selected_count} 個のタグを選択しました")
                    
                    # タグを選択した後、「表示中のタグを一括追加」ボタンをクリック
                    logger.info("✓ 表示中のタグを一括追加します")
                    # 現在のところShadow DOM内では直接セレクタを使用
                    self.browser.clickShadowItemByText(
                        'v3-item-selector',
                        'div.itempool div.item_selector ul li:nth-child(1) span',
                        '表示中のタグを一括追加します',
                        scroll_into_view=True
                    )
                    time.sleep(1)  # 一括追加後の待機
            
            if not any(tags for _, tags in tag_patterns):
                # どちらのタグパターンも指定されていない場合は従来通りタグ一括追加
                logger.info("✓ タグを一括追加")
                # 現在のところShadow DOM内では直接セレクタを使用
                self.browser.clickShadowItemByText(
                    'v3-item-selector',
                    'div.itempool div.item_selector ul li:nth-child(1) span',
                    '表示中のタグを一括追加します',
                    scroll_into_view=True
                )
            
            # ページ最下部までスクロール
            logger.info("📜 ページ最下部までスクロール")
            self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # スクロール後の待機
            
            # 送信ボタンをクリック
            logger.info("🔘 送信ボタンのクリックを試行")
            submit_button = self.browser._get_element('csv', 'submit_button')
            self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # スクロール後の待機
            self.browser.driver.execute_script("arguments[0].click();", submit_button)
            logger.info("✓ CSVエクスポートを開始しました")
            
            # エクスポート完了まで待機（3分）に変更
            logger.info("⏳ エクスポート完了を3分間待機します...")
            time.sleep(180)  # 60秒から180秒に変更
            
            # ダウンロードボタンのクリック
            logger.info("📥 最新のCSVファイルのダウンロードを試みます")
            self.browser.driver.refresh()
            logger.info("ページをリフレッシュしました")
            time.sleep(5)  # ページロード待機
            
            # ダウンロードボタンを探して操作
            download_button = self.browser._get_element('csv', 'latest_download', wait=10)
            download_button.click()
            logger.info("✓ ダウンロードボタンをクリックしました")
            
            # ダウンロード完了を待機
            downloads_path = Path.home() / "Downloads"
            base_pattern = "member_*.csv"
            
            logger.info("⏳ CSVファイルのダウンロード完了を待機中...")
            for _ in range(12):  # 最大60秒待機
                time.sleep(5)
                csv_files = list(downloads_path.glob(base_pattern))
                
                if csv_files:
                    latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
                    if time.time() - latest_csv.stat().st_mtime < 5:
                        logger.info(f"✓ 新しい会員CSVファイルを検出: {latest_csv.name}")
                        
                        # スプレッドシートに転記
                        logger.info("📊 会員データをスプレッドシートに転記します")
                        if spreadsheet.update_sheet(str(latest_csv), sheet_type='friend'):
                            logger.info("✅ 会員データの転記が完了しました")
                            
                            # CSVファイルの削除
                            try:
                                latest_csv.unlink()
                                logger.info(f"✓ CSVファイルを削除しました: {latest_csv.name}")
                            except Exception as e:
                                logger.warning(f"CSVファイルの削除に失敗: {str(e)}")
                            
                            # 成功時のログ記録
                            log_sheet.log_operation(
                                operation_type="会員データダウンロード",
                                status="成功",
                                error_message=None
                            )
                            return True
                        else:
                            error_msg = "会員データの転記に失敗しました"
                            logger.error(f"❌ {error_msg}")
                            # エラーログを記録
                            log_sheet.log_operation(
                                operation_type="会員データダウンロード",
                                status="失敗",
                                error_message=error_msg
                            )
                            return False
            
            error_msg = "会員CSVファイルのダウンロードがタイムアウトしました"
            logger.error(f"❌ {error_msg}")
            # エラーログを記録
            log_sheet.log_operation(
                operation_type="会員データダウンロード",
                status="失敗",
                error_message=error_msg
            )
            return False
                
        except Exception as e:
            error_msg = f"CSVダウンロード処理でエラー: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # エラーログを記録
            log_sheet.log_operation(
                operation_type="会員データダウンロード",
                status="失敗",
                error_message=error_msg
            )
            return False

    def download_questionnaire(self):
        """アンケートデータのダウンロード処理"""
        spreadsheet = Spreadsheet()
        log_sheet = LogSpreadsheet()
        try:
            # 回答フォームをクリック
            logger.info("�� 回答フォームページに遷移します")
            questionnaire_link = self.browser._get_element('menu', 'questionnaire_form')
            questionnaire_link.click()
            time.sleep(3)
            
            # 回答一覧DLをクリック
            logger.info("📥 回答一覧をダウンロードします")
            download_link = self.browser._get_element('questionnaire', 'download_answers')
            download_link.click()
            
            # ダウンロード完了を待機
            logger.info("⏳ ダウンロード完了を待機中...")
            downloads_path = Path.home() / "Downloads"
            base_pattern = "LINE登録時初回アンケート_*回答_*.csv"
            
            for _ in range(12):  # 最大60秒待機
                time.sleep(5)
                csv_files = list(downloads_path.glob(base_pattern))
                
                if csv_files:
                    latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
                    if time.time() - latest_csv.stat().st_mtime < 5:
                        logger.info(f"✓ 新しいアンケートCSVファイルを検出: {latest_csv.name}")
                        
                        # スプレッドシートに転記
                        logger.info("📊 アンケートデータをスプレッドシートに転記します")
                        if spreadsheet.update_sheet(str(latest_csv), sheet_type='anq_data'):
                            logger.info("✅ アンケートデータの転記が完了しました")
                            
                            # CSVファイルの削除
                            try:
                                latest_csv.unlink()
                                logger.info(f"✓ CSVファイルを削除しました: {latest_csv.name}")
                            except Exception as e:
                                logger.warning(f"CSVファイルの削除に失敗: {str(e)}")
                            
                            # 成功時のログ記録
                            log_sheet.log_operation(
                                operation_type="アンケートデータダウンロード",
                                status="成功",
                                error_message=None
                            )
                            return True
                        else:
                            error_msg = "アンケートデータの転記に失敗しました"
                            logger.error(f"❌ {error_msg}")
                            # エラーログを記録
                            log_sheet.log_operation(
                                operation_type="アンケートデータダウンロード",
                                status="失敗",
                                error_message=error_msg
                            )
                            return False
            
            error_msg = "アンケートCSVファイルのダウンロードがタイムアウトしました"
            logger.error(f"❌ {error_msg}")
            # エラーログを記録
            log_sheet.log_operation(
                operation_type="アンケートデータダウンロード",
                status="失敗",
                error_message=error_msg
            )
            return False
                
        except Exception as e:
            error_msg = f"アンケートデータのダウンロードでエラー: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # エラーログを記録
            log_sheet.log_operation(
                operation_type="アンケートデータダウンロード",
                status="失敗",
                error_message=error_msg
            )
            return False 