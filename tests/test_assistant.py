"""B3-2 AI 기반 Git 커밋/PR 자동 생성기 단위 및 통합 테스트."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# src 경로 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

import convention as conv
from ai_client import AIClient
from git_collector import GitCollector
from prompt_builder import build_commit_prompt, build_pr_prompt
from validator import validate_commit, validate_pr, COMMIT_HARD, PR_TITLE_MAX
from main import build_parser


class TestGitCollector(unittest.TestCase):
    """Git 수집기 및 안전 모드(Safe Mode) 테스트."""

    def setUp(self):
        self.collector = GitCollector()

    def test_is_git_repo(self):
        """Git 저장소 내부인지 올바르게 감지해야 한다."""
        self.assertTrue(self.collector.is_git_repo())

    def test_safe_mode_masking(self):
        """Safe mode에서 API Key, 토큰, 비밀번호, 이메일이 마스킹되어야 한다."""
        sensitive_diff = (
            "diff --git a/config.py b/config.py\n"
            "+OPENAI_KEY = 'sk-123456789012345678901234567890'\n"
            "+AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n"
            "+admin_email = 'developer@company.com'\n"
            "+password = 'SuperSecret123!'\n"
        )
        masked_diff, stats = self.collector._apply_safe(sensitive_diff, max_files=10, max_lines=200)

        self.assertNotIn("sk-123456789012345678901234567890", masked_diff)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", masked_diff)
        self.assertNotIn("developer@company.com", masked_diff)
        self.assertIn("[MASKED_API_KEY]", masked_diff)
        self.assertIn("[MASKED_AWS_KEY]", masked_diff)
        self.assertIn("[MASKED_EMAIL]", masked_diff)
        self.assertGreater(stats['masked'], 0)

    def test_safe_mode_line_truncation(self):
        """Safe mode에서 최대 라인 수를 초과하면 잘라내고 안내 문구를 추가해야 한다."""
        long_diff = "\n".join([f"+line {i}" for i in range(100)])
        truncated, stats = self.collector._apply_safe(long_diff, max_files=10, max_lines=30)
        lines = truncated.splitlines()

        self.assertLessEqual(len(lines), 35)
        self.assertIn("[SAFE] 70줄 생략됨", truncated)
        self.assertEqual(stats['lines_trimmed'], 70)


class TestAIClient(unittest.TestCase):
    """AI 클라이언트 환경변수 및 예외 처리 테스트."""

    def test_missing_api_key_exits(self):
        """AI_API_KEY 및 OPENROUTER_API_KEY가 모두 없으면 [ERROR] 출력 후 sys.exit(1)해야 한다."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                AIClient(model="anthropic/claude-3.5-haiku", temperature=0.3, max_tokens=100)
            self.assertEqual(cm.exception.code, 1)

    def test_api_key_recognized_from_env(self):
        """AI_API_KEY가 환경변수로 제공되면 정상 초기화되어야 한다."""
        with patch.dict(os.environ, {'AI_API_KEY': 'sk-test-key'}, clear=True):
            client = AIClient(model="anthropic/claude-3.5-haiku", temperature=0.3, max_tokens=100)
            self.assertIsNotNone(client.client)
            self.assertEqual(client.model, "anthropic/claude-3.5-haiku")


class TestPromptBuilder(unittest.TestCase):
    """프롬프트 빌더 형식 및 템플릿 테스트."""

    def test_commit_prompt_contains_rules_and_diff(self):
        """커밋 프롬프트는 필수 규칙과 diff 내용을 포함해야 한다."""
        prompt = build_commit_prompt("M file.py", "+new line", {'commit_language': 'ko', 'commit_prefix': True})
        self.assertIn("50자 이내 권장", prompt)
        self.assertIn("--- GIT DIFF ---", prompt)
        self.assertIn("+new line", prompt)

    def test_pr_prompt_contains_required_sections(self):
        """PR 프롬프트는 Why, What, How to Test 섹션을 반드시 포함해야 한다."""
        prompt = build_pr_prompt("M file.py", "+new line", "feature/login", conv.DEFAULTS)
        self.assertIn("## Why", prompt)
        self.assertIn("## What", prompt)
        self.assertIn("## How to Test", prompt)
        self.assertIn("feature/login", prompt)


