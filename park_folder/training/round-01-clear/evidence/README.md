# B3-2 R01 — Evidence Guide

## 원칙

Evidence는 `Requirement → Implementation → Verification → Evidence` 순서로 연결합니다. Reference 코드·unit test가 존재한다는 이유만으로 실제 Runtime을 PASS 처리하지 않습니다.

B3-2에는 Password/API Key/Token/Private Key가 필요하지 않습니다. 불필요한 Secret을 만들거나 Evidence에 저장하지 않습니다.

## Runtime Evidence 최소 구조

Phase C에서 실제 실행할 때만 생성합니다.

```text
evidence/runtime/
├── verify.txt
├── repl.txt
└── evaluation.md
```

## 1. 자동 검증

```bash
mkdir -p training/round-01-clear/evidence/runtime
bash training/round-01-clear/environment/verify.sh \
  | tee training/round-01-clear/evidence/runtime/verify.txt
```

실제 마지막 결과가 `Result: N PASS / 0 FAIL`인지 확인합니다.

## 2. 핵심 REPL 시나리오

실제 생성 hash를 사용하며 예시 hash를 Evidence로 가장하지 않습니다.

```text
INIT "Alice Kim"
COMMIT "root commit"
BRANCH left
BRANCH right
SWITCH left
COMMIT "add login feature"
COMMIT "fix login validation"
SWITCH right
COMMIT "add profile page"
LOG
LOG --sort-by=date
LOG --sort-by=author
PATH <left-tip> <right-tip>
ANCESTORS <left-tip>
SEARCH login
SEARCH LOGIN
SEARCH --author="Alice Kim"
```

다음을 확인합니다.

- branch는 commit 복사가 아니라 pointer
- hash/message/author/timestamp/parents 식별 가능
- 기본 LOG에서 모든 parent가 child보다 먼저
- date/author custom sort
- PATH는 branch 사이 shortest path
- ANCESTORS는 parent 방향만 탐색
- SEARCH는 keyword/author index 결과

## 3. `No path` 시나리오

정상 CLI만으로도 첫 commit 전에 branch를 나누면 disconnected roots를 만들 수 있습니다.

```text
INIT alice
BRANCH other
COMMIT "main root"
SWITCH other
COMMIT "other root"
PATH c000001 c000002
```

정상 결과:

```text
No path
```

## 4. 오류 Evidence

```text
COMMIT
SWITCH missing
PATH c999999 c000001
LOG --sort-by=message
SEARCH
HELLO
```

상황에 따라 다음 계약을 확인합니다.

- `Invalid args`
- `Unknown branch: <name>`
- `Unknown commit: <hash>`
- `Unknown command: <name>`
- `No path`

## 5. 금지 API / 라이브러리

`verify.sh`의 AST 검사로 Mini Git core에 다음이 없는지 확인합니다.

- `sorted()`
- `.sort()`
- graph-specific library import

## 6. 설명형 평가

`evaluation.md`에는 최소한 다음 질문을 자기 말로 답합니다.

- commit graph가 DAG인 이유
- branch/HEAD pointer
- parent-first LOG
- BFS shortest path와 undirected edge
- stable merge sort 복잡도/안정성
- inverted index
- 10배 규모 병목
- parent-only PATH 변경
- author sort에 parent-before-child 제약 추가
- counter vs random hash

## 7. Runtime Gate

세 파일을 실제 결과로 채운 뒤:

```bash
bash training/round-01-clear/environment/verify.sh --runtime
```

`--runtime`은 Evidence 파일이 실제로 존재하고 비어 있지 않은지 추가로 확인합니다.

## CLEAR

다음이 모두 확인되기 전에는 `✅ CLEAR`가 아닙니다.

- Reference verify 실제 0 FAIL
- 실제 REPL 기능/오류 결과
- parent-first LOG
- shortest PATH + No path
- ANCESTORS
- SEARCH / custom sort
- Evaluation 자기 말 설명
- Evidence 완료
