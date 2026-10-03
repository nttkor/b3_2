from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def stable_merge_sort(items: list[T], key: Callable[[T], object]) -> list[T]:
    """Stable O(n log n) merge sort without sorted()/list.sort()."""

    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = stable_merge_sort(items[:middle], key)
    right = stable_merge_sort(items[middle:], key)
    result: list[T] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        left_key = key(left[left_index])
        right_key = key(right[right_index])
        if left_key <= right_key:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    while left_index < len(left):
        result.append(left[left_index])
        left_index += 1
    while right_index < len(right):
        result.append(right[right_index])
        right_index += 1

    return result


def smallest_string(values: list[str]) -> str | None:
    """Return the lexicographically smallest string without a sorting API."""

    if not values:
        return None
    smallest = values[0]
    for value in values[1:]:
        if value < smallest:
            smallest = value
    return smallest
