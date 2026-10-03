"""CLI 파서와 명령 실행 테스트. 출력 문자열이 정확히 일치하는지 확인한다."""

import unittest

from minigit.cli import execute, parse_line
from minigit.errors import InvalidArgsError, MiniGitError
from minigit.repository import Repository

from .helpers import FakeClock


class ParseLineTests(unittest.TestCase):
    def test_command_is_lowercased(self):
        for line in ("INIT Alice", "init Alice", "InIt Alice"):
            with self.subTest(line=line):
                self.assertEqual(parse_line(line), ("init", ["Alice"], {}))

    def test_quoted_argument_keeps_spaces(self):
        self.assertEqual(
            parse_line('commit "Add login feature"'),
            ("commit", ["Add login feature"], {}),
        )

    def test_option_parsed_into_dict(self):
        self.assertEqual(parse_line("log --sort-by=date"), ("log", [], {"sort-by": "date"}))

    def test_option_value_may_contain_spaces_when_quoted(self):
        self.assertEqual(
            parse_line('search "--author=Jane Doe"'), ("search", [], {"author": "Jane Doe"})
        )

    def test_option_value_may_contain_equals(self):
        self.assertEqual(parse_line("x --k=a=b"), ("x", [], {"k": "a=b"}))

    def test_multiple_positional_arguments(self):
        self.assertEqual(parse_line("path abc def"), ("path", ["abc", "def"], {}))

    def test_blank_line_returns_none(self):
        for line in ("", "   ", "\t"):
            with self.subTest(line=line):
                self.assertIsNone(parse_line(line))

    def test_unbalanced_quote_rejected(self):
        with self.assertRaises(InvalidArgsError):
            parse_line('commit "unclosed')


class CommandOutputTests(unittest.TestCase):
    """명령별 출력 문자열이 기대값과 정확히 일치하는지 확인한다."""

    def setUp(self):
        self.repo = Repository(clock=FakeClock())

    def run_command(self, line: str):
        return execute(self.repo, line)

    def test_init_output(self):
        self.assertEqual(
            self.run_command('init "Alice"'),
            "Initialized repository.\nCurrent branch: main\nCurrent user: Alice",
        )

    def test_commit_output(self):
        self.run_command('init "Alice"')
        output = self.run_command('commit "Initial commit"')
        head = self.repo.commits[self.repo.branches["main"]]
        self.assertEqual(output, f"[main {head.short_hash}] Initial commit")

    def test_branch_and_switch_output(self):
        self.run_command('init "Alice"')
        self.assertEqual(self.run_command("branch feature"), "Created branch: feature")
        self.assertEqual(self.run_command("switch feature"), "Switched to branch: feature")

    def test_user_output(self):
        self.run_command('init "Alice"')
        self.assertEqual(self.run_command('user "Bob"'), "Current user: Bob")

    def test_log_format(self):
        self.run_command('init "Alice"')
        self.run_command('commit "Initial commit"')
        head = self.repo.commits[self.repo.branches["main"]]
        self.assertEqual(
            self.run_command("log"),
            f"commit {head.short_hash} (Alice, 2026-01-15 09:00:00) [main]\n"
            f"    Initial commit",
        )

    def test_log_on_empty_repository(self):
        self.run_command('init "Alice"')
        self.assertEqual(self.run_command("log"), "No commits yet.")

    def test_log_marks_merge_commit(self):
        for line in (
            'init "Alice"', 'commit "root"', "branch feature",
            'commit "on main"', "switch feature", 'commit "on feature"',
            "switch main", "merge feature",
        ):
            self.run_command(line)
        self.assertIn("(merge)", self.run_command("log"))

    def test_log_sorted_by_author_warns_about_broken_order(self):
        for line in ('init "Zoe"', 'commit "root"', 'user "Alice"', 'commit "child"'):
            self.run_command(line)
        self.assertIn("parent may appear after its child", self.run_command("log --sort-by=author"))

    def test_plain_log_has_no_warning(self):
        for line in ('init "Zoe"', 'commit "root"', 'user "Alice"', 'commit "child"'):
            self.run_command(line)
        self.assertNotIn("note:", self.run_command("log"))

    def test_search_singular_and_plural(self):
        self.run_command('init "Alice"')
        self.run_command('commit "Add login feature"')
        self.assertTrue(self.run_command('search "login"').startswith("Found 1 commit:"))
        self.run_command('commit "Fix login bug"')
        self.assertTrue(self.run_command('search "login"').startswith("Found 2 commits:"))

    def test_search_no_result(self):
        self.run_command('init "Alice"')
        self.run_command('commit "Add login feature"')
        self.assertEqual(self.run_command('search "nope"'), "Found 0 commits.")

    def test_search_by_author(self):
        self.run_command('init "Alice"')
        self.run_command('commit "Add login feature"')
        self.assertTrue(self.run_command("search --author=alice").startswith("Found 1 commit:"))

    def test_path_output(self):
        self.run_command('init "Alice"')
        first = self.repo.commit("a")
        second = self.repo.commit("b")
        self.assertEqual(
            self.run_command(f"path {first.short_hash} {second.short_hash}"),
            f"Path: {first.short_hash} -> {second.short_hash}",
        )

    def test_no_path_output(self):
        self.run_command('init "Alice"')
        self.run_command("branch other")
        first = self.repo.commit("root one")
        self.repo.switch("other")
        second = self.repo.commit("root two")
        self.assertEqual(
            self.run_command(f"path {first.short_hash} {second.short_hash}"), "No path"
        )

    def test_ancestors_output(self):
        self.run_command('init "Alice"')
        self.repo.commit("first")
        second = self.repo.commit("second")
        self.assertTrue(
            self.run_command(f"ancestors {second.short_hash}").startswith("Found 1 ancestor:")
        )

    def test_ancestors_of_root(self):
        self.run_command('init "Alice"')
        root = self.repo.commit("root")
        self.assertEqual(self.run_command(f"ancestors {root.short_hash}"), "No ancestors.")

    def test_blank_line_produces_no_output(self):
        self.assertIsNone(self.run_command("   "))

    def test_exit_and_quit_raise_system_exit(self):
        for line in ("exit", "EXIT", "quit", "Quit"):
            with self.subTest(line=line):
                with self.assertRaises(SystemExit):
                    self.run_command(line)