class TestValidator(unittest.TestCase):
    """길이 및 형식 검증기(Validator) 테스트."""

    def test_validate_commit_title_truncation(self):
        """72자를 초과하는 커밋 제목은 72자로 자르고 본문은 유지해야 한다."""
        long_title = "feat: " + "a" * 80
        body = "\n\n- 상세 내용 설명"
        raw_commit = long_title + body
        validated = validate_commit(raw_commit)

        lines = validated.splitlines()
        self.assertEqual(len(lines[0]), COMMIT_HARD)
        self.assertIn("- 상세 내용 설명", validated)

    def test_validate_pr_title_truncation(self):
        """80자를 초과하는 PR 제목은 80자로 잘라야 한다."""
        long_title = "TITLE: feat: " + "p" * 90
        raw_pr = f"{long_title}\n\n## Why\n- 이유\n\n## What\n- 내용\n\n## How to Test\n- 방법"
        title, body = validate_pr(raw_pr)

        self.assertLessEqual(len(title), PR_TITLE_MAX)
        self.assertIn("## Why", body)

    def test_validate_pr_ensures_missing_sections(self):
        """필수 섹션이 누락된 경우 후처리로 자동 추가되어야 한다."""
        broken_pr = "TITLE: feat: test\n\n## Why\n- 이유 설명"
        title, body = validate_pr(broken_pr)

        self.assertIn("## Why", body)
        self.assertIn("## What", body)
        self.assertIn("## How to Test", body)

    def test_validate_pr_ensures_bullets(self):
        """각 섹션에 불릿(-)이 누락된 경우 기본 불릿이 추가되어야 한다."""
        broken_bullets = "TITLE: feat: test\n\n## Why\n이유만 텍스트로 서술\n\n## What\n내용만 텍스트로 서술\n\n## How to Test\n테스트 방법"
        title, body = validate_pr(broken_bullets)

        self.assertIn("## Why\n- ", body)
        self.assertIn("## What\n- ", body)
        self.assertIn("## How to Test\n- ", body)


class TestCLIParser(unittest.TestCase):
    """CLI 옵션 파싱 (단일 하이픈 및 이중 하이픈 지원) 테스트."""

    def setUp(self):
        self.parser = build_parser()

    def test_double_dash_options(self):
        """--temperature 및 --max-tokens 옵션이 정상 파싱되어야 한다."""
        args = self.parser.parse_args(['--temperature', '0.7', '--max-tokens', '512', 'commit'])
        self.assertEqual(args.temperature, 0.7)
        self.assertEqual(args.max_tokens, 512)
        self.assertEqual(args.command, 'commit')

    def test_single_dash_options(self):
        """-temperature 및 -max-tokens 옵션이 정상 파싱되어야 한다."""
        args = self.parser.parse_args(['-temperature', '0.5', '-max-tokens', '256', '-safe-mode', 'pr'])
        self.assertEqual(args.temperature, 0.5)
        self.assertEqual(args.max_tokens, 256)
        self.assertTrue(args.safe_mode)
        self.assertEqual(args.command, 'pr')

    def test_options_after_subcommand(self):
        """서브커맨드 뒤에 옵션이 지정되어도 정상 파싱되어야 한다."""
        args = self.parser.parse_args(['commit', '-temperature', '0.2', '-safe-mode'])
        self.assertEqual(args.command, 'commit')
        self.assertEqual(args.temperature, 0.2)
        self.assertTrue(args.safe_mode)


if __name__ == '__main__':
    unittest.main()
