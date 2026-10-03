# B3-2 Round 01 — Mission Clear Checklist

> Mission 상태는 `⬜ NOT STARTED`, `🟡 ACTIVE`, `⛔ BLOCKED`, `✅ CLEAR`만 사용합니다. 현재는 Phase A Reference Build이며 실제 Runtime/Evidence는 아직 수행하지 않습니다.

## 현재 상태

- Training Round: **R01 — CLEAR**
- Mission: **B3-2**
- Mission 상태: **⬜ NOT STARTED**
- 작업 모드: **Phase A — REFERENCE BUILD**

## A. Source

- [x] `b3-2-mission.pdf` 확인
- [x] `b3-2-mission.md` 확인
- [x] `b3-2-evaluation.md` 확인
- [x] 필수/보너스 분리
- [x] Runtime 항목 분리

## B. Repository / Commit Graph

- [x] Python 3.10+ 기준
- [x] `Commit(hash, message, author, timestamp, parents)`
- [x] commit hash 빠른 조회 구조
- [x] 세션 내 unique monotonic hash
- [x] parent list로 DAG 표현
- [x] cycle guard
- [x] `main` branch
- [x] HEAD 역할의 `head_branch`
- [x] branch는 commit pointer
- [ ] Runtime에서 실제 pointer 변화 확인

## C. Required Commands

- [x] INIT
- [x] BRANCH
- [x] SWITCH
- [x] COMMIT
- [x] LOG
- [x] PATH
- [x] ANCESTORS
- [x] SEARCH keyword
- [x] SEARCH `--author=`
- [x] LOG `--sort-by=date`
- [x] LOG `--sort-by=author`
- [x] exit / quit REPL
- [ ] 실제 REPL 명령 확인

## D. LOG / Sorting

- [x] 기본 LOG parent-before-child
- [x] parent-first DFS 구조
- [x] 직접 구현 stable merge sort
- [x] 평균 O(n log n)
- [x] 최악 O(n log n)
- [x] stable 조건
- [x] `sorted()` 미사용
- [x] `list.sort()` 미사용
- [x] AST verifier
- [ ] Runtime LOG Evidence

## E. PATH / ANCESTORS

- [x] PATH parent-child를 undirected edge로 사용
- [x] BFS distance
- [x] start == target
- [x] disconnected graph `No path`
- [x] 여러 shortest path 중 lexicographic minimum 규칙
- [x] ANCESTORS parent-direction traversal
- [x] multi-parent DAG ancestor 중복 제거 test
- [ ] Runtime PATH/ANCESTORS 확인

## F. Inverted Index

- [x] keyword → commit hashes
- [x] author → commit hashes
- [x] message whitespace split
- [x] lowercase normalization
- [x] repeated keyword token duplicate 방지
- [x] author case-insensitive lookup
- [ ] Runtime SEARCH 확인

## G. CLI / Error Contract

- [x] command case-insensitive
- [x] quoted user/message/author 지원
- [x] `Invalid args`
- [x] `Unknown branch: <name>`
- [x] `Unknown commit: <hash>`
- [x] `Unknown command: <name>`
- [x] invalid sort option 처리
- [x] malformed quote 처리
- [ ] Runtime 오류 Evidence

## H. Constraints / Code Quality

- [x] graph 전용 library 사용 안 함
- [x] `sorted()` / `.sort()` 금지 자동검사
- [x] graph/sort/index logic 모듈 분리
- [x] Commit/algorithm/repository 핵심 책임 분리
- [x] 주요 class/function docstring 또는 설명 존재
- [x] file content tracking 구현 안 함
- [x] network 구현 안 함
- [x] persistence를 불필요하게 추가하지 않음
- [x] B3-2에 실제 Secret 불필요

## I. Reference Tests / Verification

- [x] INIT/branch/switch/commit graph test
- [x] 50 commits unique hash test
- [x] diverged branch parent-first LOG test
- [x] PATH cross-branch test
- [x] PATH disconnected `No path` test
- [x] PATH equal-distance lexicographic tie test
- [x] multi-parent ANCESTORS test
- [x] inverted index case/duplicate-token test
- [x] stable merge sort equal-key order test
- [x] date/author repository sort test
- [x] CLI/error boundary tests
- [x] side-effect-light AST verifier
- [x] Secret-pattern filename scan
- [x] Runtime Evidence Gate 설계
- [ ] 실제 `verify.sh` 결과 0 FAIL

## J. Evaluation 설명

- [x] commit graph가 DAG인 이유
- [x] branch / HEAD pointer 구조
- [x] hash lookup / unique hash 전략
- [x] inverted index 갱신 시점
- [x] LOG parent-first 알고리즘
- [x] BFS shortest path / undirected edge 이유
- [x] merge sort 복잡도와 stable 여부
- [x] inverted index vs full scan
- [x] commit 10배 증가 병목
- [x] PATH를 parent-only로 변경할 때의 차이
- [x] author sort + parent-before-child 동시 제약 전략
- [x] counter vs random hash의 test/reproducibility 차이
- [ ] 사용자가 실제 코드 근거로 자기 말 설명

## K. Documentation / Evidence

- [x] `REFERENCE-BUILD.md`
- [x] `REFERENCE-STATUS.md`
- [x] 상세 `BEGINNER-GUIDE.md`
- [x] `reference/README.md`
- [x] `docs/requirements-mapping.md`
- [x] `docs/evaluation-qa.md`
- [x] `evidence/README.md`
- [x] `environment/verify.sh`
- [ ] `evidence/runtime/verify.txt`
- [ ] `evidence/runtime/repl.txt`
- [ ] `evidence/runtime/evaluation.md`

## L. Final CLEAR

- [ ] 공식 Mission 누락 없음 최종 확인
- [ ] 공식 Evaluation 누락 없음 최종 확인
- [ ] Reference test/verify 실제 PASS
- [ ] 핵심 REPL Runtime 완료
- [ ] parent-first LOG 실제 확인
- [ ] PATH shortest / No path 실제 확인
- [ ] ANCESTORS 실제 확인
- [ ] SEARCH / sort 실제 확인
- [ ] 오류 Runtime 완료
- [ ] Evidence 완료
- [ ] 설명형 평가 대응 가능
- [ ] **✅ B3-2 CLEAR**
