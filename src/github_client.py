import os
import requests
import json

class GitHubClient:
    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.owner = os.environ.get("GITHUB_OWNER", "fumiharu")
        self.repo = os.environ.get("GITHUB_REPO", "ui-automation-test-sample")
        self.workflow_id = os.environ.get("GITHUB_WORKFLOW_ID", "ui-test.yml")
        self.ref = os.environ.get("GITHUB_REF", "main")

        # モックモード: 環境変数が明示的にFalseでない限りTrue (安全側に倒す)
        self.mock_mode = os.environ.get("MOCK_GITHUB_MODE", "True").lower() != "false"

    def trigger_workflow(self, test_file_path: str) -> bool:
        """
        Triggers a GitHub Actions workflow with the specified test file.
        Returns True if successful, False otherwise.
        """
        if self.mock_mode:
            print(f"[MOCK] Triggering GitHub Workflow '{self.workflow_id}' on '{self.owner}/{self.repo}'")
            print(f"[MOCK] Payload: {{'test_file': '{test_file_path}'}}")
            return True

        if not self.token:
            print("[ERROR] GITHUB_TOKEN is not set.")
            return False

        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/actions/workflows/{self.workflow_id}/dispatches"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

        data = {
            "ref": self.ref,
            "inputs": {
                "test_target": test_file_path
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"[INFO] Successfully triggered workflow for {test_file_path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to trigger workflow: {e}")
            if response is not None:
                print(f"[ERROR] Response body: {response.text}")
            return False
