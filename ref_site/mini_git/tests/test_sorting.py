"""정렬 모듈 테스트: merge_sort / insertion_sort / MinHeap / min_by."""

import random
import unittest

from minigit.sorting import MinHeap, insertion_sort, merge_sort, min_by

ALGORITHMS = (("merge_sort", merge_sort), ("insertion_sort", insertion_sort))


class SortResultTests(unittest.TestCase):
    """두 정렬 알고리즘이 같은 정답을 내는지 확인한다."""

    CASES = [
        ([], []),
        ([1], [1]),
        ([2, 1], [1, 2]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),          # 이미 정렬
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),          # 역순
        ([3, 1, 3, 1, 2], [1, 1, 2, 3, 3]),          # 중복
        ([0, -5, 10, -1], [-5, -1, 0, 10]),          # 음수
        (["banana", "Apple", "cherry"], ["Apple", "banana", "cherry"]),
    ]

    def test_expected_results(self):
        for name, algorithm in ALGORITHMS:
            for values, expected in self.CASES:
                with self.subTest(algorithm=name, values=values):
                    self.assertEqual(algorithm(values), expected)

    def test_does_not_mutate_input(self):
        for name, algorithm in ALGORITHMS:
            with self.subTest(algorithm=name):
                original = [3, 1, 2]
                algorithm(original)
                self.assertEqual(original, [3, 1, 2])

    def test_key_changes_comparison_basis(self):
        words = ["ccc", "a", "bb"]
        for name, algorithm in ALGORITHMS:
            with self.subTest(algorithm=name):
                self.assertEqual(algorithm(words, key=len), ["a", "bb", "ccc"])
                self.assertEqual(
                    algorithm(words, key=lambda w: -len(w)), ["ccc", "bb", "a"]
                )

    def test_both_algorithms_agree_on_random_input(self):
        rng = random.Random(42)
        for _ in range(50):
            values = [rng.randint(-50, 50) for _ in range(rng.randint(0, 40))]
            self.assertEqual(merge_sort(values), insertion_sort(values))


class StabilityTests(unittest.TestCase):
    """안정 정렬 여부. 동률일 때 원래 순서가 보존되어야 한다."""

    def test_equal_keys_preserve_original_order(self):
        # (정렬 키, 원래 인덱스). 키가 같은 항목들의 인덱스가 오름차순이어야 한다.
        items = [("b", 0), ("a", 1), ("b", 2), ("a", 3), ("b", 4)]
        expected = [("a", 1), ("a", 3), ("b", 0), ("b", 2), ("b", 4)]
        for name, algorithm in ALGORITHMS:
            with self.subTest(algorithm=name):
                self.assertEqual(algorithm(items, key=lambda x: x[0]), expected)

    def test_stability_on_random_input(self):
        rng = random.Random(7)
        items = [(rng.randint(0, 3), i) for i in range(200)]
        for name, algorithm in ALGORITHMS:
            with self.subTest(algorithm=name):
                result = algorithm(items, key=lambda x: x[0])
                for group_key in range(4):
                    indices = [i for k, i in result if k == group_key]
                    self.assertEqual(indices, merge_sort(indices))


class MinHeapTests(unittest.TestCase):
    """최소 힙. 위상 정렬의 후보 선택에 쓰인다."""

    def test_pops_in_ascending_order(self):
        heap = MinHeap()
        for value in [5, 3, 8, 1, 9, 2]:
            heap.push(value)
        popped = [heap.pop() for _ in range(6)]
        self.assertEqual(popped, [1, 2, 3, 5, 8, 9])

    def test_len_tracks_size(self):
        heap = MinHeap()
        self.assertEqual(len(heap), 0)
        heap.push("x")
        heap.push("y")
        self.assertEqual(len(heap), 2)
        heap.pop()
        self.assertEqual(len(heap), 1)

    def test_respects_key(self):
        heap = MinHeap(key=lambda word: len(word))
        for word in ["ccc", "a", "bb"]:
            heap.push(word)
        self.assertEqual([heap.pop() for _ in range(3)], ["a", "bb", "ccc"])

    def test_interleaved_push_pop(self):
        """중간에 더 작은 값을 넣어도 항상 최소가 나와야 한다."""
        heap = MinHeap()
        heap.push(10)
        heap.push(20)
        self.assertEqual(heap.pop(), 10)
        heap.push(5)
        heap.push(15)
        self.assertEqual(heap.pop(), 5)
        self.assertEqual(heap.pop(), 15)
        self.assertEqual(heap.pop(), 20)

    def test_matches_merge_sort_on_random_input(self):
        rng = random.Random(3)
        values = [rng.randint(0, 999) for _ in range(300)]
        heap = MinHeap()
        for value in values:
            heap.push(value)
        self.assertEqual([heap.pop() for _ in values], merge_sort(values))

    def test_pop_from_empty_raises(self):
        with self.assertRaises(IndexError):
            MinHeap().pop()


class MinByTests(unittest.TestCase):
    def test_returns_minimum(self):
        self.assertEqual(min_by([3, 1, 2]), 1)

    def test_returns_none_for_empty(self):
        self.assertIsNone(min_by([]))

    def test_respects_key(self):
        self.assertEqual(min_by(["ccc", "a", "bb"], key=len), "a")

    def test_returns_first_of_equal_minimums(self):
        first, second = ("a", 1), ("a", 2)
        self.assertIs(min_by([first, second], key=lambda x: x[0]), first)


if __name__ == "__main__":
    unittest.main()