# LINE公式アカウント データダウンロード自動化システム

## プロジェクトの概要

本プロジェクトは、LINE公式アカウントの管理画面から会員データとアンケートデータを自動的にダウンロードし、指定されたGoogleスプレッドシートに転記するシステムです。定期的なデータ収集作業を自動化することで、運用効率の向上と人的ミスの削減を目的としています。

## プログラムの概要

### 主要機能
- LINE公式アカウント管理画面への自動ログイン
- 会員データのCSVダウンロード
- アンケートデータのCSVダウンロード
- ダウンロードしたデータのGoogleスプレッドシートへの転記
- 操作ログの記録
- ダウンロードしたCSVファイルの自動削除

### 技術スタック
- Python 3.x
- Selenium WebDriver (ブラウザ自動操作)
  - Shadow DOM対応
  - 動的要素の待機処理
  - エラーリカバリー機能
- Google Sheets API (スプレッドシートへの書き込み)
- Pandas (CSVデータ処理)
- Logging (ログ管理)
- セレクタ管理システム (CSV形式)

### システム構成
![コンポーネント図](docs/component.md)

主要コンポーネント:
- **Browser**: Seleniumを使用したブラウザ操作
  - Shadow DOM要素の操作
  - 動的要素の待機処理
  - セレクタ管理
  - エラーリカバリー
- **Login**: LINEアカウントへのログイン処理
  - セッション管理
  - 認証エラー処理
- **CsvDownloader**: データダウンロードとファイル処理
  - 複数タグの選択処理
  - ダウンロード状態監視
- **Spreadsheet**: Googleスプレッドシートへのデータ転記
  - バッチ処理による高速化
  - エラー時のロールバック
- **LogSpreadsheet**: 操作ログの記録
  - 詳細なエラー情報の記録
  - 実行状態の追跡

## プログラムの仕様

詳細な仕様については、以下のドキュメントを参照してください：

- [機能仕様書](docs/spec.md): プログラムの詳細な機能と動作仕様
- [シーケンス図](docs/sequence.md): 処理の流れと順序
- [アクティビティ図](docs/activity.md): 処理フローと分岐
- [コンポーネント図](docs/component.md): システム構成
- [データフロー図](docs/data_flow.md): データの流れ
- [クラス図](docs/class_diagram.md): プログラム構造

## 実行方法

### 前提条件
- Python 3.7以上がインストールされていること
- Chromeブラウザがインストールされていること
- インターネット接続が利用可能であること
- Google Cloud Platformのアカウントと認証情報があること

### 環境設定
1. リポジトリのクローン
   ```
   git clone <リポジトリURL>
   cd <プロジェクトディレクトリ>
   ```

2. 設定ファイルの準備
   - `config/settings.ini.template` を `config/settings.ini` にコピーして必要な設定を入力
   - `secrets.env.template` を `secrets.env` にコピーしてLINEアカウント情報とGoogle API認証情報を設定

3. Google認証情報の取得と設定
   - Google Cloud Platformでプロジェクトを作成
   - Google Sheets APIを有効化
   - サービスアカウントキーを作成（JSON形式）
   - キーファイルを `credentials.json` として保存

### 実行コマンド

開発環境では、付属の実行スクリプトを使用します：

```
run_dev.bat
```

実行時に以下のオプションを選択できます：
- Development (dev): 開発者向け、詳細なログとデバッグ情報を表示
- Production (prd): 本番運用向け、安定性重視でユーザー向け

このスクリプトは自動的に：
- 仮想環境の作成
- 必要なパッケージのインストール
- 環境変数の設定
- プログラムの実行

を行います。

## 実行ファイルの作り方 (PyInstaller)

Windowsデスクトップアプリケーションとして配布する場合は、以下の手順で実行ファイル（.exe）を作成できます：

1. 開発環境の準備
   ```
   run_dev.bat
   ```
   を実行し、必要な環境とパッケージを準備します。

2. PyInstallerのインストール（未インストールの場合）
   ```
   pip install pyinstaller
   ```

3. 実行ファイルのビルド
   ```
   pyinstaller line_downloader.spec
   ```

   これにより、line_downloader.specファイルに定義された設定に基づいて実行ファイルが生成されます。
   このspecファイルには以下の設定が含まれています：
   - 必要な設定ファイル（settings.ini, selectors.csv, 認証情報など）の同梱
   - 必要なライブラリの依存関係
   - 実行ファイルの名前と設定

4. ビルド結果の確認
   - `dist` フォルダ内に `line_downloader.exe` ファイルが生成されます
   - 実行時に必要なファイル（設定ファイル、認証情報）が含まれていることを確認

5. 配布準備
   - 実行ファイルと必要な設定ファイルをまとめてzip形式などで配布

### 手動でspecファイルを作成・編集する場合

カスタム設定が必要な場合は、以下のコマンドで新しいspecファイルを生成できます：

```
pyi-makespec --onefile --name line
```

## 実行環境のフォルダ構成

実行ファイル（.exe）を使用する場合、以下のフォルダ構成が必要です：

```
program/
├── line_data_downloader.exe    # 実行ファイル
├── config/                     # 設定ファイル
│   ├── settings.ini           # アプリケーション設定
│   └── selectors.csv          # HTML要素セレクター
├── credentials.json           # Google API認証情報
└── logs/                      # ログファイル出力先
    └── app.log               # アプリケーションログ
```

### 設定ファイルの準備

1. `config/settings.ini`
   ```ini
   [LINE]
   login_url = https://...
   csv_download_url = https://...
   
   [SPREADSHEET]
   spreadsheet_id = your_spreadsheet_id
   friend_sheet_name = Friends
   questionnaire_sheet_name = Questionnaire
   log_sheet_name = Log
   
   [WAIT]
   page_load = 3
   download = 180
   operation = 2
   ```

2. `credentials.json`
   - Google Cloud Platformから取得したサービスアカウントキー
   - 実行ファイルと同じフォルダに配置

### 実行手順

1. 上記のフォルダ構成を準備
2. 設定ファイルを編集
3. 実行ファイルをダブルクリック
4. 実行モード（dev/prd）を選択
5. ログファイルで実行状況を確認

### トラブルシューティング

実行時の主なエラーと対処方法：

1. 設定ファイルが見つからない
   - `config` フォルダと必要なファイルが存在するか確認
   - ファイルパーミッションを確認
   - `selectors.csv` の内容とフォーマットを確認

2. 認証エラー
   - `credentials.json` の内容を確認
   - Google Cloud Platformでの権限設定を確認
   - セッションの有効期限を確認

3. ブラウザエラー
   - Chrome ブラウザが最新版かを確認
   - ブラウザの自動更新設定を確認
   - Shadow DOM対応の確認
   - 動的要素の待機時間を調整

4. ダウンロードエラー
   - インターネット接続を確認
   - ダウンロードフォルダのパーミッションを確認
   - `settings.ini` の待機時間設定を調整
   - タグ選択の状態を確認

5. スプレッドシートエラー
   - スプレッドシートIDの設定を確認
   - シート名の設定を確認
   - API有効化状態を確認
   - データ形式の整合性を確認

6. セレクタエラー
   - `selectors.csv` の最新版を使用しているか確認
   - Shadow DOM要素のセレクタを確認
   - 動的要素の待機設定を確認
   - エラー時の代替セレクタを確認

詳細なエラーメッセージは `logs/app.log` に記録されます。
エラー発生時には自動的にデバッグ情報（HTML, スクリーンショット）が保存されます。