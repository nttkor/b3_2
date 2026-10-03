# Codyssey Basic B3-2 — Mini Git

## 현재 훈련 상태

- 구분: **필수 미션 (REQUIRED)**
- Round: **R01 — CLEAR**
- Runtime Mission 상태: **⬜ NOT STARTED**
- 현재 모드: **Phase A — REFERENCE BUILD**
- Reference 판정: **CORE READY**

Reference Complete Version은 준비되었지만 실제 REPL/검증/Evidence를 아직 수행하지 않았으므로 `✅ CLEAR`가 아닙니다.

## 공식 원본

- `b3-2-mission.pdf`
- `b3-2-mission.md`
- `b3-2-evaluation.md`

공식 원본은 수정하지 않습니다.

## 시작 위치

1. `training/round-01-clear/REFERENCE-STATUS.md`
2. `training/round-01-clear/REFERENCE-BUILD.md`
3. `training/round-01-clear/BEGINNER-GUIDE.md`
4. `training/round-01-clear/CHECKLIST.md`
5. `training/round-01-clear/reference/README.md`

## Reference 구조

```text
training/round-01-clear/
├── REFERENCE-STATUS.md
├── REFERENCE-BUILD.md
├── BEGINNER-GUIDE.md
├── CHECKLIST.md
├── reference/
│   ├── main.py
│   ├── mini_git/
│   │   ├── models.py
│   │   ├── algorithms.py
│   │   ├── repository.py
│   │   └── cli.py
│   └── tests/test_mini_git.py
├── environment/verify.sh
├── docs/
└── evidence/
```

## 구현된 필수 범위

- INIT / BRANCH / SWITCH / COMMIT
- LOG parent-before-child
- `LOG --sort-by=date|author`
- PATH shortest path + lexicographic tie-break
- ANCESTORS
- keyword/author Inverted Index SEARCH
- quoted strings / case-insensitive commands
- standard CLI errors
- custom stable merge sort
- graph-library 및 standard sort API 제약 검사

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

## Reference 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

실제 Runtime Evidence가 준비된 뒤에는:

```bash
bash training/round-01-clear/environment/verify.sh --runtime
```

## CLEAR 원칙

Reference 코드와 tests가 존재한다는 이유만으로 CLEAR하지 않습니다. Phase C에서 실제 REPL, parent-first LOG, PATH/No path, ANCESTORS, SEARCH, custom sort, 오류 처리, Evaluation 설명과 Evidence를 확인한 뒤 `✅ CLEAR`로 변경합니다.
