from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from git_ai.ai_client import AIConfig
from git_ai.cli import run
from git_ai.errors import GitAIError
from git_ai.git_tools import GitChanges
from git_ai.prompts import commit_prompt, pr_prompt
from git_ai.validators import validate_commit_output, validate_pr_output


class FakeClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls: list[tuple[AIConfig, str]] = []

    def generate(self, config: AIConfig, prompt: str) -> str:
        self.calls.append((config, prompt))
        return self.output


class PromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.changes = GitChanges(
            status=" M app.py\n",
            unstaged_diff="diff --git a/app.py b/app.py\n+print('hello')\n",
            staged_diff="",
        )

    def test_commit_prompt_contains_git_context(self) -> None:
        prompt = commit_prompt(self.changes)
        self.assertIn("app.py", prompt)
        self.assertIn("TITLE:", prompt)
        self.assertIn("Git diff", prompt)

    def test_pr_prompt_requires_sections(self) -> None:
        prompt = pr_prompt(self.changes)
        self.assertIn("## Why", prompt)
        self.assertIn("## What", prompt)
        self.assertIn("## How to Test", prompt)


class ValidatorTests(unittest.TestCase):
    def test_valid_commit(self) -> None:
        text = "TITLE: feat: add greeting\nBODY:\n- Update app.py greeting output"
        self.assertEqual(validate_commit_output(text), text)

    def test_commit_requires_bullet(self) -> None:
        with self.assertRaises(GitAIError):
            validate_commit_output("TITLE: feat: no body")

    def test_valid_pr(self) -> None:
        text = """TITLE: Add greeting
## Why
- Explain the change
## What
- Update app.py
## How to Test
- Run the CLI and inspect output"""
        self.assertEqual(validate_pr_output(text), text)

    def test_pr_requires_each_section_bullet(self) -> None:
        with self.assertRaises(GitAIError):
            validate_pr_output("""TITLE: x
## Why
- reason
## What
- change
## How to Test
none""")


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.changes = GitChanges(
            status=" M app.py\n",
            unstaged_diff="diff --git a/app.py b/app.py\n+print('hello')\n",
            staged_diff="",
        )
        self.env = {
            "AI_API_URL": "https://example.invalid/v1/chat/completions",
            "AI_API_KEY": "test-placeholder-key",
        }

    def test_no_changes_skips_api(self) -> None:
        client = FakeClient("should not be used")
        empty = GitChanges(status="", unstaged_diff="", staged_diff="")
        with patch("git_ai.cli.collect_changes", return_value=empty):
            code = run(["commit"], client=client)
        self.assertEqual(code, 0)
        self.assertEqual(client.calls, [])

    def test_commit_options_reach_client(self) -> None:
        output = "TITLE: feat: add greeting\nBODY:\n- Update app.py greeting output"
        client = FakeClient(output)
        with patch.dict(os.environ, self.env, clear=False), patch(
            "git_ai.cli.collect_changes", return_value=self.changes
        ):
            code = run(
                ["commit", "--model", "demo-model", "--temperature", "0.3", "--max-tokens", "250"],
                client=client,
            )
        self.assertEqual(code, 0)
        self.assertEqual(len(client.calls), 1)
        config, _ = client.calls[0]
        self.assertEqual(config.model, "demo-model")
        self.assertEqual(config.temperature, 0.3)
        self.assertEqual(config.max_tokens, 250)

    def test_missing_key_is_error(self) -> None:
        with patch.dict(os.environ, {"AI_API_URL": "https://example.invalid"}, clear=True), patch(
            "git_ai.cli.collect_changes", return_value=self.changes
        ):
            code = run(["commit"], client=FakeClient("unused"))
        self.assertEqual(code, 2)

    def test_pr_generation(self) -> None:
        output = """TITLE: Add greeting
## Why
- Improve the example
## What
- Update app.py
## How to Test
- Run the CLI and inspect the output"""
        client = FakeClient(output)
        with patch.dict(os.environ, self.env, clear=False), patch(
            "git_ai.cli.collect_changes", return_value=self.changes
        ):
            code = run(["pr"], client=client)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
