# B6-2 Round 01 — Beginner Guide Reference

> Phase A용 Reference 가이드입니다. 실제 AI API Key 입력/호출과 Git Commit/PR 적용은 Phase C에서 수행합니다.

## STEP 01 — Git 변경사항 이해

① 왜 하는가: AI가 요약할 실제 근거를 확보합니다.  
② 무엇: `git status --short`, `git diff`, `git diff --cached`를 구분합니다.  
③ 용어: Working Tree, Staging Area, Diff.  
④ 개념: unstaged + staged 변경을 합쳐야 현재 작업 전체를 볼 수 있습니다.  
⑤ 명령:
```bash
git status --short
git diff
git diff --cached
```
⑥ 주석: `--cached`는 staged diff입니다.  
⑦ 정상 결과: 변경 파일과 line diff가 보입니다.  
⑧ 의미: AI prompt의 실제 입력 근거입니다.  
⑨ 오류: Git repo가 아니면 project root로 이동합니다.  
⑩ 완료: status/diff 차이를 설명할 수 있습니다.

## STEP 02 — CLI 구조와 no-change 경로

① 왜: 변경이 없으면 API 비용을 쓰지 않아야 합니다.  
② 무엇: `collect_changes()`와 `has_changes`를 확인합니다.  
③ 용어: CLI, Early Return.  
④ 개념: 입력이 없으면 생성도 하지 않습니다.  
⑤ 명령:
```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 -m git_ai --help
```
⑥ 주석: `commit`/`pr` 두 subcommand와 model/temperature/max-tokens 옵션을 확인합니다.  
⑦ 정상: help 출력.  
⑧ 의미: 실행 계약을 확인했습니다.  
⑨ 오류: import 실패 시 PYTHONPATH 확인.  
⑩ 완료: no-change 시 `변경 사항이 없습니다.` 경로를 이해합니다.

## STEP 03 — Secret과 API Runtime 설정

① 왜: API Key 노출을 막습니다.  
② 무엇: Key와 endpoint를 환경변수로만 제공합니다.  
③ 용어: Environment Variable, API Key, Secret.  
④ 개념: Code와 credential을 분리합니다.  
⑤ 명령:
```bash
export AI_API_URL="<runtime-endpoint>"
export AI_API_KEY="<local-secret-only>"
```
⑥ 주석: 실제 값을 README/GitHub/Evidence에 복사하지 않습니다.  
⑦ 정상: process가 env에서 값을 읽습니다.  
⑧ 의미: Secret이 repository history에 남지 않습니다.  
⑨ 오류: Key missing은 사용자용 오류로 종료합니다.  
⑩ 완료: 실제 값 노출 없이 설정 방법을 설명할 수 있습니다.

## STEP 04 — Commit Message 생성

① 왜: 실제 diff를 근거로 의미 있는 Commit 문장을 만듭니다.  
② 무엇: `commit` command를 실행합니다.  
③ 용어: Prompt, Context, Temperature.  
④ 개념: Prompt에 status/diff + 출력 형식 + hallucination 금지 규칙을 함께 넣습니다.  
⑤ 명령:
```bash
python3 -m git_ai commit --model "<runtime-model>" --temperature 0.2 --max-tokens 700
```
⑥ 주석: model/temperature/max-tokens는 Runtime provider 지원 범위를 확인합니다.  
⑦ 정상: `TITLE:` 1줄과 BODY bullet.  
⑧ 의미: Git 변경이 자연어 요약으로 변환되었습니다.  
⑨ 오류: format 실패는 validator가 막습니다.  
⑩ 완료: 실제 diff와 생성 내용이 일치하는지 사람이 확인합니다.

## STEP 05 — PR 초안 생성

① 왜: Reviewer가 변경 배경/내용/검증 방법을 빠르게 이해하게 합니다.  
② 무엇: `pr` command를 실행합니다.  
③ 용어: Pull Request, Template.  
④ 개념: Why/What/How to Test를 고정합니다.  
⑤ 명령:
```bash
python3 -m git_ai pr --model "<runtime-model>" --temperature 0.2 --max-tokens 900
```
⑥ 주석: 실제 테스트 증거가 없으면 `passed`라고 주장하지 않습니다.  
⑦ 정상: TITLE + 3 sections, 각 bullet 1+.  
⑧ 의미: PR 형식과 diff 맥락이 연결되었습니다.  
⑨ 오류: section 누락은 validator 오류.  
⑩ 완료: PR draft가 실제 변경과 일치합니다.

## STEP 06 — API 오류 대응

① 왜: Network/Auth 실패를 구분해야 해결할 수 있습니다.  
② 무엇: HTTP/network/timeout/JSON/empty response 오류를 확인합니다.  
③ 용어: HTTP 401/403, Timeout, JSON.  
④ 개념: 원인 종류마다 복구 방법이 다릅니다.  
⑤ 명령: 안전한 Runtime에서 잘못된 endpoint 또는 invalid credential case를 별도로 재현할 수 있습니다.  
⑥ 주석: 실제 credential은 출력하지 않습니다.  
⑦ 정상: `[ERROR]` 뒤에 원인 category가 보입니다.  
⑧ 의미: 실패가 조용히 삼켜지지 않습니다.  
⑨ 오류: raw provider response에 Secret이 포함되는지 확인하고 Evidence에는 필요한 부분만 남깁니다.  
⑩ 완료: 인증/Network/format 오류를 구분합니다.

## STEP 07 — Offline Verify

① 왜: API 비용 없이 구조와 핵심 로직을 먼저 검증합니다.  
② 무엇: unit/compile/temp Git repo/Secret scan을 실행합니다.  
③ 용어: Mock, Unit Test, Smoke Test.  
④ 개념: Offline PASS와 Real API PASS는 별개입니다.  
⑤ 명령:
```bash
bash training/round-01-clear/environment/verify.sh
```
⑥ 주석: 실제 API 호출은 하지 않습니다.  
⑦ 정상: `Result: N PASS / 0 FAIL`.  
⑧ 의미: 자동 검증 가능한 Reference 범위를 통과했습니다.  
⑨ 오류: FAIL 항목만 수정 후 재실행합니다.  
⑩ 완료: Offline verify 0 FAIL.

## STEP 08 — 실제 Commit/PR 적용과 CLEAR

① 왜: AI text 생성만으로 미션이 끝나지 않고 실제 Git workflow에 적용되는지 확인해야 합니다.  
② 무엇: 생성 결과를 검토 후 실제 Commit/PR에 사용하고 Evidence를 연결합니다.  
③ 용어: Human-in-the-loop, Evidence.  
④ 개념: AI → 자동 format 검증 → 사람 검토 → 실제 Git 적용 순서입니다.  
⑤ 명령 예:
```bash
git commit
# 실제 GitHub PR 작성
```
⑥ 주석: AI가 만든 문장을 무검토 자동 적용하지 않습니다.  
⑦ 정상: 실제 commit history와 PR body에 반영됩니다.  
⑧ 의미: Git + AI API + prompt + 협업 흐름이 연결되었습니다.  
⑨ 오류: diff와 생성 결과가 다르면 prompt/context/output을 수정합니다.  
⑩ 완료: 실제 API, Commit, PR, README, Evidence, 평가 설명 후에만 `✅ CLEAR`.
