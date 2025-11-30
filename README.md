# AI Auto Test Bot for Slack

Slackから自然言語でUI自動テストを検索・実行するためのボットアプリケーションです。
スプレッドシート（CSV）のテスト仕様書と、GitHub上のテストコードをAIが紐付け、実行をサポートします。

## 機能

*   **自然言語検索**: 「ログインのテストして」などのメッセージから、関連するテストケースを特定します。
*   **AIマッピング**: テスト仕様書と実装コードの紐付けが定義されていなくても、AIが推論して適切なファイルを見つけます。
*   **実行連携**: Slack上のボタンをクリックするだけで、GitHub Actionsのワークフローをトリガーします。

## ディレクトリ構成

*   `src/`: ソースコード
    *   `bot.py`: Slackボットのメインロジック
    *   `core.py`: 検索とマッピングを行うコアロジック
    *   `github_client.py`: GitHub API連携クライアント
*   `mock_data/`: ダミーデータ（テスト仕様書CSVなど）
*   `tests/`: ユニットテストとダミーのUIテストコード

## セットアップ手順

### 1. 必要条件
*   Python 3.9以上
*   Slack App (Bot Token & App Token)
*   OpenAI API Key (AI検索機能を使用する場合)

### 2. Slackアプリの作成と設定（詳細）

このボットを動かすには、Slack APIでアプリを作成し、Socket Modeを有効にする必要があります。

