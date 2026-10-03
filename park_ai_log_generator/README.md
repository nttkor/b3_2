# Codyssey Basic B6-2 — AI Code Summarizer

## 구분

- 필수 미션 (REQUIRED)
- Round: **R01 — CLEAR**
- Reference Build: **CORE READY**
- Runtime Mission: ⬜ NOT STARTED

## 시작 위치

`training/round-01-clear/BEGINNER-GUIDE.md`

## 공식 원본

- `b6-2-mission.pdf`
- `b6-2-mission.md`

현재 저장소에는 별도 공식 Evaluation 파일이 없습니다. Mission 요구사항 자체를 최종 검증 기준으로 사용합니다.

## Reference 핵심

Git의 staged/unstaged 변경을 수집하여 Python CLI가 AI API로 Commit Message와 PR 초안을 생성합니다. API Key는 환경변수로만 관리하며 Commit/PR 형식을 Validator로 검사하고, 최종 적용 전 사람이 검토합니다.

## R01 흐름

`Mission → 용어/개념 → Git diff → CLI/Prompt → AI API → Validator → Human Review → 실제 Commit/PR → Evidence → CLEAR`

실제 API 호출, Commit/PR 적용, Runtime Evidence가 완료되기 전에는 `✅ CLEAR`로 변경하지 않습니다.
