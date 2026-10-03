# B6-2 Round 01 — Beginner Guide

구분: **필수 미션 (REQUIRED)**

> Phase A에서 완성한 Reference 기준 가이드입니다. 실제 AI API Key 입력/호출과 실제 Commit/PR 적용은 Phase C에서 수행합니다. 이 저장소에는 별도 `b6-2-evaluation.md`가 없으므로 공식 검증 기준은 `b6-2-mission.pdf`와 `b6-2-mission.md`입니다.

## 미션 한눈에 보기

Git 변경사항을 `git status`/`git diff`로 수집하고, Python CLI가 AI API에 전달하여 Commit Message와 Pull Request 초안을 생성합니다. AI가 만든 텍스트는 형식 검증 후 사람이 검토하고 실제 Git 작업에 적용합니다.

```text
Git 변경사항 → Python CLI → Prompt → AI API → 형식 검증 → 사람 검토 → Commit / PR
```

핵심 원칙은 **Secret 비노출**, **실제 diff 기반 생성**, **변경 없음 시 API 미호출**, **AI 결과 무검토 자동 적용 금지**입니다.

## STEP 01 — Git 변경사항 이해

① 왜 하는가: AI가 요약할 실제 근거를 확보합니다.  
② 무엇을 하는가: `git status --short`, `git diff`, `git diff --cached`를 구분합니다.  
③ 이번 단계에서 알아야 할 용어: 작업 트리 (Working Tree), 스테이징 영역 (Staging Area), 차이 (Diff).  
④ 필요한 핵심 개념: unstaged + staged 변경을 함께 봐야 현재 작업 전체를 이해할 수 있습니다.  
⑤ 실행할 명령어:
```bash
git status --short
git diff
git diff --cached
```
⑥ 주석: `--cached`는 이미 staging된 변경의 diff입니다.  
⑦ 예상 정상 결과: 변경 파일 목록과 line diff가 보입니다.  
⑧ 의미: 이 내용이 AI Prompt의 근거가 됩니다.  
⑨ 오류와 해결: Git 저장소가 아니라면 프로젝트 루트로 이동합니다.  
⑩ 완료 확인: status와 staged/unstaged diff 차이를 설명할 수 있습니다.

## STEP 02 — CLI 구조와 변경 없음 경로

① 왜 하는가: 변경이 없는데 AI API를 호출하면 불필요한 비용과 요청이 발생합니다.  
② 무엇을 하는가: CLI help와 no-change early exit 구조를 확인합니다.  
③ 용어: 명령줄 인터페이스 (CLI), 조기 종료 (Early Return).  
④ 개념: 입력 근거가 없으면 생성 작업도 시작하지 않습니다.  
⑤ 실행할 명령어:
```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 -m git_ai --help
```
⑥ 주석: `commit`과 `pr` subcommand, model/temperature/max-tokens 옵션을 확인합니다.  
⑦ 정상 결과: CLI help가 출력됩니다.  
⑧ 의미: 프로그램의 입력 계약을 확인했습니다.  
⑨ 오류와 해결: import 실패 시 현재 경로와 `PYTHONPATH`를 확인합니다.  
⑩ 완료 확인: 변경이 없으면 `변경 사항이 없습니다.`를 출력하고 API를 호출하지 않는 이유를 설명합니다.

## STEP 03 — Secret과 API Runtime 설정

① 왜 하는가: API Key가 Git 기록이나 문서에 노출되는 것을 막습니다.  
② 무엇을 하는가: endpoint와 Key를 환경변수로만 제공합니다.  
③ 용어: 환경변수 (Environment Variable), API Key, 비밀정보 (Secret).  
④ 개념: Source Code와 Credential을 분리합니다.  
⑤ 실행할 명령어:
```bash
export AI_API_URL="<runtime-endpoint>"
export AI_API_KEY="<local-secret-only>"
```
⑥ 주석: 실제 값은 README, GitHub, 채팅, Evidence에 복사하지 않습니다.  
⑦ 정상 결과: 프로세스가 환경변수에서 값을 읽습니다.  
⑧ 의미: Secret이 repository history에 남지 않습니다.  
⑨ 오류와 해결: Key 누락 시 사용자용 오류가 나와야 하며 실제 Key를 출력해서는 안 됩니다.  
⑩ 완료 확인: Secret 값 노출 없이 설정 방법을 설명할 수 있습니다.

## STEP 04 — Commit Message 생성

① 왜 하는가: 실제 diff를 근거로 의미 있는 Commit 문장을 생성합니다.  
② 무엇을 하는가: `commit` 명령을 실행합니다.  
③ 용어: 프롬프트 (Prompt), 문맥 (Context), Temperature.  
④ 개념: Prompt에 status/diff, 출력 형식, 근거 없는 내용 생성 금지를 함께 넣습니다.  
⑤ 실행할 명령어:
```bash
python3 -m git_ai commit --model "<runtime-model>" --temperature 0.2 --max-tokens 700
```
⑥ 주석: 실제 model과 parameter 범위는 Runtime provider가 지원하는 값을 사용합니다.  
⑦ 정상 결과: 제목 1줄과 필요한 경우 본문 bullet이 출력됩니다.  
⑧ 의미: Git 변경이 사람이 검토 가능한 자연어 설명으로 변환되었습니다.  
⑨ 오류와 해결: 제목 길이·형식 실패 시 validator가 오류를 표시해야 합니다.  
⑩ 완료 확인: 생성 내용이 실제 diff와 일치하는지 사람이 확인합니다.

