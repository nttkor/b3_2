"""저장소 명령 테스트. 명세의 기능 요구 항목 순서대로 구성."""

import unittest

from minigit.errors import (
    AmbiguousCommitError,
    DuplicateBranchError,
    InvalidArgsError,
    NotInitializedError,
    UnknownBranchError,
    UnknownCommitError,
)
from minigit.repository import Repository

from .helpers import (
    FakeClock,
    FixedClock,
    build_diamond,
    build_two_roots,
    new_repo,
)


class InitTests(unittest.TestCase):
    def test_creates_main_branch_and_sets_head(self):
        repo = new_repo("Alice")
        self.assertEqual(repo.current_branch, "main")
        self.assertEqual(repo.branches, {"main": None})

    def test_sets_current_user(self):
        self.assertEqual(new_repo("Alice").current_user, "Alice")

    def test_starts_with_no_commits(self):
        self.assertEqual(new_repo().commits, {})

    def test_empty_user_name_rejected(self):
        with self.assertRaises(InvalidArgsError):
            Repository().init("   ")

    def test_reinit_clears_previous_state(self):
        repo = new_repo("Alice")
        repo.commit("first")
        repo.branch("feature")
        repo.init("Bob")
        self.assertEqual(repo.commits, {})
        self.assertEqual(repo.branches, {"main": None})
        self.assertEqual(repo.current_user, "Bob")

    def test_commands_before_init_are_rejected(self):
        for action in (
            lambda r: r.commit("x"),
            lambda r: r.branch("feature"),
            lambda r: r.switch("main"),
        ):
            with self.subTest(action=action):
                with self.assertRaises(NotInitializedError):
                    action(Repository())


class BranchTests(unittest.TestCase):
    def test_new_branch_points_to_current_head(self):
        repo = new_repo()
        first = repo.commit("first")
        repo.branch("feature")
        self.assertEqual(repo.branches["feature"], first.hash)

    def test_branch_before_any_commit_has_no_head(self):
        repo = new_repo()
        repo.branch("feature")
        self.assertIsNone(repo.branches["feature"])

    def test_creating_branch_does_not_switch(self):
        repo = new_repo()
        repo.branch("feature")
        self.assertEqual(repo.current_branch, "main")

    def test_duplicate_branch_rejected(self):
        repo = new_repo()
        repo.branch("feature")
        with self.assertRaises(DuplicateBranchError):
            repo.branch("feature")

    def test_error_message_format(self):
        repo = new_repo()
        with self.assertRaises(DuplicateBranchError) as ctx:
            repo.branch("main")
        self.assertEqual(str(ctx.exception), "Branch already exists: main")


class SwitchTests(unittest.TestCase):
    def test_switch_moves_head(self):
        repo = new_repo()
        repo.branch("feature")
        repo.switch("feature")
        self.assertEqual(repo.current_branch, "feature")

    def test_unknown_branch_rejected(self):
        with self.assertRaises(UnknownBranchError):
            new_repo().switch("nope")

    def test_error_message_format(self):
        with self.assertRaises(UnknownBranchError) as ctx:
            new_repo().switch("nope")
        self.assertEqual(str(ctx.exception), "Unknown branch: nope")


