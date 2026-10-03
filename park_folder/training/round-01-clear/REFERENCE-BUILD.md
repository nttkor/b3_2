# B3-2 R01 — Reference Build

## 목적

공식 Mission/Evaluation을 기준으로 **DAG 기반 commit graph + branch pointer + graph traversal + custom sorting + inverted index**를 직접 구현한 CLI Mini Git 기준본을 준비합니다.

Reference Build가 완료되어도 Phase C에서 실제 REPL/자동 검증/Evidence를 확인하기 전에는 `✅ CLEAR`로 판정하지 않습니다.

## Source of Truth

1. `b3-2-mission.pdf`
2. `b3-2-mission.md`
3. `b3-2-evaluation.md`

## Reference 설계 결정

- Python 3.10+
- 그래프 전용 라이브러리 사용 안 함
- `sorted()`, `list.sort()` 사용 안 함
- Commit hash: 세션 내 증가 카운터 기반 (`c000001`, ...)
- Commit repository: `dict[hash, Commit]`
- Branch: `dict[branch_name, commit_hash | None]`
- HEAD 역할: 현재 branch 이름을 보관하는 `head_branch`
- Inverted Index: keyword/author → commit hash list
- keyword token: whitespace `split()` + `lower()`
- 기본 LOG: parent를 먼저 방문하는 DFS 성격의 ordering
- LOG sort: 직접 구현 stable merge sort, 평균/최악 O(n log n)
- PATH: parent-child를 undirected edge로 보고 BFS distance 계산
- shortest path tie: distance가 1 감소하는 후보 중 hash 사전순 최소 선택
- ANCESTORS: parent 방향 traversal
- CLI: `shlex.split()` quoted string + case-insensitive command
- persistence/file-content/network는 공식 필수 범위 밖이므로 추가하지 않음

## Reference Complete Path

1. Commit / repository / branch / HEAD 모델
2. INIT / BRANCH / SWITCH / COMMIT
3. unique hash 및 inverted index 갱신
4. LOG parent-first
5. custom stable merge sort
6. PATH BFS shortest + lexicographic tie-break
7. ANCESTORS
8. SEARCH keyword/author
9. CLI syntax/error contract
10. edge/boundary tests
11. verifier / constraints scan
12. Evaluation Q&A
13. Runtime Evidence
14. CLEAR

## 자체감사에서 보강한 항목

- [x] 세션 내 다수 commit hash uniqueness test
- [x] branch divergence에서 parent-first LOG 검증
- [x] disconnected roots를 이용한 `No path` test
- [x] multi-parent DAG를 이용한 shortest-path lexicographic tie-break test
- [x] multi-parent ANCESTORS 누락/중복 방지 test
- [x] keyword case normalization + repeated token duplicate 방지 test
- [x] stable merge sort의 equal-key 상대 순서 test
- [x] date/author repository sort 및 invalid sort test
- [x] malformed quote / invalid args / unknown branch/commit/command test
- [x] verifier를 AST parse 방식으로 변경해 검증 부작용 최소화
- [x] `sorted()` / `.sort()` / graph library 금지 검사 강화
- [x] tracked Secret-pattern filename scan
- [x] `--runtime` Evidence Gate 설계
- [x] Evaluation 확장 질문까지 문서화
- [x] Beginner Guide / Checklist / Mapping / Evidence / Status 동기화
- [x] 실제 Runtime 결과를 PASS로 가장하지 않음

## Phase C에서만 완료할 것

- [ ] Python 3.10+ 실제 환경 확인
- [ ] `environment/verify.sh` 실제 0 FAIL
- [ ] INIT/BRANCH/SWITCH/COMMIT 실제 REPL
- [ ] 기본 LOG parent-before-child 실제 확인
- [ ] date/author sort 실제 확인
- [ ] PATH shortest / disconnected `No path`
- [ ] ANCESTORS
- [ ] SEARCH keyword/author
- [ ] 대표 오류
- [ ] Runtime Evidence
- [ ] 사용자 자기 말 Evaluation 설명
- [ ] `✅ B3-2 CLEAR`

## 현재 판정

**Reference Build: CORE READY**  
**Mission 상태: ⬜ NOT STARTED 유지 / Runtime 미시작 / CLEAR 아님**

다음 Phase A 자체감사 대상은 **B4-1**입니다.
