# Interactive Simulation Script
import os
import sys

# Mock environment variables for simulation
os.environ["TEST_MODE"] = "True"
os.environ["MOCK_GITHUB_MODE"] = "True"
os.environ["MOCK_MODE"] = "True" # Core logic mock
os.environ["SLACK_BOT_TOKEN"] = "xoxb-dummy"

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from core import TestRegistry
from github_client import GitHubClient

def simulate():
    print("=== Auto Test Bot Simulation ===")
    print("Type your message (e.g., 'login', 'checkout'). Type 'exit' to quit.")

    registry = TestRegistry("mock_data/test_cases.csv", "tests/ui")
    github = GitHubClient()

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        print(f"[Bot] Thinking...")

        # 1. Search
        test_case = registry.search_test_case(user_input)

        if not test_case:
            print("[Bot] Sorry, I couldn't find any relevant test case.")
            continue

        # 2. Resolve Path
        script_path = registry.resolve_script_path(test_case)

        print(f"\n[Bot] Found test case!")
        print(f"      Title: {test_case['title']}")
        print(f"      Description: {test_case['description']}")
        print(f"      Target Script: {script_path}")

        # 3. Ask for confirmation
        confirm = input("\n[Bot] Do you want to run this test? (y/n): ")

        if confirm.lower() == 'y':
            # 4. Execute
            if github.trigger_workflow(script_path):
                 print(f"[Bot] 🚀 Test execution started for '{script_path}' via GitHub Actions!")
            else:
                 print(f"[Bot] ⚠️ Failed to trigger workflow.")
        else:
            print("[Bot] Cancelled.")

if __name__ == "__main__":
    simulate()
