"""순수 그래프 알고리즘 모듈.

이 모듈은 Commit이 무엇인지 전혀 모른다. 노드는 그냥 문자열이고,
간선은 parents_of / children_of 콜백으로만 주어진다.

이렇게 분리한 이유:
    - 알고리즘 로직을 저장소 상태에서 독립시켜 단위 테스트가 가능해진다.
    - "Git이 그래프다"가 아니라 "그래프에 Git을 얹었다"는 관계가 코드로 드러난다.
"""

from collections import deque
from typing import Callable, Iterable, Sequence

from .errors import CycleError
from .sorting import MinHeap, min_by

NodeId = str
Neighbors = Callable[[NodeId], Sequence[NodeId]]


def topological_order(
    nodes: Iterable[NodeId],
    parents_of: Neighbors,
    children_of: Neighbors,
    tie_break_key: Callable[[NodeId], object] | None = None,
) -> list[NodeId]:
    """Kahn 알고리즘 기반 위상 정렬. 부모가 항상 자식보다 먼저 나온다.

    동작:
        1. 각 노드의 진입차수 = 부모 수.
        2. 진입차수 0인 노드(= 부모 없는 최초 커밋)를 힙에 넣는다.
        3. 힙에서 하나 꺼내 결과에 붙이고, 그 자식들의 진입차수를 1 줄인다.
        4. 0이 된 자식을 힙에 넣는다. 힙이 빌 때까지 반복.

    tie_break_key:
        진입차수 0인 후보가 동시에 여러 개일 때 위상 정렬의 답은 여러 개다.
        이 키로 최소인 것을 고정 선택해 **출력을 결정적으로** 만든다.
        브랜치가 갈라진 시점부터 후보가 여러 개가 되므로 필수적이다.

    시간복잡도: O((V + E) log V)  (힙 연산 log V)
    공간복잡도: O(V)

    Raises:
        CycleError: 사이클이 있어 모든 노드를 소비하지 못한 경우.
            정상적인 커밋 그래프는 DAG이므로 발생하지 않아야 하며,
            이 검사는 불변식에 대한 안전망이다.
    """
    node_list = list(nodes)
    indegree: dict[NodeId, int] = {
        node: len(parents_of(node)) for node in node_list
    }

    heap = MinHeap(key=tie_break_key)
    for node in node_list:
        if indegree[node] == 0:
            heap.push(node)

    result: list[NodeId] = []
    while len(heap) > 0:
        current = heap.pop()
        result.append(current)

        for child in children_of(current):
            indegree[child] -= 1
            if indegree[child] == 0:
                heap.push(child)

    if len(result) != len(node_list):
        raise CycleError()

    return result


def ancestors(start: NodeId, parents_of: Neighbors) -> list[NodeId]:
    """start에서 부모 방향으로 도달 가능한 모든 노드 (start 자신은 제외).

    재귀가 아니라 반복 BFS를 쓰는 이유:
        커밋 히스토리는 본질적으로 긴 사슬이라 깊이가 수천이 되기 쉽다.
        재귀 DFS는 파이썬 기본 재귀 한계(약 1000)에서 RecursionError가 난다.
        BFS는 부수적으로 '가까운 조상부터' 세대순 결과를 준다.

    시간복잡도: O(V + E) - 각 노드/간선을 최대 1번씩 본다.
    공간복잡도: O(V)
    """
    visited: set[NodeId] = {start}
    queue: deque[NodeId] = deque([start])
    result: list[NodeId] = []

    while queue:
        current = queue.popleft()
        for parent in parents_of(current):
            if parent in visited:
                continue
            visited.add(parent)
            result.append(parent)
            queue.append(parent)

    return result


def bfs_distances(start: NodeId, neighbors_of: Neighbors) -> dict[NodeId, int]:
    """start로부터의 간선 수 기준 최단 거리 테이블.

    간선 가중치가 모두 1이므로 BFS가 곧 최단 거리다.
    결과는 이웃 방문 순서와 무관하므로, 이웃을 미리 정렬할 필요가 없다.

    시간복잡도: O(V + E)
    """
    distance: dict[NodeId, int] = {start: 0}
    queue: deque[NodeId] = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in neighbors_of(current):
            if neighbor in distance:
                continue
            distance[neighbor] = distance[current] + 1
            queue.append(neighbor)

    return distance


def smallest_shortest_path(
    start: NodeId,
    target: NodeId,
    neighbors_of: Neighbors,
) -> list[NodeId] | None:
    """최단 경로 중 사전순으로 가장 작은 경로를 반환한다.

    접근 (거리 테이블 + 탐욕 선택, 2단계):
        1. **target에서** BFS로 거리 테이블을 만든다.
           간선을 무방향으로 보므로 dist(target, x) == dist(x, target)다.
        2. start에서 출발해, 이웃 중 dist가 정확히 1 작은 것들만 남기고
           (이들은 반드시 어떤 최단 경로 위에 있다) 그중 해시가 최소인
           것을 고른다. target에 닿을 때까지 반복한다.

    탐욕 선택이 정당한 이유:
        모든 해시 길이가 동일하므로 "경로 문자열의 사전순 비교"는
        "각 자리 해시를 앞에서부터 차례로 비교"와 동치다. 따라서 앞에서부터
        매 단계 최소를 고르면 전체 문자열도 최소가 된다.
        (해시 길이가 가변이면 이 논증은 성립하지 않는다.)

    대안 - 정방향 BFS + 이웃 정렬:
        start에서 이웃을 정렬해 BFS를 돌고 previous[]로 역복원하는 방식도
        같은 답을 낸다. 다만 정당성 논증이 "같은 레벨의 큐 순서가 그 노드들의
        최소 경로 문자열 순서와 일치한다"는 레벨 단위 귀납을 요구해 설명이
        길다. 여기서는 각 단계의 선택 근거가 국소적으로 자명한 2단계 방식을
        택했다. 부수적으로 이웃을 매 방문마다 정렬할 필요도 사라진다.

    시간복잡도: O(V + E) - BFS 1회 + 경로 길이만큼의 탐욕 선택
    """
    if start == target:
        return [start]

    distance = bfs_distances(target, neighbors_of)
    if start not in distance:
        return None

    path = [start]
    current = start

    while current != target:
        current_distance = distance[current]
        candidates = [
            neighbor
            for neighbor in neighbors_of(current)
            if distance.get(neighbor, -1) == current_distance - 1
        ]
        next_node = min_by(candidates)
        if next_node is None:  # 도달 가능하다고 판정된 이상 발생하지 않는다
            return None
        path.append(next_node)
        current = next_node

    return path