# B3-2 Mini Git Reference

## 상태

- Reference Build: **CORE READY**
- Runtime Mission: **⬜ NOT STARTED**
- 실제 REPL/Evidence 전이므로 `✅ CLEAR` 아님

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

종료: `exit`, `quit`, Ctrl+D, Ctrl+C.

## 필수 명령

```text
INIT <user_name>
BRANCH <branch_name>
SWITCH <branch_name>
COMMIT <message>
LOG
LOG --sort-by=date
LOG --sort-by=author
PATH <commit1> <commit2>
ANCESTORS <commit_hash>
SEARCH <keyword>
SEARCH --author=<name>
```

공백이 있는 문자열은 큰따옴표를 사용합니다.

```text
INIT "Alice Kim"
COMMIT "Add login feature"
SEARCH --author="Alice Kim"
```

## 내부 구조

```text
mini_git/
├── models.py       # Commit node
├── algorithms.py   # custom stable merge sort / lexical helper
├── repository.py   # DAG, branch pointers, indexes, graph traversal
└── cli.py          # parser + REPL
```

## Commit DAG / Branch / HEAD

Commit은 `hash`, `message`, `author`, `timestamp`, `parents`를 가집니다. 일반 COMMIT은 현재 HEAD를 부모로 갖고, 첫 commit은 부모가 없습니다. 자료구조는 `parents: list[str]`이므로 multi-parent DAG도 표현할 수 있습니다.

branch는 commit 복사본이 아니라 commit hash를 가리키는 pointer입니다.

```text
branches["main"] = "c000003"
head_branch = "main"
```

Commit hash는 session-local monotonic counter를 사용해 `c000001`, `c000002`처럼 중복 없이 생성합니다.

## LOG

기본 `LOG`는 parent-first DFS 성격으로 동작합니다. commit을 출력하기 전에 parent를 먼저 방문하여 parent-before-child를 보장합니다. 방문 중 같은 node를 다시 만나면 cycle invariant violation으로 처리합니다.

`LOG --sort-by=date|author`는 직접 구현한 **stable merge sort**를 사용합니다.

- 평균: O(n log n)
- 최악: O(n log n)
- stable: Yes
- `sorted()` / `list.sort()` 사용 안 함

공식 현재 요구에서 기본 LOG의 parent-before-child와 `--sort-by` 정렬은 별도 기능입니다.

## PATH

parent-child 연결을 **undirected edge**로 보고 shortest path를 찾습니다.

1. target에서 BFS distance 계산
2. source에서 distance가 1씩 감소하는 neighbor만 선택
3. 후보 중 hash가 lexicographically smallest인 neighbor 선택

따라서 여러 shortest path가 있으면 hash sequence가 사전순으로 가장 작은 경로를 선택합니다.

정상 CLI만으로 `No path`도 만들 수 있습니다. 첫 commit 전에 branch를 만들고 각 빈 branch에서 독립 root commit을 생성하면 graph component가 분리됩니다.

## ANCESTORS

지정 commit에서 `parents` 방향으로만 탐색해 모든 ancestor를 중복 없이 반환합니다. PATH와 달리 child 방향으로 내려가지 않습니다.

## Inverted Index

COMMIT 시점에 다음 index를 갱신합니다.

```text
keyword -> [commit_hash, ...]
author  -> [commit_hash, ...]
```

keyword는 공식 최소 기준대로 message를 whitespace split하고 lowercase합니다. 같은 token이 한 message에 반복돼도 동일 commit hash는 한 번만 등록합니다.

## 주요 확장 병목

현재 PATH neighbor 계산은 child를 찾을 때 commit 전체를 훑습니다. commit 수가 크게 늘면 `parent -> children` adjacency index를 추가하는 것이 주요 개선 방향입니다.

## 금지사항

- `sorted()`
- `list.sort()`
- graph-specific library

기본 `list`, `dict`, `set`은 공식 B3-2에서 허용됩니다.

## 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

Phase C Evidence가 준비된 뒤:

```bash
bash training/round-01-clear/environment/verify.sh --runtime
```
