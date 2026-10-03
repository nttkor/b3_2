"""정렬 알고리즘 직접 구현 모듈.

제약: 표준 정렬 API(sorted(), list.sort())를 일절 사용하지 않는다.

이 프로젝트에서 정렬의 역할은 두 가지다.
  1) 사용자가 요청한 표시 순서 (LOG --sort-by=date|author)
  2) **결정성 확보** - dict/set 순회 순서나 위상 정렬의 후보 동률처럼
     "정답이 여러 개인 지점"에서 항상 같은 답을 고르게 만드는 tie-break
2번이 이 과제에서 정렬이 갖는 진짜 의미다.
"""

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")

Key = Callable[[T], object]


def _identity(value: T) -> object:
    return value


def merge_sort(values: Iterable[T], key: Key | None = None) -> list[T]:
    """병합 정렬.

    시간복잡도: 최선/평균/최악 모두 O(n log n).
        입력 분포와 무관하게 항상 절반으로 쪼개므로 최악이 없다.
    공간복잡도: O(n) (병합용 임시 배열).
    안정성: 안정(stable). _merge()에서 동률일 때 왼쪽을 먼저 취하기 때문.
        LOG --sort-by=author처럼 동일 작성자가 여러 명일 때,
        원래 순서(= 위상 순서)가 보존되는 것이 이 성질 덕분이다.

    Args:
        values: 정렬할 값들.
        key: 비교 기준 추출 함수. None이면 값 자체로 비교한다.
            이 인자 하나로 "비교 기준을 바꿔 정렬"하는 요구사항을 만족한다.

    Returns:
        정렬된 새 리스트 (입력을 변경하지 않는다).
    """
    items = list(values)
    if key is None:
        key = _identity

    if len(items) <= 1:
        return items

    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    return _merge(left, right, key)


def _merge(left: list[T], right: list[T], key: Key) -> list[T]:
    """정렬된 두 리스트를 안정적으로 병합한다."""
    result: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        # '<=' 가 안정성의 핵심. '<' 로 바꾸면 동률에서 오른쪽이 먼저 나가
        # 원래 순서가 뒤집히며 불안정 정렬이 된다.
        if key(left[left_index]) <= key(right[right_index]):
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])
    return result


def insertion_sort(values: Iterable[T], key: Key | None = None) -> list[T]:
    """삽입 정렬. (보너스: 정렬 알고리즘 성능 비교용)

    시간복잡도: 최선 O(n) (이미 정렬된 입력), 평균/최악 O(n^2).
    공간복잡도: O(1) 추가 공간 (제자리 정렬).
    안정성: 안정. 동률이면 이동을 멈추므로 순서가 유지된다.

    merge_sort와 달리 입력 분포에 민감하다는 점이 비교 실험의 관전 포인트다.
    """
    items = list(values)
    if key is None:
        key = _identity

    for i in range(1, len(items)):
        current = items[i]
        current_key = key(current)
        j = i - 1
        while j >= 0 and key(items[j]) > current_key:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = current

    return items


def min_by(values: Iterable[T], key: Key | None = None) -> T | None:
    """전체 정렬 없이 최솟값 하나만 O(n)에 고른다.

    최단 경로에서 "다음 후보 중 사전순 최소"를 고를 때처럼,
    정렬 결과 전체가 아니라 첫 원소만 필요한 경우에 사용한다.
    """
    if key is None:
        key = _identity

    best: T | None = None
    best_key: object = None
    for value in values:
        value_key = key(value)
        if best is None or value_key < best_key:  # type: ignore[operator]
            best = value
            best_key = value_key
    return best


class MinHeap:
    """이진 최소 힙. (표준 heapq를 쓰지 않고 직접 구현)

    push/pop 모두 O(log n). 위상 정렬에서 "진입차수 0인 후보들 중
    tie-break 기준상 최소"를 반복해서 꺼내야 하는데, 후보 리스트를
    매번 재정렬하면 O(V^2 log V)가 된다. 힙을 쓰면 O((V+E) log V)다.
    """

    def __init__(self, key: Key | None = None) -> None:
        self._key: Key = key if key is not None else _identity
        self._items: list = []

    def __len__(self) -> int:
        return len(self._items)

    def push(self, item) -> None:
        """원소를 넣고 힙 속성을 복구한다. O(log n)."""
        self._items.append(item)
        self._sift_up(len(self._items) - 1)

    def pop(self):
        """key 기준 최솟값을 꺼낸다. O(log n). 비어 있으면 IndexError."""
        if not self._items:
            raise IndexError("pop from empty heap")

        top = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._key(self._items[index]) < self._key(self._items[parent]):
                self._swap(index, parent)
                index = parent
            else:
                break

    def _sift_down(self, index: int) -> None:
        size = len(self._items)
        while True:
            left = 2 * index + 1
            right = left + 1
            smallest = index

            if left < size and self._key(self._items[left]) < self._key(self._items[smallest]):
                smallest = left
            if right < size and self._key(self._items[right]) < self._key(self._items[smallest]):
                smallest = right
            if smallest == index:
                break

            self._swap(index, smallest)
            index = smallest

    def _swap(self, a: int, b: int) -> None:
        self._items[a], self._items[b] = self._items[b], self._items[a]