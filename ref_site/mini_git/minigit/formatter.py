"""출력 포맷 담당. 표현(presentation)을 도메인 로직에서 분리한다."""

from .models import Commit

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_commit(commit: Commit, branch_labels: dict[str, list[str]]) -> str:
    """LOG 한 항목. hash / author / timestamp / message 를 모두 식별 가능하게."""
    labels = branch_labels.get(commit.hash, [])
    label_text = f" [{', '.join(labels)}]" if labels else ""
    merge_text = " (merge)" if commit.is_merge else ""
    header = (
        f"commit {commit.short_hash} "
        f"({commit.author}, {commit.timestamp.strftime(TIME_FORMAT)})"
        f"{label_text}{merge_text}"
    )
    return f"{header}\n    {commit.message}"


def format_log(commits: list[Commit], branch_labels: dict[str, list[str]]) -> str:
    """LOG 출력 전체. 커밋이 없으면 안내 문구를 돌려준다."""
    if not commits:
        return "No commits yet."
    return "\n".join(format_commit(c, branch_labels) for c in commits)


def format_search_results(commits: list[Commit]) -> str:
    """SEARCH 결과. 개수에 따라 단수/복수를 맞춘다."""
    if not commits:
        return "Found 0 commits."
    noun = "commit" if len(commits) == 1 else "commits"
    lines = [f"Found {len(commits)} {noun}:", ""]
    for commit in commits:
        lines.append(f"- {commit.short_hash}: {commit.message}")
    return "\n".join(lines)


def format_ancestors(commits: list[Commit]) -> str:
    """ANCESTORS 결과. 개수에 따라 단수/복수를 맞춘다."""
    if not commits:
        return "No ancestors."
    noun = "ancestor" if len(commits) == 1 else "ancestors"
    lines = [f"Found {len(commits)} {noun}:", ""]
    for commit in commits:
        lines.append(f"- {commit.short_hash}: {commit.message}")
    return "\n".join(lines)


def format_path(path: list[str] | None, short: bool = True) -> str:
    """PATH 결과. 경로가 없으면 명세대로 'No path'."""
    if path is None:
        return "No path"
    rendered = [h[:7] if short else h for h in path]
    return "Path: " + " -> ".join(rendered)


def format_diff(rows: list[tuple[str, str]]) -> str:
    """DIFF 결과. 본문 뒤에 추가/삭제 줄 수 요약을 붙인다."""
    added = sum(1 for symbol, _ in rows if symbol == "+")
    removed = sum(1 for symbol, _ in rows if symbol == "-")
    body = "\n".join(f"{symbol} {line}" for symbol, line in rows)
    return f"{body}\n\n(+{added} added, -{removed} removed)"