## STEP 05 — Pull Request 초안 생성

① 왜 하는가: Reviewer가 변경 배경·내용·검증 방법을 빠르게 이해하도록 합니다.  
② 무엇을 하는가: `pr` 명령을 실행합니다.  
③ 용어: 풀 리퀘스트 (Pull Request), 템플릿 (Template).  
④ 개념: PR 본문은 `Why`, `What`, `How to Test`를 고정 구조로 사용합니다.  
⑤ 실행할 명령어:
```bash
python3 -m git_ai pr --model "<runtime-model>" --temperature 0.2 --max-tokens 900
```
⑥ 주석: 실제 검증 Evidence가 없다면 테스트가 통과했다고 주장하면 안 됩니다.  
⑦ 정상 결과: PR 제목과 3개 섹션, 각 섹션 bullet 1개 이상이 출력됩니다.  
⑧ 의미: PR 형식과 실제 diff 문맥이 연결되었습니다.  
⑨ 오류와 해결: 필수 섹션이나 bullet 누락 시 validator 오류를 확인합니다.  
⑩ 완료 확인: PR 초안이 실제 변경과 일치합니다.

## STEP 06 — API 오류 대응

① 왜 하는가: Network/Auth/Timeout/JSON 문제는 해결 방법이 서로 다릅니다.  
② 무엇을 하는가: API 실패 유형별 사용자 오류 처리를 확인합니다.  
③ 용어: HTTP 401/403, 타임아웃 (Timeout), JSON.  
④ 개념: 오류를 숨기지 말되 Credential은 노출하지 않습니다.  
⑤ 실행: Phase C의 안전한 Runtime에서 잘못된 endpoint 또는 무효 credential case를 별도로 확인합니다.  
⑥ 주석: 실제 credential을 터미널 캡처나 Evidence에 포함하지 않습니다.  
⑦ 정상 결과: 오류 category와 원인을 이해할 수 있는 메시지가 표시됩니다.  
⑧ 의미: 실패가 조용히 삼켜지지 않고 진단 가능합니다.  
⑨ 오류와 해결: raw provider 응답에 민감정보가 없는지 확인하고 필요한 부분만 Evidence에 남깁니다.  
⑩ 완료 확인: 인증·Network·Timeout·응답 형식 오류를 구분합니다.

## STEP 07 — Offline Verify

① 왜 하는가: 실제 API 비용 없이 구조와 핵심 로직을 먼저 검증합니다.  
② 무엇을 하는가: unit test, 임시 Git repo, Secret scan 등을 실행합니다.  
③ 용어: 모의 객체 (Mock), 단위 테스트 (Unit Test), 스모크 테스트 (Smoke Test).  
④ 개념: Offline PASS와 실제 AI API PASS는 별개입니다.  
⑤ 실행할 명령어:
```bash
bash training/round-01-clear/environment/verify.sh
```
⑥ 주석: 이 단계는 실제 AI API 호출 성공을 증명하지 않습니다.  
⑦ 정상 결과: `Result: N PASS / 0 FAIL`.  
⑧ 의미: 자동 검증 가능한 Reference 범위를 통과했습니다.  
⑨ 오류와 해결: FAIL 항목만 수정한 뒤 다시 실행합니다.  
⑩ 완료 확인: Offline verify가 0 FAIL입니다.

## STEP 08 — 실제 적용과 CLEAR

① 왜 하는가: AI 텍스트 생성만으로는 공식 미션의 전체 흐름이 완료되지 않습니다.  
② 무엇을 하는가: 실제 Git diff로 Commit/PR을 생성하고 사람이 검토한 뒤 실제 workflow에 적용합니다.  
③ 용어: 사람 개입 검토 (Human-in-the-loop), 증빙 (Evidence).  
④ 개념: `AI 생성 → 자동 형식 검증 → 사람 검토 → 실제 Git 적용` 순서를 지킵니다.  
⑤ 실행 예:
```bash
git commit
# GitHub에서 실제 PR 작성
```
⑥ 주석: AI가 만든 문장을 무검토 자동 적용하지 않습니다.  
⑦ 정상 결과: 실제 Commit history와 PR 본문에 검토된 결과가 반영됩니다.  
⑧ 의미: Git + AI API + Prompt + 협업 흐름이 하나로 연결되었습니다.  
⑨ 오류와 해결: diff와 생성 결과가 다르면 Prompt/Context/Validator를 수정합니다.  
⑩ 완료 확인: 실제 API, Commit, PR, README, Evidence, 자기 말 설명이 완료된 뒤에만 `✅ CLEAR`로 판정합니다.

## CLEAR 전에 반드시 확인

- 실제 API Key는 저장소/채팅/Evidence에 없음
- 실제 Git diff 기반 Commit 생성 결과 존재
- 실제 Git diff 기반 PR 초안 존재
- Commit 제목 최대 72자, PR 제목 최대 80자 검증
- PR Why/What/How to Test와 bullet 존재
- API 오류 경로 실제 확인
- README에 설치·환경변수·사용 예·출력 예·보안 또는 비용 주의사항 포함
- `environment/verify.sh` 0 FAIL
- `docs/requirements-mapping.md`와 Evidence가 연결됨

Reference 파일의 존재만으로는 `✅ CLEAR`가 아닙니다.
