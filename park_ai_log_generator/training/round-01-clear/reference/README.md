# B6-2 Git AI Reference

## 목적

현재 Git 작업 트리의 `git status`, unstaged/staged `git diff`를 수집해 AI API에 전달하고 Commit Message 또는 Pull Request 초안을 생성합니다.

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 -m git_ai --help
```

실제 Runtime:

```bash
export AI_API_URL="<provider-compatible-endpoint>"
export AI_API_KEY="<local-secret-only>"
python3 -m git_ai commit --model "<runtime-model>" --temperature 0.2 --max-tokens 700
python3 -m git_ai pr --model "<runtime-model>" --temperature 0.2 --max-tokens 900
```

## Commit 출력 형식

```text
TITLE: <one line>
BODY:
- <concrete change>
```

## PR 출력 형식

```text
TITLE: <PR title>
## Why
- ...
## What
- ...
## How to Test
- ...
```

## 안전 원칙

- 실제 API Key 하드코딩 금지
- 실제 Key/.env/Token GitHub 저장 금지
- diff가 없으면 API 호출하지 않음
- Prompt는 실제 status/diff만 근거로 생성
- 테스트를 실제 수행한 증거가 없으면 `passed`라고 쓰지 않음
- generated text는 사용자가 읽고 실제 Git command/PR에 적용

## API Adapter

Reference는 endpoint를 `AI_API_URL`로 주입하고 Bearer token 방식의 REST 요청을 사용합니다. 기본 parser는 OpenAI-compatible `choices[0].message.content` 또는 gateway의 top-level `output_text`를 읽습니다. 실제 Provider의 endpoint/모델/지원 parameter는 Phase C에서 선택한 Provider 문서에 맞춰 확인합니다.
