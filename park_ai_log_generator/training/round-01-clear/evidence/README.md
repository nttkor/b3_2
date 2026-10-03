# B6-2 R01 — Evidence Guide

## 1. Offline verify

```bash
bash training/round-01-clear/environment/verify.sh
```

실제 `Result: N PASS / 0 FAIL`을 저장합니다.

## 2. Git change collection

실제 테스트 branch에서 파일 하나를 수정하고:

```bash
git status --short
git diff
git diff --cached
```

CLI가 같은 변경 맥락을 기반으로 동작하는지 확인합니다.

## 3. No-change path

깨끗한 working tree에서:

```bash
python3 -m git_ai commit
```

API 호출 없이 `변경 사항이 없습니다.`가 표시되는지 확인합니다.

## 4. Secret setup

실제 local shell에만:

```bash
export AI_API_URL="<runtime-endpoint>"
export AI_API_KEY="<secret-input-only>"
```

Evidence에는 변수 이름/설정 방법만 남기고 실제 값은 마스킹 또는 미포함합니다.

## 5. Commit generation

```bash
python3 -m git_ai commit \
  --model "<runtime-model>" \
  --temperature 0.2 \
  --max-tokens 700
```

Evidence:

- TITLE 한 줄
- BODY concrete bullet
- 실제 diff와 일치
- 없는 테스트/파일 주장 없음

## 6. PR generation

```bash
python3 -m git_ai pr \
  --model "<runtime-model>" \
  --temperature 0.2 \
  --max-tokens 900
```

Evidence:

- TITLE
- `## Why` + bullet
- `## What` + bullet
- `## How to Test` + bullet

## 7. Error path

가능하면 실제 안전한 범위에서 잘못된 endpoint/인증 등으로 오류 원인을 확인합니다. 실제 Secret 자체는 출력하지 않습니다.

## 8. Actual Git/GitHub application

생성된 text를 사람이 검토한 뒤:

- 실제 Commit message 적용
- 실제 PR title/body 적용
- 관련 Commit/PR URL 기록

## 9. README

평가자가 README만 보고 다음을 확인할 수 있어야 합니다.

- 설치/실행
- env variable
- commit/pr examples
- parameter options
- generated output example
- Secret/운영 주의사항

## CLEAR

Mock/Unit Test 결과만으로 CLEAR하지 않습니다. 실제 API 호출과 실제 diff 기반 생성 품질, 실제 Commit/PR 적용까지 확인합니다.
