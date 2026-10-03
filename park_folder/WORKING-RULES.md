# B5-2 작업 룰(Working Rules)

> 현재 제2기 Mission: **B5-2 — 파일이 언제 어떻게 바뀌었는지 기록하는 작은 프로그램 만들기**  
> 과거 Repository Mission ID: `B3-2`  
> **기준 레포(Canonical Control Repository):** [MetaStudy999/codyssey-basic](https://github.com/MetaStudy999/codyssey-basic)

이 파일은 현재 미션의 **얇은 작업 운영 어댑터(Thin Working Rules Adapter)** 이다. 공통 규칙 전문은 기준 레포에서 관리하고 이 Repository에는 미션별 연결과 현재 Round만 둔다.

## 기준 우선순위

```text
제2기 현재 Mission PDF
→ 제2기 오리엔테이션 PDF
→ 이 Repository의 기존 Mission
→ 기존 Evaluation
→ training/round-01-clear 참고자료
→ 일반 지식·외부 자료
```

현재 번호·제목·공식 요구사항은 제2기 현재 Mission PDF를 따른다. 과거 번호 파일은 동일 주제의 1기 참고자료로 보존한다.

## 현재 Round

- 기존 참고: `training/round-01-clear/`
- 제2기 신규 수행: `training/round-02-clear/`
- 시작 문서: [training/round-02-clear/README.md](training/round-02-clear/README.md)
- 진행 체크: [training/round-02-clear/CHECKLIST.md](training/round-02-clear/CHECKLIST.md)
- 공통 표준: [ROUND-02-MISSION-EXECUTION-STANDARD.md](https://github.com/MetaStudy999/codyssey-basic/blob/main/standards/ROUND-02-MISSION-EXECUTION-STANDARD.md)

## 빠른 적용

```text
공식 기준 확정
→ 평가항목 먼저
→ 최소 통과 경로
→ 필요한 개념만 학습
→ round-02-clear에서 한 단계씩 실제 실행
→ Verification + Evidence
→ 평가 설명
→ 모의평가
→ 조건 충족 시에만 B5-2 CLEAR
```

## 상태 원칙

```text
문서 존재 ≠ Runtime PASS
Runtime PASS ≠ Verification PASS
Verification PASS ≠ Evidence Complete
Evidence Complete ≠ Evaluation Ready
위 조건 미충족 ≠ Mission CLEAR
```

사용자의 실제 실행 결과 없이 PASS/CLEAR를 기록하지 않는다. Round 01의 과거 PASS/Evidence를 Round 02 실제 결과로 대신하지 않는다.

## 오류·보안

오류는 **원인 확인 → 최소 수정 → 재실행 → 검증** 순서로 처리하고, 정상 환경을 무조건 재설치하지 않는다.

Password, API Key, Token, Private Key, Secret, Cloud Credential을 Repository·Chat·Evidence에 노출하지 않는다.
