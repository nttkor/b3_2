"""평가 시연용 데모 시나리오.

    python demo.py

가짜 시계를 주입해 커밋 해시를 고정한다. 실행할 때마다 같은 해시가 나오므로
발표 자료의 그림과 화면 출력이 항상 일치한다.
(main.py 의 REPL 은 실제 시각을 쓰므로 매번 다른 해시가 나온다.)

만들어지는 그래프:

    a1  Initial commit        (Alice)
    ├── b1  Add login form    (Alice)   main
    │   └── d1  Fix login bug (Alice)   main
    └── c1  Add payment API   (Bob)     feature
        └── e1  Add payment tests (Bob) feature
                 \\
    m1  Merge branch 'feature' into main   (부모 2개: d1, e1)
"""

from datetime import datetime, timedelta

from minigit.cli import execute
from minigit.repository import Repository

SCRIPT = [
    'init "Alice"',
    'commit "Initial commit"',
    "branch feature",
    'commit "Add login form"',
    "switch feature",
    'user "Bob"',
    'commit "Add payment API"',
    'commit "Add payment tests"',
    "switch main",
    'user "Alice"',
    'commit "Fix login bug"',
    "merge feature",
]

QUERIES = [
    "log",
    "log --sort-by=date",
    "log --sort-by=author",
    'search "login"',
    'search "payment"',
    "search --author=Bob",
]


class DemoClock:
    """호출할 때마다 10분씩 흐르는 고정 시계."""

    def __init__(self) -> None:
        self._now = datetime(2026, 3, 2, 9, 0, 0)

    def __call__(self) -> datetime:
        current = self._now
        self._now += timedelta(minutes=10)
        return current


def build() -> Repository:
    """데모 저장소를 만든다."""
    repo = Repository(clock=DemoClock())
    for line in SCRIPT:
        execute(repo, line)
    return repo


def run(repo: Repository, line: str) -> None:
    print(f"mini-git> {line}")
    output = execute(repo, line)
    if output:
        print(output)
    print()


def main() -> None:
    repo = Repository(clock=DemoClock())

    print("=" * 62)
    print(" 1. 저장소 구축")
    print("=" * 62 + "\n")
    for line in SCRIPT:
        run(repo, line)

    print("=" * 62)
    print(" 2. 조회 명령")
    print("=" * 62 + "\n")
    for line in QUERIES:
        run(repo, line)

    print("=" * 62)
    print(" 3. 경로 탐색")
    print("=" * 62 + "\n")
    order = repo.log()
    first, last = order[0], order[-1]
    run(repo, f"path {first.short_hash} {last.short_hash}")
    run(repo, f"ancestors {last.short_hash}")


if __name__ == "__main__":
    main()