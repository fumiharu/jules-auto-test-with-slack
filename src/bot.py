import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from core import TestRegistry
from github_client import GitHubClient

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

# Initialize registry and client
registry = TestRegistry("mock_data/test_cases.csv", "tests/ui")
github_client = GitHubClient()

# Initialize App
# TEST_MODEの場合はトークン検証をスキップするように構成 (token_verification_enabled=Falseは存在しないが、
# Appのコンストラクタ呼び出し時にダミートークンでauth.testが走らないように工夫が必要。
# BoltのAppは初期化時に必ずauth.testを行うため、これを回避するにはClientをモックするか、
# テストコード側で App オブジェクトそのものを作らずハンドラだけテストする設計にするのが正道だが、
# ここでは簡易的に、import時にエラーにならないよう try-except で囲むか、Appの初期化自体を遅延させる。
# しかしデコレータ(@app.message)を使う構造上、appはグローバルに必要。
# 解決策: テスト時のみWebClientをモックする。

if os.environ.get("TEST_MODE") == "True":
    # モックのWebClientを使ってauth.testを成功させる
    from unittest.mock import MagicMock
    from slack_sdk.web import WebClient

    class MockWebClient(WebClient):
        def auth_test(self, **kwargs):
             return {"ok": True, "bot_id": "B12345", "user_id": "U12345"}

    app = App(
        token="xoxb-dummy",
        client=MockWebClient(token="xoxb-dummy"),
        request_verification_enabled=False
    )
else:
    app = App(token=SLACK_BOT_TOKEN)

@app.message()
def handle_message(message, say):
    text = message.get("text", "")
    user_id = message.get("user")

    # 1. Search for test case
    test_case = registry.search_test_case(text)

    if not test_case:
        say(f"Sorry <@{user_id}>, I couldn't find any relevant test case for '{text}'.")
        return

    # 2. Resolve script path
    script_path = registry.resolve_script_path(test_case)

    # 3. Ask for confirmation using Block Kit
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Found a relevant test case for *'{text}'*:\n\n*Title:* {test_case['title']}\n*Description:* {test_case['description']}\n*Script:* `{script_path}`"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Run Test",
                        "emoji": True
                    },
                    "value": script_path,
                    "action_id": "run_test_action",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Cancel",
                        "emoji": True
                    },
                    "action_id": "cancel_action",
                    "style": "danger"
                }
            ]
        }
    ]

    say(blocks=blocks, text=f"Found test case: {test_case['title']}")

@app.action("run_test_action")
def handle_run_test(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    script_path = body["actions"][0]["value"]

    # Trigger GitHub Actions
    success = github_client.trigger_workflow(script_path)

    if success:
        say(f"<@{user_id}> Test execution started for `{script_path}`! 🚀\n(Triggered GitHub Workflow)")
    else:
        say(f"<@{user_id}> ⚠️ Failed to start test execution. Please check the logs.")

@app.action("cancel_action")
def handle_cancel(ack, body, say):
    ack()
    say(f"Test execution cancelled.")

if __name__ == "__main__":
    if SLACK_APP_TOKEN:
        SocketModeHandler(app, SLACK_APP_TOKEN).start()
    else:
        print("SLACK_APP_TOKEN not found. Running in mock/test mode might be needed.")
