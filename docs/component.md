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
        Component(main, "Main", "Python", "アプリケーションのエントリーポイント\n全体の処理フローを制御")
        
        Component(browser, "Browser", "Selenium", "ブラウザ操作を管理\nHTML要素の取得と操作")
        Component(login, "Login", "Python", "ログイン処理を実行")
        Component(csv, "CsvDownloader", "Python", "CSVダウンロードと\nデータ処理を管理")
        
        Component(sheet, "Spreadsheet", "Google Sheets API", "スプレッドシートへの\nデータ転記を管理")
        Component(log, "LogSpreadsheet", "Google Sheets API", "操作ログの記録を管理")
        
        Component(env, "EnvironmentUtils", "Python", "環境設定と\n設定ファイルの管理")
        Component(logger, "LoggingConfig", "Python", "ログ出力の設定と管理")
    }

    Container_Boundary(external, "外部システム") {
        System_Ext(line, "LINE公式アカウント\n管理画面", "Webアプリケーション")
        System_Ext(gsheet, "Googleスプレッド\nシート", "クラウドサービス")
    }

    Container_Boundary(config, "設定ファイル") {
        ContainerDb(settings, "settings.ini", "設定ファイル", "アプリケーション設定")
        ContainerDb(selectors, "selectors.csv", "セレクター定義", "HTML要素のセレクター")
        ContainerDb(secrets, "secrets.env", "環境変数", "認証情報")
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
``` 