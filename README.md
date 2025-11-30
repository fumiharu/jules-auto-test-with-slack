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

### 2. インストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env` ファイルを作成し、以下の値を設定してください。

```ini
# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# OpenAI (AI検索・推論用)
OPENAI_API_KEY=sk-your-openai-key

# GitHub (Actions連携用)
GITHUB_TOKEN=ghp-your-github-token
GITHUB_OWNER=your-org
GITHUB_REPO=your-repo
GITHUB_WORKFLOW_ID=ui-test.yml
```

### 4. 実行方法

**本番モード（Slackに接続）:**
```bash
python src/bot.py
```

**シミュレーションモード（CLIで動作確認）:**
Slackに接続せず、ターミナル上で対話をテストできます。
```bash
python simulate_bot.py
```

## カスタマイズ

*   **テストケース**: `mock_data/test_cases.csv` を編集するか、`src/core.py` を修正してGoogleスプレッドシートから読み込むように変更してください。
*   **ロジック**: `src/core.py` 内の `MOCK_MODE` フラグを `False` にすると、実際にOpenAI APIを使用した検索が有効になります。
