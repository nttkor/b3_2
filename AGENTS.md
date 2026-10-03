# 전역 규칙 (Always-On Rules)

## [7대 핵심 운영 규칙]

1. **계획 수립 및 원스톱 자율 실행 (Autonomous Execution)**
   - 계획 승인 후 파일 단위로 중간 확인을 묻지 않고 완료 시까지 끝까지 일괄 처리.

2. **작업 완료 후 자동 Git 커밋 (Auto Commit, No Auto Push)**
   - 테스트 통과 후 즉시 컨벤션(`docs/CONVENTIONS.md`)에 맞춰 로컬 자동 커밋 (`<type>: <description>`).
   - 커밋 메시지 본문에는 변경 배경, 수정된 구체적인 파일 및 로직, 해결된 문제, 검증 결과를 최대한 상세히 기록하여 커밋 로그만 보고도 작업 맥락을 완벽히 파악할 수 있도록 작성.
   - **원격 저장소 푸시(`git push`)는 절대 자동으로 실행하지 않으며, 사용자가 명시적으로 요청할 때만 수행.**

3. **최종 보고 및 시간 기록 (Final Reporting with Timestamp)**
   - 작업 완료 시 현재 로컬 시각(KST) 및 clickable한 `file://` 마크다운 링크 포함 종합 보고.

4. **코드 및 문서 작성 기준**
   - 기존 주석/로직 100% 보존, 상세 docstring(Args, Returns, Raises), 보안 원칙(CSRF, Argon2id, XSS, hide_parameters) 엄수.

5. **전역 규칙 파일 상호 동기화 관리 (Dual Rule Synchronization)**
   - `GEMINI.md`와 `AGENTS.md` 두 파일은 100% 동일한 내용으로 상시 자동 동기화 유지.

6. **공통 유틸리티 재사용 원칙 (Reusable Utils)**
   - 프롬프트 처리 시 매번 일회성 파이썬 코드를 즉석 생성하지 않고, `backend/app/utils/`에 모듈화하여 재활용.

7. **작업 메모리(아티팩트) 우선 참조 원칙 (Memory First Execution)**
   - 새로운 작업 시 `find`, `grep` 등으로 전체 리포지토리를 반복 스캔하지 않고, 안티그래비티 자체 작업 메모리(`activity_log.md`)를 최우선 참조하여 즉시 파일로 접근하여 작업.
