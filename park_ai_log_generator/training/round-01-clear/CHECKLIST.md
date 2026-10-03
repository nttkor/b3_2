# B6-2 Round 01 — Mission Clear Checklist

## 현재 상태

- Reference Build: **CORE READY**
- Runtime Mission: ⬜ NOT STARTED
- 별도 `b6-2-evaluation.md`: **없음** — 공식 Mission 요구사항을 검증 기준으로 사용

## Source / Learn

- [x] `b6-2-mission.pdf` 확인
- [x] `b6-2-mission.md` 확인
- [x] 필수/선택/보너스/Runtime 분리
- [x] Git/AI API/Prompt/Commit/PR 핵심 개념 준비
- [x] Beginner Guide 단계별 경로 준비

## Git Input

- [x] Git repository 확인 로직
- [x] `git status --short`
- [x] unstaged `git diff`
- [x] staged `git diff --cached`
- [x] no-change early exit
- [ ] 실제 Git working tree Runtime

## AI API / Secret

- [x] `AI_API_KEY` 환경변수
- [x] `AI_API_URL` 환경변수
- [x] Key 하드코딩 금지
- [x] Network/Auth/Timeout/JSON 오류 처리
- [x] `--model`
- [x] `--temperature`
- [x] `--max-tokens`
- [ ] 실제 Provider endpoint/model 확인
- [ ] 실제 API Key local input
- [ ] 실제 AI API 호출

## Commit

- [x] `commit` command
- [x] 실제 diff context Prompt
- [x] 제목 1줄 validator
- [x] 제목 최대 72자 검증
- [x] 본문 사용 시 구체적 bullet/파일 맥락 검증
- [ ] 실제 AI Commit 생성 결과
- [ ] 실제 Commit 적용

## Pull Request

- [x] `pr` command
- [x] PR 제목
- [x] `## Why`
- [x] `## What`
- [x] `## How to Test`
- [x] 각 섹션 bullet 1개 이상
- [x] PR 제목 최대 80자 검증
- [x] 확인하지 않은 테스트 PASS 주장 금지
- [ ] 실제 AI PR 초안
- [ ] 실제 GitHub PR 적용

## Tests / Verify

- [x] Prompt/Validator 테스트 설계
- [x] no-change 테스트
- [x] option propagation 테스트
- [x] missing-key/error 테스트
- [x] disposable Git repo collector 검증
- [x] Secret-like pattern scan
- [ ] `environment/verify.sh` 실제 `0 FAIL`
- [ ] 실제 API Runtime 정상 경로
- [ ] 실제 API Runtime 오류 경로

## Docs / Evidence

- [x] Requirements Mapping
- [x] Q&A Reference
- [x] Evidence Guide
- [x] canonical Beginner Guide
- [x] canonical Checklist
- [ ] Root README 최종 사용 가이드와 일치
- [ ] 실제 generated Commit Evidence
- [ ] 실제 generated PR Evidence
- [ ] 실제 Commit/PR 링크
- [ ] 실제 API 오류 Evidence
- [ ] Secret 노출 없음 최종 확인

## CLEAR Gate

- [ ] 공식 Mission 필수 요구사항 누락 없음
- [ ] Offline verify PASS
- [ ] 실제 AI API 호출 PASS
- [ ] 실제 diff 기반 Commit 생성/적용
- [ ] 실제 diff 기반 PR 생성/적용
- [ ] README/Evidence 완료
- [ ] 사용자가 Git→Prompt→API→Validator→Human Review 흐름을 자기 말로 설명
- [ ] Secret 노출 없음
- [ ] **✅ B6-2 CLEAR**

Reference 구현이나 문서가 존재한다는 이유만으로 CLEAR하지 않습니다.
