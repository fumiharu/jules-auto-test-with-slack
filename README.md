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
    # ...他項目も同様に設定
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
          # その他の変数は secrets か env で直接指定
          GITHUB_OWNER: fumiharu
          GITHUB_REPO: ui-automation-test-sample
          TEST_MODE: "False"
        run: |
          pip install -r requirements.txt
          python src/bot.py
    ```

#### アプリの利用開始
起動後、Slackチャンネルにアプリを招待 (`/invite @AutoTestBot`) し、「@AutoTestBot ログインのテストして」のように話しかけてください。
