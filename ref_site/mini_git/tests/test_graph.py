"""그래프 알고리즘 테스트: 위상 정렬 / 조상 / BFS / 최단 경로."""

import random
import unittest

from minigit.errors import CycleError
from minigit.graph import (
    ancestors,
    bfs_distances,
    smallest_shortest_path,
    topological_order,
)

from .helpers import (
    all_topological_orders,
    brute_force_smallest_path,
    is_parent_first,
    random_dag,
)


def make_graph(edges: dict[str, list[str]]):
    """{자식: [부모...]} 로부터 (nodes, parents_of, children_of) 를 만든다."""
    nodes = list(edges.keys())
    children: dict[str, list[str]] = {n: [] for n in nodes}
    for child, parents in edges.items():
        for parent in parents:
            children[parent].append(child)
    return nodes, (lambda n: edges[n]), (lambda n: children[n])


CHAIN = {"a": [], "b": ["a"], "c": ["b"], "d": ["c"]}
DIAMOND = {"a": [], "b": ["a"], "c": ["a"], "d": ["b", "c"]}


class TopologicalOrderTests(unittest.TestCase):
    def test_chain_has_single_valid_order(self):
        nodes, parents_of, children_of = make_graph(CHAIN)
        result = topological_order(nodes, parents_of, children_of, lambda n: n)
        self.assertEqual(result, ["a", "b", "c", "d"])

    def test_diamond_picks_lexicographically_smallest(self):
        # 유효한 순서는 abcd 와 acbd 두 가지. 사전순 최소인 abcd 를 골라야 한다.
        nodes, parents_of, children_of = make_graph(DIAMOND)
        result = topological_order(nodes, parents_of, children_of, lambda n: n)
        self.assertEqual(result, ["a", "b", "c", "d"])

    def test_tie_break_key_controls_choice(self):
        """후보가 여럿일 때 tie-break 기준이 순서를 결정한다."""
        nodes, parents_of, children_of = make_graph(DIAMOND)
        reversed_order = topological_order(
            nodes, parents_of, children_of, tie_break_key=lambda n: [x for x in "zyxw"][
                "abcd".index(n)
            ]
        )
        self.assertEqual(reversed_order, ["a", "c", "b", "d"])
        # 기준이 무엇이든 위상 제약은 유지된다.
        self.assertTrue(is_parent_first(reversed_order, DIAMOND))

    def test_disconnected_components(self):
        edges = {"a": [], "b": ["a"], "x": [], "y": ["x"]}
        nodes, parents_of, children_of = make_graph(edges)
        result = topological_order(nodes, parents_of, children_of, lambda n: n)
        self.assertEqual(result, ["a", "b", "x", "y"])

    def test_empty_graph(self):
        self.assertEqual(topological_order([], lambda n: [], lambda n: [], lambda n: n), [])

    def test_single_node(self):
        nodes, parents_of, children_of = make_graph({"a": []})
        self.assertEqual(topological_order(nodes, parents_of, children_of, lambda n: n), ["a"])

    def test_cycle_raises(self):
        edges = {"a": ["c"], "b": ["a"], "c": ["b"]}
        nodes, parents_of, children_of = make_graph(edges)
        with self.assertRaises(CycleError):
            topological_order(nodes, parents_of, children_of, lambda n: n)

    def test_matches_brute_force_smallest_order(self):
        """무작위 DAG에서 완전탐색으로 구한 사전순 최소 위상 순서와 일치해야 한다."""
        rng = random.Random(5)
        for _ in range(60):
            count = rng.randint(3, 7)
            nodes, parents, children = random_dag(count, rng.choice([0.3, 0.5]), rng)
            result = topological_order(
                nodes, lambda n: parents[n], lambda n: children[n], lambda n: n
            )
            every = all_topological_orders(nodes, parents)
            self.assertIn(result, every)                    # 유효한 위상 순서
            self.assertEqual(result, min(every))            # 그중 사전순 최소


