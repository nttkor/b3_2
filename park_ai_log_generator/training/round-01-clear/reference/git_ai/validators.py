from __future__ import annotations

from .errors import GitAIError


def _extract_title(text: str) -> str:
    first = text.splitlines()[0].strip() if text.strip() else ""
    if not first.startswith("TITLE:"):
        raise GitAIError("AI 결과 형식 오류: 첫 줄은 'TITLE:'이어야 합니다.")
    title = first.removeprefix("TITLE:").strip()
    if not title:
        raise GitAIError("AI 결과 형식 오류: 제목이 비어 있습니다.")
    if "\n" in title or "\r" in title:
        raise GitAIError("AI 결과 형식 오류: 제목은 한 줄이어야 합니다.")
    return title


def validate_commit_output(text: str) -> str:
    _extract_title(text)
    lines = [line.strip() for line in text.splitlines()]
    bullets = [line for line in lines if line.startswith("- ") and len(line) > 2]
    if not bullets:
        raise GitAIError("AI 결과 형식 오류: Commit 본문에는 최소 1개의 구체적 bullet이 필요합니다.")
    return text.strip()


def validate_pr_output(text: str) -> str:
    _extract_title(text)
    required = ["## Why", "## What", "## How to Test"]
    lines = text.splitlines()

    for header in required:
        if header not in lines:
            raise GitAIError("AI 결과 형식 오류: '{}' 섹션이 필요합니다.".format(header))

    for index, header in enumerate(required):
        start = lines.index(header) + 1
        end = len(lines)
        if index + 1 < len(required):
            end = lines.index(required[index + 1])
        section = [line.strip() for line in lines[start:end]]
        if not any(line.startswith("- ") and len(line) > 2 for line in section):
            raise GitAIError("AI 결과 형식 오류: '{}'에는 최소 1개의 bullet이 필요합니다.".format(header))

    return text.strip()
