# Git Commit Conventions

## 1. Commit Type
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정 (README, EVALUATION_PLAN 등)
- `test`: 테스트 코드 추가 및 수정
- `refactor`: 코드 리팩토링 (기능 변경 없음)
- `style`: 코드 포맷팅, 세미콜론 누락 등
- `chore`: 빌드 업무 수정, 패키지 매니저 수정 등

## 2. Commit Format & Detailed Body Guidelines
커밋 메시지만 보고도 전체 작업 맥락과 수정 사항을 완벽히 이해할 수 있도록 본문을 최대한 상세히 기록한다.

```text
<type>: <제목 (50자 이내 권장, 최대 72자, 마침표 없음)>

- 배경(Why): 변경을 수행하게 된 원인, 요구사항 또는 발생했던 결함
- 상세 변경점(What):
  - [파일명/모듈]: 구체적으로 수정한 함수, 클래스, 로직 상세 설명
  - [파일명/모듈]: 추가되거나 변경된 설정값 및 엔드포인트
- 영향 및 개선점(Impact): 변경 후 해결된 문제와 코드 안정성 향상 결과
- 검증 내역(Verification): 실행한 테스트 명령어, 통과한 테스트 케이스 및 검증 증빙
```