class AncestorsTests(unittest.TestCase):
    def test_chain(self):
        parents_of = lambda n: CHAIN[n]
        self.assertEqual(set(ancestors("d", parents_of)), {"a", "b", "c"})

    def test_returns_generation_order(self):
        """BFS이므로 가까운 조상이 먼저 나온다."""
        self.assertEqual(ancestors("d", lambda n: CHAIN[n]), ["c", "b", "a"])

    def test_excludes_self(self):
        self.assertNotIn("d", ancestors("d", lambda n: CHAIN[n]))

    def test_root_has_no_ancestors(self):
        self.assertEqual(ancestors("a", lambda n: CHAIN[n]), [])

    def test_diamond_deduplicates_shared_ancestor(self):
        """a 는 b, c 두 경로로 도달하지만 한 번만 나와야 한다."""
        result = ancestors("d", lambda n: DIAMOND[n])
        self.assertEqual(len(result), 3)
        self.assertEqual(result.count("a"), 1)
        self.assertEqual(set(result), {"a", "b", "c"})

    def test_deep_chain_does_not_hit_recursion_limit(self):
        """재귀 DFS라면 RecursionError가 나는 깊이."""
        depth = 5000
        parents = {f"n{i}": ([f"n{i - 1}"] if i else []) for i in range(depth)}
        result = ancestors(f"n{depth - 1}", lambda n: parents[n])
        self.assertEqual(len(result), depth - 1)


class BfsDistanceTests(unittest.TestCase):
    ADJACENCY = {"a": ["b", "c"], "b": ["a", "d"], "c": ["a", "d"], "d": ["b", "c"], "z": []}

    def test_distances(self):
        result = bfs_distances("a", lambda n: self.ADJACENCY[n])
        self.assertEqual(result, {"a": 0, "b": 1, "c": 1, "d": 2})

    def test_unreachable_node_absent(self):
        result = bfs_distances("a", lambda n: self.ADJACENCY[n])
        self.assertNotIn("z", result)


class ShortestPathTests(unittest.TestCase):
    # 무방향 다이아몬드: a-b, a-c, b-d, c-d, 그리고 고립된 z
    ADJACENCY = {"a": ["b", "c"], "b": ["a", "d"], "c": ["a", "d"], "d": ["b", "c"], "z": []}

    def neighbors(self, node):
        return self.ADJACENCY[node]

    def test_same_node(self):
        self.assertEqual(smallest_shortest_path("a", "a", self.neighbors), ["a"])

    def test_adjacent_nodes(self):
        self.assertEqual(smallest_shortest_path("a", "b", self.neighbors), ["a", "b"])

    def test_picks_lexicographically_smallest_of_two_shortest(self):
        """a->b->d 와 a->c->d 둘 다 길이 2. 사전순 최소인 b 경유를 골라야 한다."""
        self.assertEqual(smallest_shortest_path("a", "d", self.neighbors), ["a", "b", "d"])

    def test_symmetric_direction(self):
        self.assertEqual(smallest_shortest_path("d", "a", self.neighbors), ["d", "b", "a"])

    def test_no_path_returns_none(self):
        self.assertIsNone(smallest_shortest_path("a", "z", self.neighbors))

    def test_matches_brute_force_on_random_graphs(self):
        rng = random.Random(99)
        checked = 0
        for _ in range(80):
            count = rng.randint(4, 8)
            nodes, parents, children = random_dag(count, rng.choice([0.25, 0.5, 0.7]), rng)
            adjacency = {n: parents[n] + children[n] for n in nodes}
            for _ in range(3):
                start, target = rng.choice(nodes), rng.choice(nodes)
                self.assertEqual(
                    smallest_shortest_path(start, target, lambda n: adjacency[n]),
                    brute_force_smallest_path(start, target, adjacency),
                )
                checked += 1
        self.assertGreater(checked, 200)


if __name__ == "__main__":
    unittest.main()