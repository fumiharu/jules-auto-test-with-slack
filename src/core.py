import os
import glob
import pandas as pd
from typing import List, Optional, Dict
import openai
import json

# モックモードの制御 (環境変数で制御可能にする)
MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() == "true"

class TestRegistry:
    def __init__(self, csv_path: str, tests_root: str):
        self.csv_path = csv_path
        self.tests_root = tests_root
        self.df = self._load_csv()
        self.available_scripts = self._scan_scripts()

    def _load_csv(self) -> pd.DataFrame:
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        return pd.read_csv(self.csv_path)

    def _scan_scripts(self) -> Dict[str, str]:
        """
        Scans the tests directory and returns a mapping of {filepath: content_summary}.
        content_summary includes filename and docstrings.
        """
        scripts = {}
        search_pattern = os.path.join(self.tests_root, "**/*.py")
        for filepath in glob.glob(search_pattern, recursive=True):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 簡易的なDocstring抽出 (本来はastモジュールなどを使うとより正確)
                    scripts[filepath] = content
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
        return scripts

    def search_test_case(self, query: str) -> Optional[Dict]:
        """
        Searches for the most relevant test case in the CSV based on the user query.
        Returns a dictionary representing the row, or None if not found.
        """
        # 1. 簡易的なキーワード検索 (モック/フォールバック用)
        # 本来はここでOpenAIを使ってクエリの意味解析を行い、CSV内の description とマッチングする

        if MOCK_MODE:
            print(f"[DEBUG] Searching for query: {query}")
            # デモ用に単純なキーワードマッチ
            # 除外ワードリスト
            ignore_words = ["make", "me", "a"]
            query_words = [w for w in query.lower().split() if w not in ignore_words]

            if not query_words:
                return None

            for _, row in self.df.iterrows():
                text = f"{row['title']} {row['description']}".lower()
                # 少なくとも1つの意味のある単語がヒットすること
                if any(word in text for word in query_words):
                    return row.to_dict()
            return None

        # 2. OpenAIを使用した検索 (TODO: 実装)
        # Prompt: "User query: {query}. Which of these test cases is most relevant? {json_of_csv}"
        return self._ai_search_csv(query)

    def resolve_script_path(self, test_case: Dict) -> str:
        """
        Determines the script path for a given test case.
        If 'script_path' is empty in CSV, uses AI to find the best matching script.
        """
        if pd.notna(test_case.get("script_path")) and test_case["script_path"]:
            return test_case["script_path"]

        print(f"[INFO] Script path missing for '{test_case['title']}'. Searching in codebase...")

        if MOCK_MODE:
            # モックロジック: ファイル名に特定のキーワードが含まれていればヒットとする
            # 実際にはここでAIにファイルの中身を見せて選ばせる
            keywords = test_case['title'].lower().split()
            for filepath in self.available_scripts.keys():
                filename = os.path.basename(filepath).lower()
                if any(k in filename for k in keywords if len(k) > 3): # 3文字以上のキーワードでマッチ
                    return filepath
            return "No matching script found (Mock)"

        return self._ai_find_script(test_case)

    def _ai_search_csv(self, query: str) -> Optional[Dict]:
        # OpenAI API implementation placeholder
        pass

    def _ai_find_script(self, test_case: Dict) -> str:
        # OpenAI API implementation placeholder
        # Prompt: "Here is a test case description: {desc}. Here are available scripts: {list}. Which one matches?"
        pass

# 使用例 (デバッグ用)
if __name__ == "__main__":
    registry = TestRegistry("mock_data/test_cases.csv", "tests/ui")

    # Case 1: CSVにパスがある場合
    print("--- Case 1: Login ---")
    case1 = registry.search_test_case("login")
    if case1:
        print(f"Found Case: {case1['title']}")
        path = registry.resolve_script_path(case1)
        print(f"Script Path: {path}")

    # Case 2: CSVにパスがなく、推論が必要な場合 (例: Checkout)
    print("\n--- Case 2: Checkout ---")
    case2 = registry.search_test_case("checkout")
    if case2:
        print(f"Found Case: {case2['title']}")
        path = registry.resolve_script_path(case2)
        print(f"Script Path: {path}")
