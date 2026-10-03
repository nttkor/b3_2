from __future__ import annotations

import unittest

from mini_git.algorithms import stable_merge_sort
from mini_git.cli import execute
from mini_git.models import Commit
from mini_git.repository import MiniGitError, MiniGitRepository


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = MiniGitRepository()
        self.repo.init("alice")

    def test_init_branch_switch_and_commit_graph(self) -> None:
        self.assertEqual(self.repo.head_branch, "main")
        self.assertEqual(self.repo.current_user, "alice")
        self.assertIsNone(self.repo.current_head())

        first = self.repo.commit("Initial commit")
        self.repo.branch("feature/login")
        self.repo.switch("feature/login")
        second = self.repo.commit("Add login feature")

        self.assertEqual(first.parents, [])
        self.assertEqual(second.parents, [first.hash])
        self.assertEqual(self.repo.current_head(), second.hash)
        self.assertEqual(self.repo.branches["main"], first.hash)

    def test_commit_hashes_are_unique_in_session(self) -> None:
        hashes = [self.repo.commit("commit {}".format(index)).hash for index in range(50)]
        self.assertEqual(len(hashes), len(set(hashes)))
        self.assertEqual(hashes[0], "c000001")
        self.assertEqual(hashes[-1], "c000050")

    def test_parent_first_log_across_diverged_branches(self) -> None:
        root = self.repo.commit("root")
        self.repo.branch("left")
        self.repo.branch("right")

        self.repo.switch("left")
        left = self.repo.commit("left")
        self.repo.switch("right")
        right = self.repo.commit("right")

        hashes = [commit.hash for commit in self.repo.log_parent_first()]
        self.assertLess(hashes.index(root.hash), hashes.index(left.hash))
        self.assertLess(hashes.index(root.hash), hashes.index(right.hash))

    def test_shortest_path_across_branches_and_same_commit(self) -> None:
        root = self.repo.commit("root")
        self.repo.branch("left")
        self.repo.branch("right")

        self.repo.switch("left")
        left1 = self.repo.commit("left one")
        left2 = self.repo.commit("left two")

        self.repo.switch("right")
        right1 = self.repo.commit("right one")

        self.assertEqual(
            self.repo.path(left2.hash, right1.hash),
            [left2.hash, left1.hash, root.hash, right1.hash],
        )
        self.assertEqual(self.repo.path(root.hash, root.hash), [root.hash])

    def test_path_no_path_for_disconnected_roots(self) -> None:
        # A branch created before the first commit still points to None. Committing
        # independently on each empty branch creates two disconnected roots.
        self.repo.branch("other")
        main_root = self.repo.commit("main root")
        self.repo.switch("other")
        other_root = self.repo.commit("other root")
        self.assertIsNone(self.repo.path(main_root.hash, other_root.hash))

    def test_path_lexicographic_tie_break(self) -> None:
        # Inject a valid DAG with two equal-length paths: s-a-t and s-b-t.
        self.repo.commits = {
            "s": Commit("s", "source", "alice", "2026-01-01T00:00:00+00:00", []),
            "a": Commit("a", "left", "alice", "2026-01-02T00:00:00+00:00", ["s"]),
            "b": Commit("b", "right", "alice", "2026-01-02T00:00:00+00:00", ["s"]),
            "t": Commit("t", "target", "alice", "2026-01-03T00:00:00+00:00", ["a", "b"]),
        }
        self.assertEqual(self.repo.path("s", "t"), ["s", "a", "t"])

    def test_ancestors_returns_all_unique_parents(self) -> None:
        self.repo.commits = {
            "r": Commit("r", "root", "alice", "2026-01-01T00:00:00+00:00", []),
            "a": Commit("a", "a", "alice", "2026-01-02T00:00:00+00:00", ["r"]),
            "b": Commit("b", "b", "alice", "2026-01-02T00:00:00+00:00", ["r"]),
            "m": Commit("m", "merge-like", "alice", "2026-01-03T00:00:00+00:00", ["a", "b"]),
        }
        self.assertEqual(self.repo.ancestors("m"), ["a", "b", "r"])

    def test_inverted_index_keyword_author_case_and_duplicate_token(self) -> None:
        first = self.repo.commit("Login login LOGIN")
        second = self.repo.commit("Fix login validation")
        self.repo.commit("Document profile")

        keyword = [commit.hash for commit in self.repo.search_keyword("LOGIN")]
        author = [commit.hash for commit in self.repo.search_author("ALICE")]
        self.assertEqual(keyword, [first.hash, second.hash])
        self.assertEqual(len(author), 3)

    def test_unknown_branch_commit_and_duplicate_branch(self) -> None:
        self.repo.branch("feature")
        with self.assertRaises(MiniGitError):
            self.repo.branch("feature")
        with self.assertRaises(MiniGitError):
            self.repo.switch("missing")
        with self.assertRaises(MiniGitError):
            self.repo.path("c999999", "c888888")


