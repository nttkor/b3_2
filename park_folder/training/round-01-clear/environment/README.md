# B3-2 R01 Environment

## Golden Path

- Python 3.10+
- 외부 graph library 없음
- Reference 실행: `python3 training/round-01-clear/reference/main.py`
- `sorted()` / `list.sort()` 사용 금지
- 정렬은 직접 구현 stable merge sort 사용
- B3-2는 외부 Secret/API Key가 필요하지 않음

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

## Reference 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

검사 항목:

- Python 3.10+
- 필수 파일
- AST 문법 parse
- unit tests
- `sorted()` / `.sort()` 금지
- graph-specific library import 금지
- required command smoke
- tracked Secret-pattern filename

검증기가 불필요한 bytecode를 만들지 않도록 `compileall` 대신 AST parse와 `PYTHONDONTWRITEBYTECODE=1`을 사용합니다.

## Runtime Evidence Gate

Phase C에서 실제 결과를 만든 뒤:

```bash
bash training/round-01-clear/environment/verify.sh --runtime
```

추가 확인:

```text
evidence/runtime/verify.txt
evidence/runtime/repl.txt
evidence/runtime/evaluation.md
```

Reference verify가 통과해도 실제 REPL/Evidence를 수행하기 전에는 `✅ CLEAR`가 아닙니다.