1.  **アプリの作成**:
    *   [Slack API: Your Apps](https://api.slack.com/apps) にアクセスし、「Create New App」をクリックします。
    *   「From scratch」を選択し、アプリ名（例: `AutoTestBot`）とインストール先のワークスペースを指定して「Create App」をクリックします。

2.  **Socket Mode の有効化 (App Tokenの取得)**:
    *   左側メニューの **Socket Mode** をクリックします。
    *   「Enable Socket Mode」をオンにします。
    *   Token Name（例: `socket-token`）を入力し、「Generate」をクリックします。
    *   表示された `xapp-...` から始まるトークンをコピーし、`.env` ファイルの `SLACK_APP_TOKEN` に設定します。

3.  **Event Subscriptions の設定**:
    *   左側メニューの **Event Subscriptions** をクリックします。
    *   「Enable Events」をオンにします。
    *   「Subscribe to bot events」セクションを展開し、「Add Bot User Event」をクリックします。
    *   `app_mention` を検索して追加します。（これでメンションに反応できるようになります）
    *   画面下部の「Save Changes」をクリックします。

4.  **OAuth & Permissions (権限) の設定**:
    *   左側メニューの **OAuth & Permissions** をクリックします。
    *   「Scopes」セクションの「Bot Token Scopes」を確認します。
    *   以下の権限が含まれていることを確認してください（足りなければ追加します）。
        *   `app_mention:read` (Event設定時に自動で追加されているはずです)
        *   `chat:write` (メッセージを送信するために必要です)

5.  **アプリのインストール (Bot Tokenの取得)**:
    *   同じ **OAuth & Permissions** ページの上部にある「Install to Workspace」をクリックします。
    *   許可画面で「Allow」をクリックします。
    *   表示された `xoxb-...` から始まる「Bot User OAuth Token」をコピーし、`.env` ファイルの `SLACK_BOT_TOKEN` に設定します。

### 3. 環境設定と実行

運用環境（ローカルPC または サーバー/クラウド）に合わせて設定を行ってください。

#### A. ローカル開発環境で動かす場合

手元のPCで動かす場合は、`.env` ファイルを使用します。

1.  **ライブラリのインストール**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **設定ファイルの作成**:
    リポジトリ直下の `.env.example` をコピーして `.env` を作成し、中身を編集してください。

    ```bash
    cp .env.example .env
    ```

    ```ini
    # .env ファイルの例
    SLACK_BOT_TOKEN=xoxb-xxxxxxxxx
    SLACK_APP_TOKEN=xapp-xxxxxxxxx
    OPENAI_API_KEY=sk-xxxxxxxxx
    GITHUB_TOKEN=ghp-xxxxxxxxx

    # Google Sheets を使う場合
    GOOGLE_CREDENTIALS_JSON=credentials.json
    GOOGLE_SHEET_KEY=your-spreadsheet-id-here
    ```

3.  **実行**:
    ```bash
    python src/bot.py
    ```

#### B. 本番環境 (GitHub Actions / クラウド) で動かす場合

サーバーやGitHub Actions上で動かす場合は、ファイルではなく**環境変数 (Secrets)** を使用します。セキュリティのため、`.env` ファイルはリポジトリに含めないでください。

1.  **環境変数の設定**:
    実行環境の環境変数設定画面（GitHub Actionsの場合は `Settings > Secrets and variables > Actions`）で、以下のキーと値を登録します。

    *   `SLACK_BOT_TOKEN`
    *   `SLACK_APP_TOKEN`
    *   `OPENAI_API_KEY`
    *   `GITHUB_TOKEN`
    *   その他 `.env.example` に記載されている変数

2.  **GitHub Actions Workflow の例**:
    `.github/workflows/run-bot.yml` のような定義ファイルから起動する場合の記述例です。

    ```yaml
    steps:
      - name: Run Slack Bot
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
          SLACK_APP_TOKEN: ${{ secrets.SLACK_APP_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # Google Sheets (JSON文字列全体をSecretsに登録した場合)
          GOOGLE_CREDENTIALS_JSON: ${{ secrets.GOOGLE_CREDENTIALS_JSON }}
          GOOGLE_SHEET_KEY: ${{ secrets.GOOGLE_SHEET_KEY }}
          # その他の変数は secrets か env で直接指定
          GITHUB_OWNER: fumiharu
          GITHUB_REPO: ui-automation-test-sample
          # 本番モード設定 (必ずFalseにする)
          TEST_MODE: "False"
          MOCK_GITHUB_MODE: "False"
          MOCK_MODE: "False"
        run: |
          pip install -r requirements.txt
          python src/bot.py
    ```

    > **Note:** 連携先の GitHub Actions ワークフロー (`ui-test.yml`) は、`workflow_dispatch` トリガーで `test_target` という入力を受け取るように設定されている必要があります。

### 4. 追加設定 (Google Sheets & OpenAI)

#### A. Google Sheets API の設定

実運用でテストケースをGoogleスプレッドシートで管理する場合の設定です。

1.  **GCPプロジェクトとAPIの有効化**:
    *   [Google Cloud Console](https://console.cloud.google.com/) にアクセスし、新しいプロジェクトを作成します。
    *   「APIとサービス」>「ライブラリ」から **Google Sheets API** を検索し、有効にします。

2.  **サービスアカウントの作成**:
    *   「APIとサービス」>「認証情報」から「認証情報を作成」>「サービスアカウント」を選択します。
    *   適当な名前（例: `auto-test-reader`）を入力して作成します（ロールは空でOK）。
    *   作成されたサービスアカウントのメールアドレス（例: `xxx@project.iam.gserviceaccount.com`）をコピーしておきます。

3.  **キーの発行**:
    *   サービスアカウントの詳細画面で「キー」タブを開き、「鍵を追加」>「新しい鍵を作成」>「JSON」を選択します。
    *   JSONファイルがダウンロードされます。
    *   **ローカル実行時**: このファイルを `credentials.json` などの名前でプロジェクトルートに置き、`.env` の `GOOGLE_CREDENTIALS_JSON` にファイル名を指定します。
    *   **本番(Actions)実行時**: このJSONファイルの**中身すべて**をコピーし、GitHub Secrets (`GOOGLE_CREDENTIALS_JSON`) に貼り付けます。

4.  **スプレッドシートの共有**:
    *   テストケースを記載したGoogleスプレッドシートを開きます。
    *   右上の「共有」ボタンを押し、先ほどコピーしたサービスアカウントのメールアドレスを追加します（権限は「閲覧者」でOK）。
    *   スプレッドシートのURL `https://docs.google.com/spreadsheets/d/XXXXXXXX/edit` の `XXXXXXXX` 部分をコピーし、`.env` の `GOOGLE_SHEET_KEY` に設定します。

#### B. OpenAI API の設定

AIによる検索・推論機能を使用するために必要です。

1.  **APIキーの取得**:
    *   [OpenAI Platform](https://platform.openai.com/api-keys) にアクセスし、アカウントを作成またはログインします。
    *   「Create new secret key」をクリックし、キーを発行します (`sk-...`)。
    *   このキーを `.env` の `OPENAI_API_KEY` に設定します。

2.  **クレジットのチャージ (重要)**:
    *   OpenAI APIは従量課金制です。無料枠がない場合、[Billing settings](https://platform.openai.com/account/billing/overview) でクレジットカードを登録し、クレジット（残高）を購入する必要があります。
    *   残高がないと API エラー (`429 You exceeded your current quota`) が発生します。

#### アプリの利用開始
起動後、Slackチャンネルにアプリを招待 (`/invite @AutoTestBot`) し、「@AutoTestBot ログインのテストして」のように話しかけてください。