class SortingTests(unittest.TestCase):
    def test_stable_merge_sort_keeps_equal_key_order(self) -> None:
        commits = [
            Commit("c3", "m3", "bob", "2026-01-03T00:00:00+00:00", []),
            Commit("c2", "m2", "alice", "2026-01-02T00:00:00+00:00", []),
            Commit("c1", "m1", "alice", "2026-01-01T00:00:00+00:00", []),
        ]
        by_author = stable_merge_sort(commits, key=lambda commit: commit.author)
        self.assertEqual([commit.hash for commit in by_author], ["c2", "c1", "c3"])
        by_date = stable_merge_sort(commits, key=lambda commit: commit.timestamp)
        self.assertEqual([commit.hash for commit in by_date], ["c1", "c2", "c3"])

    def test_repository_sort_date_and_author(self) -> None:
        self.repo = MiniGitRepository()
        self.repo.init("bob")
        first = self.repo.commit("one")
        self.repo.current_user = "alice"
        second = self.repo.commit("two")
        by_author = self.repo.log_sorted("author")
        self.assertEqual([item.hash for item in by_author], [second.hash, first.hash])
        by_date = self.repo.log_sorted("date")
        self.assertEqual([item.hash for item in by_date], [first.hash, second.hash])
        with self.assertRaises(MiniGitError):
            self.repo.log_sorted("message")


class CliTests(unittest.TestCase):
    def test_commands_case_insensitive_and_quoted_strings(self) -> None:
        repo = MiniGitRepository()
        self.assertIn("Initialized", execute(repo, 'init "Alice Kim"'))
        first = execute(repo, 'commit "Add login feature"')
        self.assertIn("c000001", first)
        self.assertIn("Add login feature", execute(repo, "SEARCH LOGIN"))
        self.assertIn("Alice Kim", execute(repo, 'SEARCH --author="Alice Kim"'))
        self.assertIn("c000001", execute(repo, "log"))
        self.assertIn("c000001", execute(repo, "LOG --sort-by=date"))
        self.assertIn("c000001", execute(repo, "LOG --sort-by=author"))

    def test_cli_path_ancestors_and_no_path(self) -> None:
        repo = MiniGitRepository()
        execute(repo, "INIT alice")
        execute(repo, "BRANCH other")
        execute(repo, 'COMMIT "main root"')
        execute(repo, "SWITCH other")
        execute(repo, 'COMMIT "other root"')
        self.assertEqual(execute(repo, "PATH c000001 c000002"), "No path")
        self.assertEqual(execute(repo, "ANCESTORS c000002"), "(empty)")

    def test_errors(self) -> None:
        repo = MiniGitRepository()
        self.assertEqual(execute(repo, "COMMIT"), "Invalid args")
        self.assertEqual(execute(repo, "HELLO"), "Unknown command: HELLO")
        self.assertEqual(execute(repo, "INIT alice"), "Initialized repository for alice on main")
        self.assertEqual(execute(repo, "SWITCH missing"), "Unknown branch: missing")
        self.assertEqual(execute(repo, "PATH c999999 c000001"), "Unknown commit: c999999")
        self.assertEqual(execute(repo, "LOG --sort-by=message"), "Invalid args")
        self.assertEqual(execute(repo, "SEARCH"), "Invalid args")
        self.assertEqual(execute(repo, 'COMMIT "unterminated'), "Invalid args")


if __name__ == "__main__":
    unittest.main()
