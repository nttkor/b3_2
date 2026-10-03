# B6-2 R01 — Evaluation Q&A Reference

## 1. Git 변경사항을 프로그램 입력으로 어떻게 연결하는가?

Python에서 `subprocess.run()`으로 `git status --short`, `git diff`, `git diff --cached`를 실행하고 stdout을 문자열로 수집합니다. status는 변경 파일을 빠르게 보여 주고 diff는 실제 line-level 변경 내용을 제공합니다.

## 2. staged/unstaged diff를 모두 보는 이유는?

`git diff`만 보면 아직 stage하지 않은 변경만 보이고, `git diff --cached`는 staged 변경을 보여 줍니다. Commit/PR 초안이 현재 작업 전체를 놓치지 않도록 두 범위를 구분해 prompt context에 넣습니다.

## 3. 변경이 없을 때 왜 AI API를 호출하지 않는가?

입력 근거가 없으면 의미 있는 Commit/PR을 만들 수 없고 API 비용/시간만 소비합니다. 따라서 status/diff가 모두 비어 있으면 `변경 사항이 없습니다.`라고 알려 주고 종료합니다.

## 4. API Key를 환경변수로 두는 이유는?

소스코드나 Git history에 Secret을 넣으면 repository를 공유하는 순간 credential이 노출될 수 있습니다. Runtime process가 environment에서 읽도록 하면 code와 Secret을 분리할 수 있습니다.

## 5. model, temperature, max_tokens는 무엇을 조절하는가?

- `model`: 어떤 AI model을 호출할지 선택합니다.
- `temperature`: provider가 지원할 경우 생성 다양성/확률 분포에 영향을 줍니다.
- `max_tokens`: 생성 결과 최대 길이를 제한합니다.

실제 지원 parameter 이름/범위는 선택한 Provider의 현재 API 문서를 확인해야 합니다.

## 6. Commit prompt에 무엇을 넣어야 품질이 좋아지는가?

실제 status/diff와 출력 format을 함께 줍니다. `TITLE` 한 줄, concrete body bullet처럼 형식을 고정하고 변경하지 않은 파일/테스트를 만들어내지 말라는 규칙을 넣으면 결과 검증이 쉬워집니다.

## 7. PR prompt에 Why/What/How to Test를 넣는 이유는?

PR reviewer가 변경 배경, 실제 변경, 검증 방법을 빠르게 이해하기 위한 최소 구조입니다. 세 section마다 bullet을 요구하면 내용이 비어 있는 형식만 생성되는 것을 줄일 수 있습니다.

## 8. AI 결과를 그대로 git commit/PR에 자동 적용하지 않는 이유는?

AI가 diff를 잘못 요약하거나 실행하지 않은 테스트를 통과했다고 쓸 수 있습니다. B6-2 Reference는 생성 text를 terminal에 출력하고 format을 자동 검증한 뒤 사람이 실제 diff와 비교해 적용하는 안전한 경로를 사용합니다.

## 9. API 인증 실패와 Network 실패를 왜 구분해야 하는가?

401/403 같은 인증/권한 문제는 Key/계정/endpoint를 확인해야 하고 DNS/timeout은 Network 경로를 확인해야 합니다. 원인이 다른데 `API 호출 실패` 한 줄로만 표시하면 해결 방향을 잡기 어렵습니다.

## 10. Prompt injection 같은 위험은 이 미션에서 어떻게 생각해야 하는가?

Git diff 안의 text는 외부/사용자 입력일 수 있으므로 prompt의 지시와 data context를 구분해야 합니다. Reference는 system-style rule에 `supplied diff를 근거로만 요약`하도록 명시하지만, production에서는 structured input, content filtering, output validation, permission boundary가 더 필요합니다.

## 11. 생성 품질을 어떻게 검증하는가?

1. 실제 변경 파일/모듈을 언급하는가
2. 핵심 변경을 빠뜨리지 않았는가
3. 없는 테스트/기능을 만들어내지 않았는가
4. Commit title/PR section format을 만족하는가
5. 사람이 복사해도 팀 convention에 맞는가

자동 format validator와 human review를 함께 사용합니다.

## 12. API Provider를 endpoint 환경변수로 분리한 이유는?

Mission은 특정 Provider가 아니라 AI API 연동 원리를 평가합니다. Endpoint/Key/model을 Runtime 설정으로 분리하면 code를 크게 바꾸지 않고 호환 endpoint를 교체할 수 있습니다. 다만 실제 Provider별 request parameter와 response schema는 Runtime에서 현재 문서에 맞춰 확인해야 합니다.
