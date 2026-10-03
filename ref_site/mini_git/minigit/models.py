"""커밋 노드 정의."""

from dataclasses import dataclass
from datetime import datetime

SHORT_HASH_LENGTH = 7


@dataclass(frozen=True)
class Commit:
    """커밋 그래프의 노드.

    frozen=True + parents를 tuple로 둔 이유:
        Git의 커밋은 '내용이 곧 정체성'인 불변 객체다. 생성 후 필드가
        바뀌면 hash가 내용을 대표하지 못하고, parents가 mutable이면
        런타임에 간선을 추가해 DAG 불변식을 깨뜨릴 수 있다.
        불변으로 강제해 이 두 사고를 타입 수준에서 차단한다.

    Attributes:
        hash: 세션 내 유일한 커밋 식별자 (sha1 hexdigest).
        message: 커밋 메시지.
        author: 작성자 이름.
        timestamp: 생성 시각.
        parents: 부모 커밋 해시들. 0개(최초) / 1개(일반) / 2개(merge).
        sequence: 생성 순번. 해시 유일성 보장과 결정적 정렬에 사용.
    """

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]
    sequence: int

    @property
    def short_hash(self) -> str:
        """사람이 읽기 좋은 축약 해시."""
        return self.hash[:SHORT_HASH_LENGTH]

    @property
    def is_merge(self) -> bool:
        """부모가 2개 이상이면 merge 커밋이다."""
        return len(self.parents) >= 2