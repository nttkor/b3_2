"""역색인 테스트: 토큰화 / 등록 / 조회."""

import unittest
from datetime import datetime

from minigit.index import InvertedIndex
from minigit.models import Commit


def make_commit(hash_value: str, message: str, author: str) -> Commit:
    return Commit(
        hash=hash_value,
        message=message,
        author=author,
        timestamp=datetime(2026, 1, 15, 9, 0, 0),
        parents=(),
        sequence=0,
    )


class TokenizeTests(unittest.TestCase):
    def test_splits_on_whitespace_and_lowercases(self):
        self.assertEqual(
            InvertedIndex.tokenize("Add Login Feature"), ["add", "login", "feature"]
        )

    def test_strips_surrounding_punctuation(self):
        self.assertEqual(
            InvertedIndex.tokenize("Fix bug, (again)!"), ["fix", "bug", "again"]
        )

    def test_keeps_inner_punctuation(self):
        """토큰 내부의 기호는 살린다. 식별자를 쪼개면 검색이 어려워진다."""
        self.assertEqual(InvertedIndex.tokenize("update user_id"), ["update", "user_id"])

    def test_collapses_repeated_whitespace(self):
        self.assertEqual(InvertedIndex.tokenize("a   b\tc"), ["a", "b", "c"])

    def test_empty_and_punctuation_only(self):
        self.assertEqual(InvertedIndex.tokenize(""), [])
        self.assertEqual(InvertedIndex.tokenize("... !!!"), [])


class IndexLookupTests(unittest.TestCase):
    def setUp(self):
        self.index = InvertedIndex()
        self.index.add(make_commit("h1", "Add login feature", "Alice"))
        self.index.add(make_commit("h2", "Fix login bug.", "Bob"))
        self.index.add(make_commit("h3", "Add payment feature", "Alice"))

    def test_keyword_shared_by_multiple_commits(self):
        self.assertEqual(self.index.find_by_keyword("login"), {"h1", "h2"})
        self.assertEqual(self.index.find_by_keyword("feature"), {"h1", "h3"})

    def test_keyword_unique_to_one_commit(self):
        self.assertEqual(self.index.find_by_keyword("payment"), {"h3"})

    def test_keyword_lookup_is_case_insensitive(self):
        self.assertEqual(self.index.find_by_keyword("LOGIN"), {"h1", "h2"})

    def test_trailing_punctuation_indexed_as_bare_word(self):
        """'Fix login bug.' 의 'bug.' 이 'bug' 로 검색되어야 한다."""
        self.assertEqual(self.index.find_by_keyword("bug"), {"h2"})
        self.assertEqual(self.index.find_by_keyword("bug."), {"h2"})

    def test_missing_keyword_returns_empty_set(self):
        self.assertEqual(self.index.find_by_keyword("nonexistent"), set())

    def test_author_lookup(self):
        self.assertEqual(self.index.find_by_author("Alice"), {"h1", "h3"})
        self.assertEqual(self.index.find_by_author("Bob"), {"h2"})

    def test_author_lookup_is_case_insensitive(self):
        self.assertEqual(self.index.find_by_author("ALICE"), {"h1", "h3"})

    def test_missing_author_returns_empty_set(self):
        self.assertEqual(self.index.find_by_author("Carol"), set())

    def test_result_is_a_copy(self):
        """반환값을 변경해도 내부 인덱스가 오염되지 않아야 한다."""
        result = self.index.find_by_keyword("login")
        result.add("bogus")
        self.assertEqual(self.index.find_by_keyword("login"), {"h1", "h2"})

    def test_stats(self):
        keywords, authors = self.index.stats()
        # add, login, feature, fix, bug, payment
        self.assertEqual(keywords, 6)
        self.assertEqual(authors, 2)

    def test_clear(self):
        self.index.clear()
        self.assertEqual(self.index.find_by_keyword("login"), set())
        self.assertEqual(self.index.stats(), (0, 0))


class IndexEquivalenceTests(unittest.TestCase):
    """역색인 결과가 전체 순회 검색 결과와 같아야 한다.

    역색인은 어디까지나 '같은 답을 더 빠르게' 얻는 최적화다.
    답이 달라지면 최적화가 아니라 버그다.
    """

    def test_matches_linear_scan(self):
        commits = [
            make_commit(f"h{i}", message, author)
            for i, (message, author) in enumerate(
                [
                    ("Add login feature", "Alice"),
                    ("Fix login bug.", "Bob"),
                    ("Add payment feature", "Alice"),
                    ("Refactor LOGIN handler", "Carol"),
                    ("Update docs", "Bob"),
                ]
            )
        ]
        index = InvertedIndex()
        for commit in commits:
            index.add(commit)

        for keyword in ("login", "feature", "docs", "missing"):
            linear = {
                c.hash for c in commits if keyword in InvertedIndex.tokenize(c.message)
            }
            with self.subTest(keyword=keyword):
                self.assertEqual(index.find_by_keyword(keyword), linear)

        for author in ("Alice", "Bob", "Carol", "Dave"):
            linear = {c.hash for c in commits if c.author.lower() == author.lower()}
            with self.subTest(author=author):
                self.assertEqual(index.find_by_author(author), linear)


if __name__ == "__main__":
    unittest.main()