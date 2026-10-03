# B6-2 R01 — Requirement / Implementation / Verification / Evidence

| ID | Requirement | Reference Implementation | Verification | Evidence |
|---|---|---|---|---|
| R01 | Git root에서 실행 | `ensure_git_repository()` | temp git repo / Runtime | terminal |
| R02 | `git status` 수집 | `git_tools.py` | disposable repo verify | output |
| R03 | `git diff` 수집 | unstaged + staged diff | disposable repo verify | output |
| R04 | 변경 없음 메시지/종료 | `GitChanges.has_changes` | unit test | terminal |
| R05 | API Key env | `AI_API_KEY` | missing-key test/Runtime | env setup |
| R06 | Key hardcode 금지 | no credential in code | secret scan | verify result |
| R07 | AI API call | `AIClient.generate()` | Phase C real API | generated output |
| R08 | API error reason | HTTP/network/JSON handlers | unit/integration/Runtime | error output |
| R09 | model option | CLI `--model` | unit | help/output |
| R10 | temperature option | CLI `--temperature` | unit | help/output |
| R11 | max tokens option | CLI `--max-tokens` | unit | help/output |
| R12 | commit title 1 line | commit prompt/validator | unit/Runtime | generated commit |
| R13 | commit concrete body | bullet validator/prompt | unit/Runtime | generated commit |
| R14 | PR title/body | PR prompt/validator | unit/Runtime | generated PR |
| R15 | PR Why/What/How to Test | exact headers | validator | generated PR |
| R16 | each PR section bullet | validator | unit/Runtime | generated PR |
| R17 | prompt contains change context | `prompts.py` | unit | prompt/code |
| R18 | actual commit/PR workflow application | Phase C | git/GitHub history | commit/PR link |
| R19 | README run/env/examples/cautions | root/reference docs | document review | README |
| R20 | explanation of parameters/prompt/automation | `evaluation-qa.md` | user explanation | evaluator check |

## Phase C 핵심

실제 API Key/Provider를 local environment에만 설정하고 commit/pr 두 command를 실제 호출합니다. 생성된 text가 format validator를 통과하고 실제 diff를 반영하는지 사람이 읽어 검증한 뒤 복사해 Git commit/PR workflow에 적용합니다.