class ErrorMessageTests(unittest.TestCase):
    """표준 에러 메시지가 명세 형식과 일치하는지 확인한다."""

    def setUp(self):
        self.repo = Repository(clock=FakeClock())

    def assert_error(self, line: str, expected: str, setup: tuple = ()):
        for step in setup:
            execute(self.repo, step)
        with self.assertRaises(MiniGitError) as ctx:
            execute(self.repo, line)
        self.assertEqual(str(ctx.exception), expected)

    def test_not_initialized(self):
        self.assert_error('commit "x"', "Repository is not initialized")

    def test_unknown_branch(self):
        self.assert_error("switch nope", "Unknown branch: nope", setup=('init "A"',))

    def test_unknown_commit(self):
        self.assert_error(
            "ancestors zzzzzz", "Unknown commit: zzzzzz", setup=('init "A"', 'commit "x"')
        )

    def test_unknown_command(self):
        self.assert_error("bogus", "Unknown command: bogus")

    def test_wrong_argument_count(self):
        for line in ("init", 'init "A" "B"', "branch", "path a", "path a b c"):
            with self.subTest(line=line):
                with self.assertRaises(MiniGitError) as ctx:
                    execute(Repository(clock=FakeClock()), line)
                self.assertTrue(str(ctx.exception).startswith("Invalid args"))

    def test_unknown_sort_key(self):
        self.assert_error(
            "log --sort-by=size",
            "Invalid args: unknown sort key: size",
            setup=('init "A"', 'commit "x"'),
        )

    def test_unknown_option_rejected(self):
        self.assert_error("log --bogus=1", "Invalid args", setup=('init "A"',))


class SessionTests(unittest.TestCase):
    """명세의 실행 예시 흐름을 그대로 재현한다."""

    SCRIPT = [
        'init "Alice"',
        'commit "Initial commit"',
        "branch feature",
        "switch feature",
        'commit "Add login feature"',
        "switch main",
        'commit "Add payment feature"',
        "log",
        'search "login"',
        "log --sort-by=author",
    ]

    @classmethod
    def run_script(cls) -> list:
        repo = Repository(clock=FakeClock())
        return [execute(repo, line) for line in cls.SCRIPT]

    def test_session_is_reproducible(self):
        self.assertEqual(self.run_script(), self.run_script())

    def test_log_lists_all_three_commits(self):
        log_output = self.run_script()[7]
        self.assertEqual(log_output.count("commit "), 3)
        self.assertIn("[main]", log_output)
        self.assertIn("[feature]", log_output)

    def test_search_finds_one_commit(self):
        self.assertIn("Add login feature", self.run_script()[8])


if __name__ == "__main__":
    unittest.main()