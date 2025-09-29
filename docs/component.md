```mermaid
C4Component
    title LINE公式アカウント データダウンロード自動化システム - コンポーネント図

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")

    %% カラーテーマの設定
    skinparam {
        BackgroundColor white
        ComponentBackgroundColor white
        ContainerBackgroundColor white
        ComponentBorderColor black
        ContainerBorderColor black
        ArrowColor black
    }

    Container_Boundary(app, "アプリケーション") {
        Component(main, "Main", "Python", "アプリケーションのエントリーポイント\n全体の処理フローを制御\nPyInstaller対応")
        
        Component(browser, "Browser", "Selenium", "ブラウザ操作を管理\nHTML要素の取得と操作\nShadow DOM要素の高度な操作")
        Component(login, "Login", "Python", "ログイン処理を実行\nreCAPTCHA認証対応")
        Component(csv, "CsvDownloader", "Python", "CSVダウンロードと\nデータ処理を管理\n複数タグパターン対応\n\n【友達リストデータ】\n- 13項目チェックボックス選択\n- Shadow DOM操作（流入経路・タグ選択）\n- 複数タグパターン（selected_tags, selected_tags2）\n- 一括追加処理\n- CSV転記（friend_data）\n\n【アンケートデータ】\n- 回答フォーム直接アクセス\n- 回答一覧DL直接クリック\n- CSV転記（anq_data）")
        
        Component(sheet, "Spreadsheet", "Google Sheets API", "スプレッドシートへの\nデータ転記を管理\n動的シート名読み込み")
        Component(log, "LogSpreadsheet", "Google Sheets API", "操作ログの記録を管理\nスプレッドシート連携")
        
        Component(env, "EnvironmentUtils", "Python", "環境設定と\n設定ファイルの管理\nPyInstaller対応")
        Component(logger, "LoggingConfig", "Python", "ログ出力の設定と管理\n日別ログファイル生成")
        Component(slack, "SlackNotifier", "Python", "Slack通知機能\nエラー通知の送信")
    }

    Container_Boundary(external, "外部システム") {
        System_Ext(line, "LINE公式アカウント\n管理画面", "Webアプリケーション")
        System_Ext(gsheet, "Googleスプレッド\nシート", "クラウドサービス")
    }

    Container_Boundary(config, "設定ファイル") {
        ContainerDb(settings, "settings.ini", "設定ファイル", "アプリケーション設定\nタグパターン設定\nシート名設定\n\n【シート名設定】\n- FRIEND_DATA: 友達リストDLデータ\n- ANQ_DATA: アンケートDLデータ\n\n【タグ設定】\n- selected_tags: 【24年10月～】流入経路\n- selected_tags2: 【25年3月～】初回応答")
        ContainerDb(selectors, "selectors.csv", "セレクター定義", "HTML要素のセレクター\nShadow DOM対応\n\n【主要セレクター】\n- friend_list: 友達リスト\n- csv_operation: CSV操作\n- csv_export_mover: CSVエクスポート\n- tag_list: タグリスト（Shadow DOM）\n- questionnaire_form: 回答フォーム\n- download_answers: 回答一覧DL\n\n【チェックボックス】\n- name, short_name, nickname等13項目")
        ContainerDb(secrets, "secrets.env", "環境変数", "認証情報\nSlack Webhook\nサービスアカウント")
    }

    %% メインの依存関係
    Rel(main, browser, "使用")
    Rel(main, login, "使用")
    Rel(main, csv, "使用")

    %% ブラウザ関連の依存関係
    Rel(browser, line, "操作", "Selenium")
    Rel(browser, selectors, "読込")
    Rel(login, browser, "使用")
    Rel(csv, browser, "使用")

    %% スプレッドシート関連の依存関係
    Rel(csv, sheet, "使用")
    Rel(csv, log, "使用")
    Rel(sheet, gsheet, "更新", "API")
    Rel(log, gsheet, "更新", "API")

    %% 設定関連の依存関係
    Rel(env, settings, "読込")
    Rel(env, secrets, "読込")
    Rel(browser, env, "使用")
    Rel(sheet, env, "使用")
    Rel(log, env, "使用")

    %% ログ関連の依存関係
    Rel(main, logger, "使用")
    Rel(browser, logger, "使用")
    Rel(login, logger, "使用")
    Rel(csv, logger, "使用")
    Rel(sheet, logger, "使用")
    Rel(log, logger, "使用")
    Rel(slack, logger, "使用")

    %% Slack通知の依存関係
    Rel(csv, slack, "使用")
    Rel(slack, env, "使用")
``` 