class CommitTests(unittest.TestCase):
    def test_first_commit_has_no_parent(self):
        self.assertEqual(new_repo().commit("first").parents, ())

    def test_second_commit_points_to_first(self):
        repo = new_repo()
        first = repo.commit("first")
        second = repo.commit("second")
        self.assertEqual(second.parents, (first.hash,))

    def test_head_advances(self):
        repo = new_repo()
        repo.commit("first")
        second = repo.commit("second")
        self.assertEqual(repo.branches["main"], second.hash)

    def test_branches_diverge_independently(self):
        repo = new_repo()
        root = repo.commit("root")
        repo.branch("feature")
        on_main = repo.commit("on main")
        repo.switch("feature")
        on_feature = repo.commit("on feature")
        self.assertEqual(on_main.parents, (root.hash,))
        self.assertEqual(on_feature.parents, (root.hash,))
        self.assertEqual(repo.branches["main"], on_main.hash)
        self.assertEqual(repo.branches["feature"], on_feature.hash)

    def test_commit_records_current_author(self):
        repo = new_repo("Alice")
        first = repo.commit("first")
        repo.set_user("Bob")
        second = repo.commit("second")
        self.assertEqual((first.author, second.author), ("Alice", "Bob"))

    def test_sequence_increments(self):
        repo = new_repo()
        sequences = [repo.commit(f"c{i}").sequence for i in range(5)]
        self.assertEqual(sequences, [0, 1, 2, 3, 4])

    def test_hashes_are_unique(self):
        repo = new_repo()
        hashes = [repo.commit(f"c{i}").hash for i in range(500)]
        self.assertEqual(len(set(hashes)), 500)

    def test_sequence_alone_guarantees_hash_uniqueness(self):
        """해시 입력의 모든 필드가 같아도 sequence 덕분에 해시가 갈린다.

        message/author/timestamp/parents 를 전부 일치시킨 뒤에도 해시가
        달라야 한다. 두 브랜치가 같은 부모에서 같은 메시지로 갈라지는
        상황이 실제로 이 조건을 만든다.
        """
        repo = Repository(clock=FixedClock())
        repo.init("Alice")
        root = repo.commit("root")
        repo.branch("feature")
        on_main = repo.commit("same message")
        repo.switch("feature")
        on_feature = repo.commit("same message")

        # 해시 입력 중 sequence 를 뺀 나머지가 완전히 동일함을 먼저 확인한다.
        self.assertEqual(on_main.message, on_feature.message)
        self.assertEqual(on_main.author, on_feature.author)
        self.assertEqual(on_main.timestamp, on_feature.timestamp)
        self.assertEqual(on_main.parents, on_feature.parents, (root.hash,))
        self.assertNotEqual(on_main.sequence, on_feature.sequence)

        self.assertNotEqual(on_main.hash, on_feature.hash)

    def test_empty_message_rejected(self):
        with self.assertRaises(InvalidArgsError):
            new_repo().commit("   ")

    def test_commit_updates_inverted_index(self):
        repo = new_repo("Alice")
        commit = repo.commit("Add login feature")
        self.assertEqual(repo.index.find_by_keyword("login"), {commit.hash})
        self.assertEqual(repo.index.find_by_author("Alice"), {commit.hash})

    def test_commit_is_immutable(self):
        commit = new_repo().commit("first")
        with self.assertRaises(Exception):
            commit.message = "changed"  # type: ignore[misc]


class LogTests(unittest.TestCase):
    def setUp(self):
        self.repo, self.hashes = build_diamond()

    def test_parent_always_precedes_child(self):
        order = [c.hash for c in self.repo.log()]
        self.assertTrue(Repository.is_parent_first(self.repo.log()))
        # A 는 맨 앞, M(merge)은 맨 뒤여야 한다.
        self.assertEqual(order[0], self.hashes["A"])
        self.assertEqual(order[-1], self.hashes["M"])

    def test_includes_every_commit_exactly_once(self):
        order = [c.hash for c in self.repo.log()]
        self.assertEqual(len(order), 4)
        self.assertEqual(set(order), set(self.hashes.values()))

    def test_is_deterministic_across_calls(self):
        self.assertEqual(
            [c.hash for c in self.repo.log()], [c.hash for c in self.repo.log()]
        )

    def test_empty_repository(self):
        self.assertEqual(new_repo().log(), [])

    def test_sort_by_date_is_ascending(self):
        commits = self.repo.log("date")
        stamps = [c.timestamp for c in commits]
        self.assertEqual(stamps, sorted(stamps))

    def test_sort_by_author_is_alphabetical(self):
        repo = new_repo("Zoe")
        repo.commit("root")
        repo.set_user("Alice")
        repo.commit("second")
        repo.set_user("Bob")
        repo.commit("third")
        authors = [c.author for c in repo.log("author")]
        self.assertEqual(authors, ["Alice", "Bob", "Zoe"])

    def test_sort_by_author_may_break_parent_first(self):
        """정렬 기준이 그래프 구조와 무관하면 위상 제약이 깨진다.

        LOG 가 단순 정렬이 아니라 위상 정렬이어야 하는 이유의 실증.
        """
        repo = new_repo("Zoe")
        repo.commit("root")
        repo.set_user("Alice")
        repo.commit("child")
        self.assertFalse(Repository.is_parent_first(repo.log("author")))
        self.assertTrue(Repository.is_parent_first(repo.log()))

    def test_sort_by_date_happens_to_keep_parent_first(self):
        """부모가 항상 먼저 생성되므로 날짜순은 우연히 위상 순서와 일치한다."""
        self.assertTrue(Repository.is_parent_first(self.repo.log("date")))

    def test_unknown_sort_key_rejected(self):
        with self.assertRaises(InvalidArgsError):
            self.repo.log("size")


