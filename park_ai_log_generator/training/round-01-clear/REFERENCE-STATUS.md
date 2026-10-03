# B6-2 R01 — Reference Status

## 판정

**Reference Build: CORE READY**  
**Runtime Mission: ⬜ NOT STARTED**  
**Runtime CLEAR: 아님**

## 공식 Source

- `b6-2-mission.pdf`
- `b6-2-mission.md`
- 별도 공식 Evaluation 파일 없음

`docs/evaluation-qa.md`는 Mission 요구사항을 바탕으로 만든 설명 연습 자료이며 공식 평가 원본으로 취급하지 않습니다.

## Phase A 준비 결과

- [x] Mission 요구사항 분석
- [x] Git status/staged/unstaged diff collector
- [x] no-change early exit
- [x] env-only API Key/endpoint
- [x] REST AI client
- [x] Network/Auth/Timeout/JSON 오류 처리
- [x] `commit` / `pr` CLI
- [x] model/temperature/max-tokens options
- [x] Commit/PR Prompt와 format validator
- [x] unit/offline tests와 `verify.sh`
- [x] Secret-like pattern scan
- [x] Requirement Mapping / Q&A / Evidence Guide
- [x] canonical `BEGINNER-GUIDE.md`
- [x] canonical `CHECKLIST.md`
- [x] Reference/Runtime 구분

## Phase C에서만 완료

- [ ] 실제 Provider endpoint/model
- [ ] 실제 API Key local input
- [ ] 실제 AI API call
- [ ] 실제 diff 기반 Commit 생성/적용
- [ ] 실제 diff 기반 PR 생성/적용
- [ ] 실제 오류 경로
- [ ] Runtime Evidence
- [ ] 사용자의 자기 말 설명
- [ ] `✅ B6-2 CLEAR`

## Canonical Audit

기존 scaffold `BEGINNER-GUIDE.md`와 `CHECKLIST.md`를 상세 Reference 가이드와 동기화했고, 존재하지 않는 `b6-2-evaluation.md` 참조를 제거했습니다.
