"""저장소 상태와 명령. graph / index / sorting 모듈을 조합하는 계층."""

import hashlib
from datetime import datetime
from typing import Callable

from . import graph
from .errors import (
    AmbiguousCommitError,
    DuplicateBranchError,
    InvalidArgsError,
    NotInitializedError,
    UnknownBranchError,
    UnknownCommitError,
)
from .index import InvertedIndex
from .models import Commit
from .sorting import merge_sort

VALID_SORT_KEYS = ("date", "author")


class Repository:
    """커밋 DAG + 브랜치 + 역색인을 보유한 인메모리 저장소.

    자료구조:
        commits:  hash -> Commit   (해시맵. 해시 조회 O(1))
        children: hash -> set[hash] (역방향 인접 리스트)
        branches: 브랜치명 -> head hash | None

    children를 커밋 시점에 함께 갱신하는 이유:
        PATH는 부모/자식 간선을 '무방향'으로 봐야 한다. Commit.parents만
        있으면 자식을 찾으려고 매번 전체 커밋을 훑어야 해서 O(V+E)가
        추가로 든다. 역방향 인덱스를 유지하면 이웃 조회가 O(1)이다.
    """

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        """
        Args:
            clock: 현재 시각을 돌려주는 함수. 기본값은 datetime.now.
                테스트에서 가짜 시계를 주입해 타임스탬프와 커밋 해시를
                결정적으로 만들기 위한 주입 지점이다. 시간을 직접 호출하면
                같은 시나리오라도 매번 다른 해시가 나와 결과값을 검증할 수 없다.
        """
        self._clock: Callable[[], datetime] = clock if clock is not None else datetime.now
        self.commits: dict[str, Commit] = {}
        self.children: dict[str, set[str]] = {}
        self.branches: dict[str, str | None] = {}
        self.current_branch: str | None = None
        self.current_user: str | None = None
        self.index = InvertedIndex()
        self._next_sequence = 0

    # ------------------------------------------------------------------
    # 저장소 / 브랜치
    # ------------------------------------------------------------------

    def init(self, user_name: str) -> None:
        """저장소를 초기화하고 main 브랜치와 HEAD, 현재 사용자를 설정한다."""
        if not user_name.strip():
            raise InvalidArgsError("user name must not be empty")

        self.commits = {}
        self.children = {}
        self.branches = {"main": None}
        self.current_branch = "main"
        self.current_user = user_name
        self.index = InvertedIndex()
        self._next_sequence = 0

    def set_user(self, user_name: str) -> None:
        """현재 작성자를 바꾼다.

        명세에는 없는 확장이다. INIT이 작성자를 한 번만 정하면 세션 내
        작성자가 항상 하나뿐이라 SEARCH --author와 LOG --sort-by=author가
        의미를 잃는다. 두 기능을 실제로 검증하기 위해 추가했다.
        """
        self._require_initialized()
        if not user_name.strip():
            raise InvalidArgsError("user name must not be empty")
        self.current_user = user_name

    def branch(self, name: str) -> None:
        """현재 HEAD를 가리키는 새 브랜치를 만든다."""
        current_branch, _ = self._require_initialized()
        if not name.strip():
            raise InvalidArgsError("branch name must not be empty")
        if name in self.branches:
            raise DuplicateBranchError(name)

        self.branches[name] = self.branches[current_branch]

    def switch(self, name: str) -> None:
        """HEAD를 지정한 브랜치로 옮긴다."""
        self._require_initialized()
        if name not in self.branches:
            raise UnknownBranchError(name)

        self.current_branch = name

    # ------------------------------------------------------------------
    # 커밋
    # ------------------------------------------------------------------

    def commit(self, message: str) -> Commit:
        """현재 HEAD를 부모로 하는 새 커밋을 만든다."""
        current_branch, _ = self._require_initialized()
        if not message.strip():
            raise InvalidArgsError("commit message must not be empty")

        head = self.branches[current_branch] 
        parents: tuple[str, ...] = () if head is None else (head,)
        return self._create_and_store(message, parents)

    def merge(self, branch_name: str) -> tuple[str, Commit | None]:
        """보너스: 대상 브랜치를 현재 브랜치로 병합한다.

        Returns:
            ("up-to-date" | "fast-forward" | "merge", 생성된 커밋 또는 None)
        """
        current_branch, _ = self._require_initialized()
        if branch_name not in self.branches:
            raise UnknownBranchError(branch_name)
        if branch_name == current_branch:
            raise InvalidArgsError("cannot merge a branch into itself")

        head = self.branches[current_branch]
        other = self.branches[branch_name]

        if other is None:
            return "up-to-date", None
        if head is None:
            self.branches[current_branch] = other
            return "fast-forward", None
        if head == other or other in self._ancestor_hashes(head):
            # 대상이 이미 내 조상 -> 병합할 게 없다
            return "up-to-date", None
        if head in self._ancestor_hashes(other):
            # 내가 대상의 조상 -> 포인터만 앞으로 (fast-forward)
            self.branches[current_branch] = other
            return "fast-forward", None

        message = f"Merge branch '{branch_name}' into {current_branch}"
        commit = self._create_and_store(message, (head, other))
        return "merge", commit

    def _create_and_store(
        self, message: str, parents: tuple[str, ...]
    ) -> Commit:
        """커밋을 만들어 그래프/브랜치/역색인에 모두 반영한다."""
        assert self.current_branch is not None
        assert self.current_user is not None

        timestamp = self._clock()
        sequence = self._next_sequence
        commit_hash = self._generate_hash(
            self._build_hash_source(
                message=message,
                author=self.current_user,
                timestamp=timestamp,
                parents=parents,
                sequence=sequence,
            )
        )

        new_commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.current_user,
            timestamp=timestamp,
            parents=parents,
            sequence=sequence,
        )

        self.commits[commit_hash] = new_commit
        self.children[commit_hash] = set()
        for parent_hash in parents:
            self.children[parent_hash].add(commit_hash)

        self.branches[self.current_branch] = commit_hash
        self.index.add(new_commit)
        self._next_sequence += 1

        return new_commit

    # ------------------------------------------------------------------
    # 조회 / 탐색
    # ------------------------------------------------------------------

    def log(self, sort_by: str | None = None) -> list[Commit]:
        """커밋 목록.

        명세상 두 명령은 성격이 다르다.
            LOG               -> 위상 정렬. 부모가 항상 자식보다 먼저.
            LOG --sort-by=... -> 지정한 비교 기준에 의한 전체 정렬.

        즉 --sort-by는 위상 순서 안의 tie-break이 아니라 위상 순서를
        '대체'한다. 이 구분 자체가 학습 포인트다.
        전체 정렬은 전순서(total order)를 만들지만, 커밋 그래프가 요구하는
        건 부분순서(partial order)이므로 정렬 기준이 그래프 구조와 무관하면
        부모가 자식 뒤로 밀릴 수 있다. is_parent_first()로 확인 가능하다.
        """
        if sort_by is None:
            return self._topological_log()
        if sort_by not in VALID_SORT_KEYS:
            raise InvalidArgsError(f"unknown sort key: {sort_by}")
        return self._sorted_log(sort_by)

    def _topological_log(self) -> list[Commit]:
        """부모가 항상 자식보다 먼저 오는 목록.

        진입차수 0인 후보가 여럿일 때(브랜치 분기 지점) 위상 정렬의 답은
        여러 개다. 해시 사전순 tie-break으로 출력을 결정적으로 고정한다.
        """
        order = graph.topological_order(
            nodes=self.commits.keys(),
            parents_of=lambda h: self.commits[h].parents,
            children_of=lambda h: self.children[h],
            tie_break_key=lambda h: h,
        )
        return [self.commits[h] for h in order]

    def _sorted_log(self, sort_by: str) -> list[Commit]:
        """비교 기준을 바꿔 전체 정렬한 목록. 위상 순서를 보장하지 않는다."""
        ordered = merge_sort(
            list(self.commits.keys()), key=self._sort_key(sort_by)
        )
        return [self.commits[h] for h in ordered]

    def _sort_key(self, sort_by: str):
        """비교 기준 추출 함수.

        정렬 로직(merge_sort)은 그대로 두고 이 key만 갈아끼운다.
        동률 처리는 sequence로 확정해 실행마다 같은 결과가 나오게 한다.
        """
        if sort_by == "date":
            return lambda h: (self.commits[h].timestamp, self.commits[h].sequence)
        # author
        return lambda h: (
            self.commits[h].author.lower(),
            self.commits[h].timestamp,
            self.commits[h].sequence,
        )

    @staticmethod
    def is_parent_first(commits: list[Commit]) -> bool:
        """주어진 순서가 '부모가 자식보다 먼저'를 만족하는지 검사한다.

        --sort-by 결과가 위상 제약을 깨는지 사용자에게 알려주는 데 쓴다.
        --sort-by=date는 (부모가 항상 자식보다 먼저 생성되므로) 이 검사를
        통과하지만, --sort-by=author는 그래프 구조와 무관한 기준이라
        일반적으로 통과하지 못한다. 두 옵션이 대칭이 아니라는 점이
        "LOG는 왜 정렬이 아니라 위상 정렬이어야 하는가"의 실물 증거다.
        """
        position = {commit.hash: i for i, commit in enumerate(commits)}
        for commit in commits:
            for parent in commit.parents:
                if parent in position and position[parent] > position[commit.hash]:
                    return False
        return True

    def path(self, start_ref: str, target_ref: str) -> list[str] | None:
        """두 커밋 사이의 최단 경로 (없으면 None)."""
        start = self.resolve(start_ref)
        target = self.resolve(target_ref)
        return graph.smallest_shortest_path(start, target, self._neighbors)

    def ancestors(self, ref: str) -> list[Commit]:
        """해당 커밋의 모든 조상. 가까운(최신) 조상부터 출력한다."""
        commit_hash = self.resolve(ref)
        hashes = graph.ancestors(
            commit_hash, lambda h: self.commits[h].parents
        )
        ordered = merge_sort(hashes, key=lambda h: -self.commits[h].sequence)
        return [self.commits[h] for h in ordered]

    def _ancestor_hashes(self, commit_hash: str) -> set[str]:
        return set(graph.ancestors(commit_hash, lambda h: self.commits[h].parents))

    def _neighbors(self, commit_hash: str) -> list[str]:
        """부모 + 자식. PATH가 간선을 무방향으로 보기 때문에 둘을 합친다.

        정렬하지 않는 이유: BFS 거리 계산은 방문 순서와 무관하고,
        사전순 선택은 경로 복원 단계에서 명시적으로 처리하기 때문이다.
        """
        return list(self.commits[commit_hash].parents) + list(
            self.children[commit_hash]
        )

    # ------------------------------------------------------------------
    # 검색 (역색인)
    # ------------------------------------------------------------------

    def search_keyword(self, keyword: str) -> list[Commit]:
        """메시지에 키워드가 포함된 커밋들. 역색인 조회."""
        return self._to_commits(self.index.find_by_keyword(keyword))

    def search_author(self, author: str) -> list[Commit]:
        """특정 작성자의 커밋들. 역색인 조회."""
        return self._to_commits(self.index.find_by_author(author))

    def _to_commits(self, hashes: set[str]) -> list[Commit]:
        """set은 순회 순서가 보장되지 않으므로 sequence로 정렬해 고정한다."""
        ordered = merge_sort(list(hashes), key=lambda h: self.commits[h].sequence)
        return [self.commits[h] for h in ordered]

    # ------------------------------------------------------------------
    # 유틸
    # ------------------------------------------------------------------

    def resolve(self, ref: str) -> str:
        """전체 해시 또는 접두사(짧은 해시)를 전체 해시로 해석한다."""
        if ref in self.commits:
            return ref

        prefix = ref.lower()
        matches = [h for h in self.commits if h.startswith(prefix)]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise AmbiguousCommitError(ref)
        raise UnknownCommitError(ref)

    def branch_labels(self) -> dict[str, list[str]]:
        """head 해시 -> 그 지점을 가리키는 브랜치 이름들."""
        labels: dict[str, list[str]] = {}
        for name in merge_sort(list(self.branches.keys())):
            head = self.branches[name]
            if head is None:
                continue
            labels.setdefault(head, []).append(name)
        return labels

    def _require_initialized(self) -> tuple[str, str]:
        if self.current_branch is None or self.current_user is None:
            raise NotInitializedError()
        if self.current_branch not in self.branches:
            raise UnknownBranchError(self.current_branch)
        return self.current_branch, self.current_user

    @staticmethod
    def _build_hash_source(
        message: str,
        author: str,
        timestamp: datetime,
        parents: tuple[str, ...],
        sequence: int,
    ) -> str:
        """해시 입력 문자열.

        sequence를 포함시키는 것이 유일성의 핵심이다. 같은 사용자가 같은
        메시지로 같은 순간에 커밋해도 sequence가 다르므로 해시가 갈린다.
        (timestamp만으로는 해상도 한계 때문에 충돌 가능성이 남는다.)
        """
        return (
            f"message:{message}\n"
            f"author:{author}\n"
            f"timestamp:{timestamp.isoformat()}\n"
            f"parents:{','.join(parents)}\n"
            f"sequence:{sequence}"
        )

    @staticmethod
    def _generate_hash(source: str) -> str:
        return hashlib.sha1(source.encode("utf-8")).hexdigest()