"""역색인(Inverted Index).

순회 검색과의 차이:
    - 순회: 커밋 N개, 메시지 평균 토큰 M개 -> 매 검색마다 O(N * M)
    - 역색인: 미리 만들어둔 해시맵 조회 -> O(1) + 결과 수 K
    즉 "검색 시점의 비용을 커밋 시점으로 옮긴" 것이다.
    커밋 1회당 색인 비용은 O(M)이고, 검색은 사실상 상수 시간이 된다.
    저장 공간을 시간과 교환하는 전형적인 space-time trade-off.
"""

from .models import Commit

PUNCTUATION = ".,!?:;()[]{}\"'`<>"


class InvertedIndex:
    """keyword -> 커밋 해시 집합, author -> 커밋 해시 집합 두 종류를 관리한다."""

    def __init__(self) -> None:
        self.keyword_to_hashes: dict[str, set[str]] = {}
        self.author_to_hashes: dict[str, set[str]] = {}

    @staticmethod
    def tokenize(text: str) -> list[str]:
        """메시지를 검색 키워드로 정규화한다.

        최소 기준(공백 split + 소문자화)에 더해 양끝 구두점을 제거한다.
        'Add login feature.' 로 커밋했을 때 'feature' 검색이 실패하는
        문제를 막기 위해서다.
        """
        tokens: list[str] = []
        for raw in text.lower().split():
            token = raw.strip(PUNCTUATION)
            if token:
                tokens.append(token)
        return tokens

    def add(self, commit: Commit) -> None:
        """커밋 하나를 두 인덱스에 모두 등록한다. O(M)."""
        for token in self.tokenize(commit.message):
            self.keyword_to_hashes.setdefault(token, set()).add(commit.hash)

        author_key = commit.author.lower()
        self.author_to_hashes.setdefault(author_key, set()).add(commit.hash)

    def find_by_keyword(self, keyword: str) -> set[str]:
        """키워드를 포함한 커밋 해시들. 조회 자체는 O(1)."""
        key = keyword.lower().strip(PUNCTUATION)
        return set(self.keyword_to_hashes.get(key, set()))

    def find_by_author(self, author: str) -> set[str]:
        """작성자의 커밋 해시들. 조회 자체는 O(1)."""
        return set(self.author_to_hashes.get(author.lower(), set()))

    def clear(self) -> None:
        """두 인덱스를 모두 비운다. 저장소 재초기화에 쓴다."""
        self.keyword_to_hashes = {}
        self.author_to_hashes = {}

    def stats(self) -> tuple[int, int]:
        """(키워드 종류 수, 작성자 수)."""
        return len(self.keyword_to_hashes), len(self.author_to_hashes)