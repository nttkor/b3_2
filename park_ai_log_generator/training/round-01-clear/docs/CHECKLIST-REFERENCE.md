# B6-2 R01 — Reference / Runtime Checklist

## 현재 상태

- Mission 상태: ⬜ NOT STARTED
- Phase A: REFERENCE BUILD

## A. Source

- [x] Mission PDF/MD 확인
- [x] Evaluation 확인
- [x] 필수 Runtime 항목 분리

## B. Git Input

- [x] Git repo 확인
- [x] `git status --short`
- [x] unstaged `git diff`
- [x] staged `git diff --cached`
- [x] no-change early exit
- [ ] 실제 Git working tree Runtime

## C. AI API / Secret

- [x] `AI_API_KEY` env
- [x] `AI_API_URL` env
- [x] Key hardcode 없음
- [x] HTTP/network/timeout/JSON 오류 처리
- [x] `--model`
- [x] `--temperature`
- [x] `--max-tokens`
- [ ] 실제 Provider endpoint 확인
- [ ] 실제 API Key local input
- [ ] 실제 API 호출 성공

## D. Commit

- [x] `commit` command
- [x] TITLE 1줄 validator
- [x] concrete BODY bullet 1+
- [x] actual diff context prompt
- [ ] 실제 AI 생성 결과
- [ ] 실제 Commit 적용

## E. PR

- [x] `pr` command
- [x] PR TITLE
- [x] `## Why`
- [x] `## What`
- [x] `## How to Test`
- [x] section별 bullet 1+
- [x] unverified test pass claim 금지 prompt
- [ ] 실제 AI PR 초안
- [ ] 실제 GitHub PR 적용

## F. Tests / Verify

- [x] prompt tests
- [x] validator tests
- [x] no-change test
- [x] option propagation test
- [x] missing-key test
- [x] PR generation test
- [x] disposable Git repo collector verify
- [x] secret-like pattern scan
- [ ] 실제 offline verify 0 FAIL
- [ ] 실제 API Runtime test

## G. Docs / Evidence

- [x] Reference usage guide
- [x] Environment guide
- [x] Requirements mapping
- [x] Evaluation Q&A
- [x] Evidence Guide
- [x] Beginner Reference Guide
- [ ] README 실제 제출 가이드와 일치 확인
- [ ] 실제 generated commit Evidence
- [ ] 실제 generated PR Evidence
- [ ] actual Commit/PR links
- [ ] actual API error Evidence
- [ ] Secret 노출 없음

## H. Evaluation

- [x] status/diff 연동 설명
- [x] staged/unstaged 차이
- [x] no-change 이유
- [x] API Key env 이유
- [x] model/temperature/max tokens 설명
- [x] Commit prompt 설계
- [x] PR Why/What/How 설계
- [x] human review 필요성
- [x] API 오류 구분
- [x] 품질 검증 기준
- [x] provider abstraction 설명
- [ ] 사용자가 실제 Runtime 결과로 자기 말 설명

## I. CLEAR

- [ ] 공식 Mission 누락 없음
- [ ] 공식 Evaluation 누락 없음
- [ ] Offline verify PASS
- [ ] 실제 API 호출 PASS
- [ ] 실제 Commit 생성/적용
- [ ] 실제 PR 생성/적용
- [ ] README/Evidence 완료
- [ ] Secret 노출 없음
- [ ] **✅ B6-2 CLEAR**