class PathTests(unittest.TestCase):
    def setUp(self):
        self.repo, self.hashes = build_diamond()

    def test_same_commit(self):
        target = self.hashes["A"]
        self.assertEqual(self.repo.path(target, target), [target])

    def test_parent_to_child(self):
        self.assertEqual(
            self.repo.path(self.hashes["A"], self.hashes["B"]),
            [self.hashes["A"], self.hashes["B"]],
        )

    def test_child_to_parent_is_symmetric(self):
        """간선을 무방향으로 보므로 역방향도 같은 길이여야 한다."""
        forward = self.repo.path(self.hashes["A"], self.hashes["M"])
        backward = self.repo.path(self.hashes["M"], self.hashes["A"])
        self.assertEqual(len(forward), len(backward))
        self.assertEqual(forward, list(reversed(backward)))

    def test_sibling_branches_route_through_common_ancestor(self):
        """B 와 C 는 직접 연결이 없다. A 또는 M 을 거쳐야 한다."""
        path = self.repo.path(self.hashes["B"], self.hashes["C"])
        self.assertEqual(len(path), 3)
        self.assertIn(path[1], (self.hashes["A"], self.hashes["M"]))

    def test_picks_lexicographically_smallest_when_tied(self):
        """B->C 최단 경로는 A 경유와 M 경유 두 가지. 사전순 최소를 골라야 한다."""
        path = self.repo.path(self.hashes["B"], self.hashes["C"])
        expected_middle = min(self.hashes["A"], self.hashes["M"])
        self.assertEqual(path[1], expected_middle)

    def test_no_path_between_disconnected_roots(self):
        repo, hashes = build_two_roots()
        self.assertIsNone(repo.path(hashes["R1"], hashes["R2"]))

    def test_unknown_commit_rejected(self):
        with self.assertRaises(UnknownCommitError):
            self.repo.path("deadbeef", self.hashes["A"])


class AncestorsTests(unittest.TestCase):
    def setUp(self):
        self.repo, self.hashes = build_diamond()

    def test_merge_commit_reaches_everything(self):
        result = {c.hash for c in self.repo.ancestors(self.hashes["M"])}
        self.assertEqual(result, {self.hashes["A"], self.hashes["B"], self.hashes["C"]})

    def test_shared_ancestor_listed_once(self):
        hashes = [c.hash for c in self.repo.ancestors(self.hashes["M"])]
        self.assertEqual(hashes.count(self.hashes["A"]), 1)

    def test_root_has_no_ancestors(self):
        self.assertEqual(self.repo.ancestors(self.hashes["A"]), [])

    def test_excludes_self(self):
        hashes = [c.hash for c in self.repo.ancestors(self.hashes["M"])]
        self.assertNotIn(self.hashes["M"], hashes)

    def test_ordered_newest_first(self):
        sequences = [c.sequence for c in self.repo.ancestors(self.hashes["M"])]
        self.assertEqual(sequences, sorted(sequences, reverse=True))

    def test_unknown_commit_rejected(self):
        with self.assertRaises(UnknownCommitError):
            self.repo.ancestors("deadbeef")


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.repo = new_repo("Alice")
        self.login = self.repo.commit("Add login feature")
        self.repo.set_user("Bob")
        self.bug = self.repo.commit("Fix login bug.")
        self.repo.set_user("Alice")
        self.payment = self.repo.commit("Add payment feature")

    def test_keyword_matches_multiple_commits(self):
        found = [c.hash for c in self.repo.search_keyword("login")]
        self.assertEqual(found, [self.login.hash, self.bug.hash])

    def test_keyword_is_case_insensitive(self):
        self.assertEqual(
            [c.hash for c in self.repo.search_keyword("LOGIN")],
            [self.login.hash, self.bug.hash],
        )

    def test_keyword_ignores_trailing_punctuation(self):
        self.assertEqual([c.hash for c in self.repo.search_keyword("bug")], [self.bug.hash])

    def test_partial_word_does_not_match(self):
        """토큰 단위 검색이므로 'log' 는 'login' 에 걸리지 않는다."""
        self.assertEqual(self.repo.search_keyword("log"), [])

    def test_no_match_returns_empty(self):
        self.assertEqual(self.repo.search_keyword("nonexistent"), [])

    def test_author_search(self):
        found = [c.hash for c in self.repo.search_author("Alice")]
        self.assertEqual(found, [self.login.hash, self.payment.hash])

    def test_author_search_is_case_insensitive(self):
        self.assertEqual(len(self.repo.search_author("ALICE")), 2)

    def test_results_are_in_commit_order(self):
        sequences = [c.sequence for c in self.repo.search_keyword("add")]
        self.assertEqual(sequences, sorted(sequences))

    def test_results_are_deterministic(self):
        """내부 인덱스가 set 이지만 출력 순서는 매번 같아야 한다."""
        first = [c.hash for c in self.repo.search_author("Alice")]
        for _ in range(20):
            self.assertEqual([c.hash for c in self.repo.search_author("Alice")], first)

    def test_many_results_follow_commit_order_exactly(self):
        """결과가 많아도 정확히 생성 순서여야 한다.

        set 을 그대로 순회하면 해시값에 따른 임의 순서가 나오므로,
        커밋 수를 충분히 늘리면 정렬 누락이 반드시 드러난다.
        """
        repo = new_repo("Alice")
        expected = [repo.commit(f"shared token number {i}").hash for i in range(30)]
        self.assertEqual([c.hash for c in repo.search_keyword("shared")], expected)
        self.assertEqual([c.hash for c in repo.search_author("Alice")], expected)

    def test_ancestors_order_is_exact_for_long_chain(self):
        """조상 목록도 set 순회가 아니라 정해진 순서여야 한다."""
        repo = new_repo("Alice")
        chain = [repo.commit(f"c{i}") for i in range(30)]
        result = [c.hash for c in repo.ancestors(chain[-1].hash)]
        self.assertEqual(result, [c.hash for c in reversed(chain[:-1])])


