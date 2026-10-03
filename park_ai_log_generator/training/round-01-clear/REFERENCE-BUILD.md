# B6-2 R01 — Reference Build

## 목적

공식 Mission을 기준으로 **Git 변경사항을 수집해 AI API에 전달하고 Commit Message와 Pull Request 초안을 생성하는 Python CLI**의 Reference Complete Version을 준비합니다.

Phase A에서는 실제 API Key를 입력하거나 유료 AI API를 호출하지 않습니다. 실제 Provider/API Runtime, 생성 품질, Commit/PR 적용과 Evidence는 Phase C에서 확인합니다.

## Source of Truth

1. `b6-2-mission.pdf`
2. `b6-2-mission.md`

> 현재 저장소에는 별도 `b6-2-evaluation.md`가 없습니다. 따라서 Mission의 기능 요구사항·제약사항·최종 결과물·설명 목표를 검증 기준으로 사용합니다. `docs/evaluation-qa.md`는 공식 평가문항이 아니라 Mission 기반 설명 연습 자료입니다.

## Reference 설계 결정

- Python 3.10+
- 실행: `python -m git_ai <commit|pr> [options]`
- Git root에서 실행
- `git status --short`, `git diff`, `git diff --cached` 수집
- 변경이 없으면 AI 호출 없이 `변경 사항이 없습니다.` 출력 후 종료
- `AI_API_KEY`, `AI_API_URL`은 환경변수
- 실제 Key/Token/Secret 하드코딩 금지
- CLI 옵션: `--model`, `--temperature`, `--max-tokens`
- Commit: 제목 1줄, 최대 72자, 본문 사용 시 구체적 변경 bullet
- PR: 제목 최대 80자 + `Why`/`What`/`How to Test`, 각 bullet 1개 이상
- Network/Auth/Timeout/JSON/형식 오류를 사용자에게 구분해 전달
- 확인하지 않은 테스트 성공을 AI가 주장하지 않도록 Prompt/Validator에서 방지

## Reference Complete Path

1. Git repository 확인
2. status/staged/unstaged diff 수집
3. no-change 종료
4. Prompt Context 구성
5. REST AI client + env Secret
6. model/temperature/max-tokens CLI
7. Commit Prompt + Validator
8. PR Prompt + Validator
9. 오류 처리
10. Offline tests/verify
11. 실제 API Runtime
12. 실제 Commit/PR 적용
13. README/Evidence/자기 설명
14. CLEAR

## Phase A 판정

**Reference Build: CORE READY / Mission 상태 ⬜ NOT STARTED / 실제 AI API Runtime 미시작 / CLEAR 아님**
