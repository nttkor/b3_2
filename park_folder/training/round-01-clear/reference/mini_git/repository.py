from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .algorithms import smallest_string, stable_merge_sort
from .models import Commit


class MiniGitError(Exception):
    """Expected command/repository error."""


@dataclass(slots=True)
class SearchIndexes:
    keyword: dict[str, list[str]]
    author: dict[str, list[str]]


class MiniGitRepository:
    """In-memory Mini Git repository for the B3-2 learning mission."""

    def __init__(self) -> None:
        self.initialized = False
        self.current_user = ""
        self.commits: dict[str, Commit] = {}
        self.branches: dict[str, str | None] = {}
        self.head_branch = ""
        self._counter = 0
        self.indexes = SearchIndexes(keyword={}, author={})

    def init(self, user_name: str) -> str:
        name = user_name.strip()
        if not name:
            raise MiniGitError("Invalid args")
        self.initialized = True
        self.current_user = name
        self.commits.clear()
        self.branches = {"main": None}
        self.head_branch = "main"
        self._counter = 0
        self.indexes = SearchIndexes(keyword={}, author={})
        return "Initialized repository for {} on main".format(name)

    def _require_init(self) -> None:
        if not self.initialized:
            raise MiniGitError("Repository not initialized")

    def current_head(self) -> str | None:
        self._require_init()
        return self.branches[self.head_branch]

    def branch(self, branch_name: str) -> str:
        self._require_init()
        name = branch_name.strip()
        if not name:
            raise MiniGitError("Invalid args")
        if name in self.branches:
            raise MiniGitError("Branch already exists: {}".format(name))
        self.branches[name] = self.current_head()
        return "Created branch {} at {}".format(name, self.branches[name] or "<empty>")

    def switch(self, branch_name: str) -> str:
        self._require_init()
        if branch_name not in self.branches:
            raise MiniGitError("Unknown branch: {}".format(branch_name))
        self.head_branch = branch_name
        return "Switched to branch {}".format(branch_name)

    def _next_hash(self) -> str:
        self._counter += 1
        return "c{:06d}".format(self._counter)

    @staticmethod
    def _tokens(message: str) -> list[str]:
        # Official minimum criterion: whitespace split + lowercase normalization.
        result: list[str] = []
        for token in message.split():
            normalized = token.lower()
            if normalized:
                result.append(normalized)
        return result

    @staticmethod
    def _append_index(index: dict[str, list[str]], key: str, commit_hash: str) -> None:
        if key not in index:
            index[key] = []
        # Avoid duplicate hash for repeated keyword tokens inside one message.
        bucket = index[key]
        if not bucket or bucket[-1] != commit_hash:
            bucket.append(commit_hash)

    def commit(self, message: str) -> Commit:
        self._require_init()
        text = message.strip()
        if not text:
            raise MiniGitError("Invalid args")

        parent = self.current_head()
        parents = [] if parent is None else [parent]
        commit_hash = self._next_hash()
        commit = Commit.create(commit_hash, text, self.current_user, parents)
        self.commits[commit_hash] = commit
        self.branches[self.head_branch] = commit_hash

        seen_tokens: dict[str, bool] = {}
        for token in self._tokens(text):
            if token in seen_tokens:
                continue
            seen_tokens[token] = True
            self._append_index(self.indexes.keyword, token, commit_hash)
        self._append_index(self.indexes.author, self.current_user.lower(), commit_hash)
        return commit

    def _require_commit(self, commit_hash: str) -> Commit:
        commit = self.commits.get(commit_hash)
        if commit is None:
            raise MiniGitError("Unknown commit: {}".format(commit_hash))
        return commit

    def _visit_parent_first(self, commit_hash: str, visiting: dict[str, bool], visited: dict[str, bool], output: list[Commit]) -> None:
        if commit_hash in visited:
            return
        if commit_hash in visiting:
            raise MiniGitError("DAG invariant violated: cycle detected")
        visiting[commit_hash] = True
        commit = self._require_commit(commit_hash)
        for parent_hash in commit.parents:
            self._visit_parent_first(parent_hash, visiting, visited, output)
        visiting.pop(commit_hash, None)
        visited[commit_hash] = True
        output.append(commit)

    def log_parent_first(self) -> list[Commit]:
        self._require_init()
        output: list[Commit] = []
        visited: dict[str, bool] = {}
        visiting: dict[str, bool] = {}
        # dict insertion order is commit creation order; parent-first DFS still enforces the requirement.
        for commit_hash in self.commits:
            self._visit_parent_first(commit_hash, visiting, visited, output)
        return output

    def log_sorted(self, sort_by: str) -> list[Commit]:
        self._require_init()
        commits = list(self.commits.values())
        if sort_by == "date":
            return stable_merge_sort(commits, key=lambda commit: (commit.timestamp, commit.hash))
        if sort_by == "author":
            return stable_merge_sort(commits, key=lambda commit: (commit.author.lower(), commit.hash))
        raise MiniGitError("Invalid args")

    def _neighbors(self, commit_hash: str) -> list[str]:
        self._require_commit(commit_hash)
        neighbors: list[str] = []
        commit = self.commits[commit_hash]
        for parent_hash in commit.parents:
            neighbors.append(parent_hash)
        for child_hash, child in self.commits.items():
            for parent_hash in child.parents:
                if parent_hash == commit_hash:
                    neighbors.append(child_hash)
                    break
        return neighbors

    def _distances_from(self, start_hash: str) -> dict[str, int]:
        self._require_commit(start_hash)
        distances: dict[str, int] = {start_hash: 0}
        queue: deque[str] = deque([start_hash])
        while queue:
            current = queue.popleft()
            next_distance = distances[current] + 1
            for neighbor in self._neighbors(current):
                if neighbor not in distances:
                    distances[neighbor] = next_distance
                    queue.append(neighbor)
        return distances

    def path(self, start_hash: str, target_hash: str) -> list[str] | None:
        self._require_init()
        self._require_commit(start_hash)
        self._require_commit(target_hash)
        if start_hash == target_hash:
            return [start_hash]

        distance_to_target = self._distances_from(target_hash)
        if start_hash not in distance_to_target:
            return None

        path = [start_hash]
        current = start_hash
        while current != target_hash:
            current_distance = distance_to_target[current]
            candidates: list[str] = []
            for neighbor in self._neighbors(current):
                if distance_to_target.get(neighbor) == current_distance - 1:
                    candidates.append(neighbor)
            next_hash = smallest_string(candidates)
            if next_hash is None:
                raise MiniGitError("Path reconstruction failed")
            path.append(next_hash)
            current = next_hash
        return path

    def ancestors(self, commit_hash: str) -> list[str]:
        self._require_init()
        self._require_commit(commit_hash)
        output: list[str] = []
        visited: dict[str, bool] = {}
        stack: list[str] = list(self.commits[commit_hash].parents)
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited[current] = True
            output.append(current)
            for parent_hash in self.commits[current].parents:
                stack.append(parent_hash)
        return stable_merge_sort(output, key=lambda value: value)

    def search_keyword(self, keyword: str) -> list[Commit]:
        self._require_init()
        hashes = self.indexes.keyword.get(keyword.lower(), [])
        return [self.commits[commit_hash] for commit_hash in hashes]

    def search_author(self, author: str) -> list[Commit]:
        self._require_init()
        hashes = self.indexes.author.get(author.lower(), [])
        return [self.commits[commit_hash] for commit_hash in hashes]
