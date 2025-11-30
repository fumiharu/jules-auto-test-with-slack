from slack_bolt import App
from src.bot import app
import pytest

class MockSay:
    def __init__(self):
        self.last_message = None
        self.last_blocks = None

    def __call__(self, text=None, blocks=None, **kwargs):
        self.last_message = text
        self.last_blocks = blocks

@pytest.fixture
def mock_say():
    return MockSay()

def test_handle_message_found(mock_say):
    # Setup mock event
    event = {"text": "login", "user": "U12345"}

    # Run handler manually (since we can't easily mock the full Bolt stack without a server)
    # We import the handler function logic.
    # To test properly, it's better to refactor the logic out of the decorator or invoke the listener.
    # For simplicity, we'll invoke the logic by importing the registry and simulating the flow.

    from src.bot import registry, handle_message

    # Inject mock_say
    handle_message(event, mock_say)

    # Verify
    assert mock_say.last_blocks is not None
    assert "Found a relevant test case" in mock_say.last_blocks[0]["text"]["text"]
    assert "test_login.py" in mock_say.last_blocks[0]["text"]["text"]
    assert mock_say.last_blocks[1]["elements"][0]["action_id"] == "run_test_action"

def test_handle_message_not_found(mock_say):
    from src.bot import handle_message

    event = {"text": "make me a coffee", "user": "U12345"}
    handle_message(event, mock_say)

    assert "couldn't find" in mock_say.last_message

def test_handle_run_action(mock_say):
    from src.bot import handle_run_test

    ack_called = False
    def mock_ack():
        nonlocal ack_called
        ack_called = True

    body = {
        "user": {"id": "U12345"},
        "actions": [{"value": "tests/ui/auth/test_login.py"}]
    }

    handle_run_test(mock_ack, body, mock_say)

    assert ack_called
    assert "Test execution started" in mock_say.last_message
    assert "tests/ui/auth/test_login.py" in mock_say.last_message
