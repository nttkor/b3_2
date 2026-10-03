# B3-2 R01 — Reference Status

## 판정

**Reference Build: CORE READY**  
**Runtime Mission 상태: ⬜ NOT STARTED**

Reference 구현·테스트·학습가이드·검증계획이 준비되었다는 뜻이며 실제 REPL/Evidence가 완료되었다는 뜻은 아닙니다.

## 공식 Source

- `b3-2-mission.pdf`
- `b3-2-mission.md`
- `b3-2-evaluation.md`

## CORE READY 근거

### Commit / Branch

- Commit: hash/message/author/timestamp/parents
- session-unique monotonic hash
- hash → Commit lookup
- branch → commit hash pointer
- current `head_branch`
- DAG parent representation / cycle guard

### Algorithms

- 기본 LOG parent-before-child
- custom stable merge sort
- `sorted()` / `.sort()` 미사용 검증
- PATH BFS shortest path
- undirected parent-child edge
- shortest path lexicographic tie-break
- ANCESTORS parent-direction traversal

### Search

- keyword inverted index
- author inverted index
- split/lower normalization
- duplicate token suppression

### Boundary Tests

- 50 commit unique hash
- branch divergence parent-first LOG
- disconnected roots `No path`
- equal-length PATH lexical tie
- multi-parent ANCESTORS
- stable sort equal-key order
- invalid sort/quote/args/branch/commit/command

### Verification / Docs

- side-effect-light AST syntax parser
- unit test runner
- standard sort API + graph-library scan
- required-command smoke test
- tracked Secret-pattern scan
- `--runtime` Evidence Gate
- Requirement Mapping
- Evaluation Q&A
- detailed Beginner Guide / Checklist / Evidence Guide

## Phase C에서만 PASS할 항목

- 실제 `verify.sh` 0 FAIL
- 실제 REPL
- branch pointer 변화
- parent-first LOG
- date/author sort
- PATH shortest + No path
- ANCESTORS
- SEARCH keyword/author
- 오류 시나리오
- 사용자 Evaluation 자기 말 설명
- `evidence/runtime/*`

## Gate

- [x] Source/Evaluation 매핑
- [x] 최소 충분 Reference 구현
- [x] algorithm/constraint 검사 설계
- [x] edge case test 설계
- [x] Reference/Runtime 엄격 분리
- [x] Evidence 계획
- [x] 허위 Runtime PASS 없음
- [x] BLOCKER/MAJOR 설계 결함 없음

따라서 Phase A 기준으로 **CORE READY**입니다. 실제 `✅ CLEAR`는 Phase C Runtime 후에만 가능합니다.
