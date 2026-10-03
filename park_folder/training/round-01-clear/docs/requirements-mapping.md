# B3-2 R01 — Requirement / Implementation / Verification / Evidence

실제 Runtime을 하지 않은 항목은 Evidence 완료로 표시하지 않습니다.

| ID | Requirement | Reference Implementation | Verification | Runtime Evidence |
|---|---|---|---|---|
| R01 | `INIT <user_name>` | `repository.py:init` | unit/smoke | init 출력 |
| R02 | main branch + HEAD + current user | `branches`, `head_branch`, `current_user` | unit | init 상태 설명 |
| R03 | BRANCH current HEAD pointer | `branch()` | unit/REPL | branch 출력 |
| R04 | SWITCH | `switch()` | unit/REPL | switch 출력 |
| R05 | COMMIT fields | `Commit`, `commit()` | unit/REPL | commit/LOG |
| R06 | session unique hash | monotonic counter | 50-commit uniqueness unit | LOG |
| R07 | 0+ parents / DAG representation | `parents: list[str]` | multi-parent tests + cycle guard | graph 설명 |
| R08 | hash fast lookup | `dict[str, Commit]` | code/unit | 평가 설명 |
| R09 | keyword inverted index | split/lower → hashes | case/duplicate-token unit | SEARCH |
| R10 | author inverted index | lower author → hashes | unit | SEARCH `--author` |
| R11 | 기본 LOG parent-before-child | parent-first DFS | diverged branch unit | LOG |
| R12 | `LOG --sort-by=date` | custom stable merge sort | unit/REPL | LOG |
| R13 | `LOG --sort-by=author` | custom stable merge sort | unit/REPL | LOG |
| R14 | no `sorted()` / `.sort()` | AST verifier | verify | verify.txt |
| R15 | graph library 금지 | AST import scan | verify | verify.txt |
| R16 | custom sort complexity/stability | `stable_merge_sort` | equal-key unit + Q&A | evaluation.md |
| R17 | PATH shortest, undirected | BFS distance | cross-branch unit | PATH |
| R18 | PATH same commit | `path()` | unit | PATH |
| R19 | PATH disconnected → `No path` | distance reachability | disconnected-roots unit | REPL |
| R20 | shortest tie lexicographic minimum | decreasing-distance + lexical neighbor | equal-length multi-parent unit | evaluation 설명 |
| R21 | ANCESTORS all parents | parent-direction traversal | multi-parent unique unit | ANCESTORS |
| R22 | command case-insensitive | `command.upper()` | CLI unit | REPL |
| R23 | quoted strings | `shlex.split()` | CLI unit | INIT/COMMIT/SEARCH |
| R24 | option syntax | CLI `--author=`, `--sort-by=` | CLI unit | REPL |
| R25 | `Invalid args` | parser/error contract | CLI unit | 오류 출력 |
| R26 | Unknown branch/commit | `MiniGitError` | unit/CLI | 오류 출력 |
| R27 | unknown command | `execute()` | CLI unit | 오류 출력 |
| R28 | entry point + REPL | `main.py`, `cli.repl()` | runtime | prompt/exit |
| R29 | algorithm responsibilities separated | models/algorithms/repository/cli | code review | 평가 설명 |
| R30 | file content/network/persistence not required | intentionally omitted | scope audit | README |
| R31 | scale bottleneck analysis | Evaluation Q&A | explanation | evaluation.md |
| R32 | parent-only PATH change | Evaluation Q&A | explanation | evaluation.md |
| R33 | author sort + dependency change | Evaluation Q&A | explanation | evaluation.md |
| R34 | counter vs random hash tradeoff | Evaluation Q&A | explanation | evaluation.md |
| R35 | Secret unnecessary | no credential dependency | tracked filename scan | verify.txt |

## Phase C Runtime 시나리오

1. `INIT` → root `COMMIT`
2. branch 2개 생성·전환·commit
3. 기본 `LOG` parent-first 확인
4. `LOG --sort-by=date`, `LOG --sort-by=author`
5. branch 사이 `PATH`
6. 별도 세션에서 disconnected roots → `No path`
7. `ANCESTORS`
8. `SEARCH keyword`, `SEARCH --author=`
9. Invalid args / Unknown branch / Unknown commit / Unknown command
10. `verify.sh` 실제 `0 FAIL`
11. Evaluation 자기 말 설명

## Evidence 최소 세트

```text
evidence/runtime/
├── verify.txt
├── repl.txt
└── evaluation.md
```

Reference unit test 작성 사실만으로 실제 Runtime PASS를 대신하지 않습니다.
