"""CLI 파서와 REPL 루프.

공통 규칙:
    - 명령어는 대소문자를 구분하지 않는다.
    - 공백을 포함하는 인자는 따옴표로 감싼다. (shlex가 처리)
    - 옵션은 --key=value 형식으로 통일한다.
"""

import shlex
import time

from .errors import InvalidArgsError, MiniGitError
from .formatter import (
    format_ancestors,
    format_log,
    format_path,
    format_search_results,
)
from .repository import Repository
from .sorting import insertion_sort, merge_sort

PROMPT = "mini-git> "
EXIT_COMMANDS = ("exit", "quit")

HELP_TEXT = """Commands:
  INIT <user_name>              저장소 초기화
  USER <user_name>              현재 작성자 변경 (확장)
  BRANCH <branch_name>          현재 HEAD를 가리키는 브랜치 생성
  SWITCH <branch_name>          브랜치 전환
  COMMIT <message>              현재 HEAD를 부모로 커밋 생성
  MERGE <branch_name>           브랜치 병합 (부모 2개인 merge commit)
  LOG                           위상 정렬 (부모가 항상 자식보다 먼저)
  LOG --sort-by=date|author     기준에 따른 전체 정렬
  PATH <commit1> <commit2>      두 커밋 사이 최단 경로
  ANCESTORS <commit_hash>       모든 조상 커밋
  SEARCH <keyword>              메시지 키워드 검색 (역색인)
  SEARCH --author=<name>        작성자 검색 (역색인)
  BENCH <n>                     정렬 알고리즘 성능 비교
  HELP                          도움말
  EXIT | QUIT                   종료

* 공백이 포함된 인자는 따옴표로: COMMIT "Add login feature"
"""


def parse_line(line: str) -> tuple[str, list[str], dict[str, str]] | None:
    """입력 한 줄을 (명령어, 위치 인자, 옵션)으로 분해한다."""
    try:
        tokens = shlex.split(line)
    except ValueError as exc:
        raise InvalidArgsError(str(exc)) from exc

    if not tokens:
        return None

    command = tokens[0].lower()
    args: list[str] = []
    options: dict[str, str] = {}

    for token in tokens[1:]:
        if token.startswith("--") and "=" in token:
            key, value = token[2:].split("=", 1)
            options[key.lower()] = value
        else:
            args.append(token)

    return command, args, options


def _expect(condition: bool) -> None:
    """인자 개수/형식 사전조건. 어기면 표준 Invalid args 에러."""
    if not condition:
        raise InvalidArgsError()


# ----------------------------------------------------------------------
# 명령 핸들러
# ----------------------------------------------------------------------


def cmd_init(repo: Repository, args, options) -> str:
    """INIT <user_name> - 저장소를 초기화한다."""
    _expect(len(args) == 1 and not options)
    repo.init(args[0])
    return (
        "Initialized repository.\n"
        f"Current branch: {repo.current_branch}\n"
        f"Current user: {repo.current_user}"
    )


def cmd_branch(repo: Repository, args, options) -> str:
    """BRANCH <name> - 현재 HEAD를 가리키는 브랜치를 만든다."""
    _expect(len(args) == 1 and not options)
    repo.branch(args[0])
    return f"Created branch: {args[0]}"


def cmd_switch(repo: Repository, args, options) -> str:
    """SWITCH <name> - HEAD를 해당 브랜치로 옮긴다."""
    _expect(len(args) == 1 and not options)
    repo.switch(args[0])
    return f"Switched to branch: {args[0]}"


def cmd_commit(repo: Repository, args, options) -> str:
    """COMMIT <message> - 현재 HEAD를 부모로 커밋을 만든다."""
    _expect(len(args) == 1 and not options)
    commit = repo.commit(args[0])
    return f"[{repo.current_branch} {commit.short_hash}] {commit.message}"


def cmd_merge(repo: Repository, args, options) -> str:
    """MERGE <name> - 대상 브랜치를 현재 브랜치로 병합한다."""
    _expect(len(args) == 1 and not options)
    kind, commit = repo.merge(args[0])
    if kind == "up-to-date":
        return "Already up to date."
    if kind == "fast-forward":
        return f"Fast-forward to branch: {args[0]}"
    assert commit is not None
    return f"[{repo.current_branch} {commit.short_hash}] {commit.message}"


def cmd_user(repo: Repository, args, options) -> str:
    """USER <name> - 현재 작성자를 바꾼다 (명세 외 확장)."""
    _expect(len(args) == 1 and not options)
    repo.set_user(args[0])
    return f"Current user: {repo.current_user}"


