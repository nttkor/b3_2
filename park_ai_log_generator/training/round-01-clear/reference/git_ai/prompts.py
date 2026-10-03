from __future__ import annotations

from .git_tools import GitChanges


SYSTEM_RULES = """You are a Git writing assistant.
Use only the supplied git status/diff context.
Do not invent files, tests, issues, deployments, or runtime results.
Keep wording concrete and developer-friendly.
"""


def _context(changes: GitChanges) -> str:
    return """Git status:
{status}

Git diff:
{diff}
""".format(
        status=changes.status.strip() or "(empty)",
        diff=changes.combined_diff.strip() or "(empty)",
    )


def commit_prompt(changes: GitChanges) -> str:
    return SYSTEM_RULES + """
Generate a Git commit message from the context below.

Required output format:
TITLE: <one concise commit title line>
BODY:
- <one concrete change bullet>
- <optional second concrete change bullet>

Rules:
- TITLE must be exactly one line.
- BODY must mention at least one changed file/module or concrete change.
- Do not wrap the answer in a code fence.

""" + _context(changes)


def pr_prompt(changes: GitChanges) -> str:
    return SYSTEM_RULES + """
Generate a Pull Request title and body from the context below.

Required output format:
TITLE: <PR title>
## Why
- <at least one bullet>
## What
- <at least one bullet>
## How to Test
- <at least one bullet based only on evidence available in the diff/status; if no test was actually run, say what should be checked, not that it passed>

Rules:
- Keep all three section headers exactly as shown.
- Every section must contain at least one '-' bullet.
- Do not claim tests passed unless the supplied context proves it.
- Do not wrap the answer in a code fence.

""" + _context(changes)
