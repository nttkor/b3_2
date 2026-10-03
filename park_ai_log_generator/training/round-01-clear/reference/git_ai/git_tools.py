from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .errors import GitAIError


@dataclass(slots=True)
class GitChanges:
    status: str
    unstaged_diff: str
    staged_diff: str

    @property
    def combined_diff(self) -> str:
        parts: list[str] = []
        if self.unstaged_diff.strip():
            parts.append("[UNSTAGED]\n" + self.unstaged_diff.strip())
        if self.staged_diff.strip():
            parts.append("[STAGED]\n" + self.staged_diff.strip())
        return "\n\n".join(parts)

    @property
    def has_changes(self) -> bool:
        return bool(self.status.strip() or self.combined_diff.strip())


def _run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise GitAIError("git 명령을 찾을 수 없습니다. Git 설치 상태를 확인하세요.") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise GitAIError("Git 명령 실패: {}".format(detail))
    return result.stdout


def ensure_git_repository() -> None:
    inside = _run_git("rev-parse", "--is-inside-work-tree").strip().lower()
    if inside != "true":
        raise GitAIError("현재 디렉터리가 Git 작업 트리가 아닙니다.")


def collect_changes() -> GitChanges:
    ensure_git_repository()
    return GitChanges(
        status=_run_git("status", "--short"),
        unstaged_diff=_run_git("diff", "--no-ext-diff"),
        staged_diff=_run_git("diff", "--cached", "--no-ext-diff"),
    )