def cmd_log(repo: Repository, args, options) -> str:
    """LOG [--sort-by=date|author] - 위상 정렬 또는 지정 기준 전체 정렬."""
    _expect(not args)
    for key in options:
        _expect(key == "sort-by")

    sort_by = options.get("sort-by")
    commits = repo.log(sort_by)
    output = format_log(commits, repo.branch_labels())

    # 전체 정렬이 위상 제약을 깨뜨렸다면 알려준다.
    # "정렬 != 위상 정렬"을 사용자가 눈으로 확인하게 만드는 장치다.
    if sort_by is not None and not repo.is_parent_first(commits):
        output += (
            "\n\n(note: this order is sorted by "
            f"{sort_by}, so a parent may appear after its child. "
            "use plain LOG for parent-first order.)"
        )
    return output


def cmd_path(repo: Repository, args, options) -> str:
    """PATH <c1> <c2> - 두 커밋 사이 최단 경로를 출력한다."""
    _expect(len(args) == 2 and not options)
    return format_path(repo.path(args[0], args[1]))


def cmd_ancestors(repo: Repository, args, options) -> str:
    """ANCESTORS <hash> - 도달 가능한 모든 조상을 출력한다."""
    _expect(len(args) == 1 and not options)
    return format_ancestors(repo.ancestors(args[0]))


def cmd_search(repo: Repository, args, options) -> str:
    """SEARCH <keyword> | SEARCH --author=<name> - 역색인 검색."""
    if "author" in options:
        _expect(not args and len(options) == 1)
        return format_search_results(repo.search_author(options["author"]))
    _expect(len(args) == 1 and not options)
    return format_search_results(repo.search_keyword(args[0]))



def cmd_bench(repo: Repository, args, options) -> str:
    """보너스: 같은 입력에 대한 merge_sort vs insertion_sort 비교."""
    _expect(len(args) == 1 and not options)
    try:
        size = int(args[0])
    except ValueError as exc:
        raise InvalidArgsError("size must be an integer") from exc
    if size <= 0 or size > 20000:
        raise InvalidArgsError("size must be between 1 and 20000")

    # 표준 정렬 API를 쓰지 않기 위해 선형 합동 생성기로 의사난수 생성
    seed = 12345
    data = []
    for _ in range(size):
        seed = (1103515245 * seed + 12345) % 2147483648
        data.append(seed)

    lines = [f"n = {size}"]
    for name, algorithm in (
        ("merge_sort    ", merge_sort),
        ("insertion_sort", insertion_sort),
    ):
        start = time.perf_counter()
        algorithm(data)
        elapsed = time.perf_counter() - start
        lines.append(f"  {name} : {elapsed * 1000:9.2f} ms")
    lines.append("  (merge O(n log n) vs insertion O(n^2))")
    return "\n".join(lines)


def cmd_help(repo: Repository, args, options) -> str:
    """HELP - 사용 가능한 명령 목록을 출력한다."""
    return HELP_TEXT


HANDLERS = {
    "init": cmd_init,
    "user": cmd_user,
    "branch": cmd_branch,
    "switch": cmd_switch,
    "commit": cmd_commit,
    "merge": cmd_merge,
    "log": cmd_log,
    "path": cmd_path,
    "ancestors": cmd_ancestors,
    "search": cmd_search,
    "bench": cmd_bench,
    "help": cmd_help,
}


def execute(repo: Repository, line: str) -> str | None:
    """한 줄을 실행하고 출력 문자열을 반환한다. None이면 출력 없음."""
    parsed = parse_line(line)
    if parsed is None:
        return None

    command, args, options = parsed
    if command in EXIT_COMMANDS:
        raise SystemExit(0)

    handler = HANDLERS.get(command)
    if handler is None:
        raise MiniGitError(f"Unknown command: {command}")

    return handler(repo, args, options)


def run_repl() -> None:
    """명령 파싱 -> 실행 -> 결과 출력을 반복하는 REPL."""
    repo = Repository()
    print("Mini Git. Type HELP for commands, EXIT to quit.")

    while True:
        try:
            line = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            output = execute(repo, line)
        except SystemExit:
            break
        except MiniGitError as exc:
            print(f"Error: {exc}")
            continue
        except RecursionError:
            print("Error: History is too deep to process")
            continue

        if output:
            print(output)

    print("Bye.")