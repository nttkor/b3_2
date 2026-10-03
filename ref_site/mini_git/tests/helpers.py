"""테스트 공용 도구."""

import random
from collections import deque
from datetime import datetime, timedelta

from minigit.repository import Repository

START_TIME = datetime(2026, 1, 15, 9, 0, 0)


class FakeClock:
    """호출할 때마다 일정 간격으로 흐르는 결정적 시계.

    실제 datetime.now()를 쓰면 타임스탬프가 매번 달라져 커밋 해시도 달라진다.
    그러면 '결과값이 일치하는가'를 검증할 수 없으므로 시계를 고정한다.
    """

    def __init__(self, start: datetime = START_TIME, step_seconds: int = 60) -> None:
        self._now = start
        self._step = timedelta(seconds=step_seconds)

    def __call__(self) -> datetime:
        current = self._now
        self._now += self._step
        return current


class FixedClock:
    """항상 같은 시각을 돌려주는 시계.

    타임스탬프까지 동일하게 만들어 '커밋 해시의 유일성이 정말 sequence
    덕분인지'를 분리 검증하는 데 쓴다.
    """

    def __init__(self, moment: datetime = START_TIME) -> None:
        self._moment = moment

    def __call__(self) -> datetime:
        return self._moment


def new_repo(user: str = "Alice") -> Repository:
    """가짜 시계를 물린 초기화된 저장소."""
    repo = Repository(clock=FakeClock())
    repo.init(user)
    return repo


def build_diamond() -> tuple[Repository, dict[str, str]]:
    """다이아몬드 그래프. merge로 두 갈래가 다시 합쳐진다.

            A            A: root
           / \\           B: main 쪽
          B   C          C: feature 쪽
           \\ /           M: merge (부모 2개)
            M
    """
    repo = new_repo("Alice")
    a = repo.commit("A root")
    repo.branch("feature")
    b = repo.commit("B main")
    repo.switch("feature")
    c = repo.commit("C feature")
    repo.switch("main")
    kind, m = repo.merge("feature")
    assert kind == "merge" and m is not None
    return repo, {"A": a.hash, "B": b.hash, "C": c.hash, "M": m.hash}


def build_two_roots() -> tuple[Repository, dict[str, str]]:
    """서로 연결되지 않은 두 커밋 그래프. PATH의 'No path' 검증용.

    커밋 전에 브랜치를 만들면 두 브랜치 모두 HEAD가 None이라
    각자 부모 없는 루트 커밋을 만들 수 있다.
    """
    repo = new_repo("Alice")
    repo.branch("other")
    r1 = repo.commit("first root")
    repo.switch("other")
    r2 = repo.commit("second root")
    return repo, {"R1": r1.hash, "R2": r2.hash}


def is_parent_first(order: list[str], parents: dict[str, list[str]]) -> bool:
    """주어진 해시 순서가 '부모가 자식보다 먼저'를 만족하는가."""
    position = {h: i for i, h in enumerate(order)}
    return all(
        position[p] < position[h]
        for h in order
        for p in parents[h]
        if p in position
    )


def all_topological_orders(
    nodes: list[str], parents: dict[str, list[str]]
) -> list[list[str]]:
    """유효한 위상 순서를 전부 열거한다 (완전탐색, 소규모 전용)."""
    results: list[list[str]] = []

    def recurse(order: list[str], placed: set[str]) -> None:
        if len(order) == len(nodes):
            results.append(list(order))
            return
        for node in nodes:
            if node in placed:
                continue
            if all(p in placed for p in parents[node]):
                order.append(node)
                placed.add(node)
                recurse(order, placed)
                order.pop()
                placed.remove(node)

    recurse([], set())
    return results


def brute_force_smallest_path(
    start: str, target: str, adjacency: dict[str, list[str]]
) -> list[str] | None:
    """최단 경로를 전부 만들어 사전순 최소를 고른다 (완전탐색, 소규모 전용)."""
    distance = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)
    if target not in distance:
        return None

    length = distance[target]
    best: tuple[str, list[str]] | None = None

    def recurse(node: str, path: list[str]) -> None:
        nonlocal best
        if len(path) - 1 > length:
            return
        if node == target and len(path) - 1 == length:
            rendered = "->".join(path)
            if best is None or rendered < best[0]:
                best = (rendered, list(path))
            return
        for neighbor in adjacency[node]:
            if neighbor in path:
                continue
            path.append(neighbor)
            recurse(neighbor, path)
            path.pop()

    recurse(start, [start])
    return best[1] if best else None


def random_dag(node_count: int, density: float, rng: random.Random):
    """무작위 DAG. i번 노드는 j < i 인 노드만 부모로 가지므로 사이클이 없다."""
    nodes = [f"{i:02d}" for i in range(node_count)]
    rng.shuffle(nodes)
    parents: dict[str, list[str]] = {n: [] for n in nodes}
    children: dict[str, list[str]] = {n: [] for n in nodes}
    for i in range(1, node_count):
        for j in range(i):
            if rng.random() < density:
                parents[nodes[i]].append(nodes[j])
                children[nodes[j]].append(nodes[i])
    return nodes, parents, children