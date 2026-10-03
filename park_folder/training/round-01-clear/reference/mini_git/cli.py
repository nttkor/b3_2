from __future__ import annotations

import shlex

from .models import Commit
from .repository import MiniGitError, MiniGitRepository


def render_commit(commit: Commit) -> str:
    parents = ",".join(commit.parents) if commit.parents else "-"
    return "{} | {} | {} | parents={} | {}".format(
        commit.hash,
        commit.author,
        commit.timestamp,
        parents,
        commit.message,
    )


def execute(repo: MiniGitRepository, line: str) -> str:
    try:
        parts = shlex.split(line)
    except ValueError:
        return "Invalid args"

    if not parts:
        return ""

    command = parts[0].upper()

    try:
        if command == "INIT":
            if len(parts) != 2:
                return "Invalid args"
            return repo.init(parts[1])

        if command == "BRANCH":
            if len(parts) != 2:
                return "Invalid args"
            return repo.branch(parts[1])

        if command == "SWITCH":
            if len(parts) != 2:
                return "Invalid args"
            return repo.switch(parts[1])

        if command == "COMMIT":
            if len(parts) != 2:
                return "Invalid args"
            commit = repo.commit(parts[1])
            return "Committed {}".format(render_commit(commit))

        if command == "LOG":
            if len(parts) == 1:
                commits = repo.log_parent_first()
            elif len(parts) == 2 and parts[1].startswith("--sort-by="):
                sort_by = parts[1].split("=", 1)[1].lower()
                commits = repo.log_sorted(sort_by)
            else:
                return "Invalid args"
            if not commits:
                return "(empty)"
            return "\n".join(render_commit(commit) for commit in commits)

        if command == "PATH":
            if len(parts) != 3:
                return "Invalid args"
            result = repo.path(parts[1], parts[2])
            return "No path" if result is None else " -> ".join(result)

        if command == "ANCESTORS":
            if len(parts) != 2:
                return "Invalid args"
            result = repo.ancestors(parts[1])
            return "(empty)" if not result else "\n".join(result)

        if command == "SEARCH":
            if len(parts) != 2:
                return "Invalid args"
            argument = parts[1]
            if argument.startswith("--author="):
                author = argument.split("=", 1)[1]
                if not author:
                    return "Invalid args"
                commits = repo.search_author(author)
            else:
                commits = repo.search_keyword(argument)
            if not commits:
                return "(empty)"
            return "\n".join(render_commit(commit) for commit in commits)

        return "Unknown command: {}".format(parts[0])

    except MiniGitError as exc:
        return str(exc)


def repl() -> None:
    repo = MiniGitRepository()
    while True:
        try:
            line = input("mini-git> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if line.strip().lower() in ("exit", "quit"):
            return

        output = execute(repo, line)
        if output:
            print(output)