class MergeTests(unittest.TestCase):
    def test_merge_commit_has_two_parents(self):
        repo, hashes = build_diamond()
        merge_commit = repo.commits[hashes["M"]]
        self.assertEqual(set(merge_commit.parents), {hashes["B"], hashes["C"]})
        self.assertTrue(merge_commit.is_merge)

    def test_merge_advances_current_branch_only(self):
        repo, hashes = build_diamond()
        self.assertEqual(repo.branches["main"], hashes["M"])
        self.assertEqual(repo.branches["feature"], hashes["C"])

    def test_already_up_to_date(self):
        repo = new_repo()
        repo.commit("root")
        repo.branch("feature")
        kind, commit = repo.merge("feature")
        self.assertEqual(kind, "up-to-date")
        self.assertIsNone(commit)

    def test_fast_forward_when_current_is_ancestor(self):
        repo = new_repo()
        repo.commit("root")
        repo.branch("feature")
        repo.switch("feature")
        ahead = repo.commit("ahead")
        repo.switch("main")
        kind, commit = repo.merge("feature")
        self.assertEqual(kind, "fast-forward")
        self.assertIsNone(commit)
        self.assertEqual(repo.branches["main"], ahead.hash)

    def test_merging_self_rejected(self):
        repo = new_repo()
        repo.commit("root")
        with self.assertRaises(InvalidArgsError):
            repo.merge("main")

    def test_unknown_branch_rejected(self):
        with self.assertRaises(UnknownBranchError):
            new_repo().merge("nope")

    def test_graph_stays_acyclic_after_merge(self):
        repo, _ = build_diamond()
        repo.log()  # 사이클이 있으면 CycleError 로 실패한다


class ResolveTests(unittest.TestCase):
    def test_full_hash(self):
        repo = new_repo()
        commit = repo.commit("first")
        self.assertEqual(repo.resolve(commit.hash), commit.hash)

    def test_short_hash_prefix(self):
        repo = new_repo()
        commit = repo.commit("first")
        self.assertEqual(repo.resolve(commit.short_hash), commit.hash)

    def test_prefix_is_case_insensitive(self):
        repo = new_repo()
        commit = repo.commit("first")
        self.assertEqual(repo.resolve(commit.short_hash.upper()), commit.hash)

    def test_unknown_prefix_rejected(self):
        with self.assertRaises(UnknownCommitError):
            new_repo().resolve("zzzzzz")

    def test_ambiguous_prefix_rejected(self):
        repo = new_repo()
        for i in range(300):
            repo.commit(f"c{i}")
        first_chars = {h[0] for h in repo.commits}
        ambiguous = next(
            c for c in first_chars if sum(h.startswith(c) for h in repo.commits) > 1
        )
        with self.assertRaises(AmbiguousCommitError):
            repo.resolve(ambiguous)


class DeterminismTests(unittest.TestCase):
    """같은 시나리오를 두 번 실행하면 완전히 같은 결과가 나와야 한다."""

    @staticmethod
    def run_scenario() -> dict:
        repo, hashes = build_diamond()
        return {
            "hashes": hashes,
            "log": [c.hash for c in repo.log()],
            "log_date": [c.hash for c in repo.log("date")],
            "log_author": [c.hash for c in repo.log("author")],
            "path": repo.path(hashes["B"], hashes["C"]),
            "ancestors": [c.hash for c in repo.ancestors(hashes["M"])],
            "search": [c.hash for c in repo.search_keyword("root")],
        }

    def test_two_runs_produce_identical_output(self):
        self.assertEqual(self.run_scenario(), self.run_scenario())

    def test_branch_labels(self):
        repo, hashes = build_diamond()
        self.assertEqual(
            repo.branch_labels(), {hashes["M"]: ["main"], hashes["C"]: ["feature"]}
        )


if __name__ == "__main__":
    unittest.main()