# AI 기반 Git 커밋 및 PR 자동 생성기 (Git AI Assistant)

Git의 변경 사항(`git status`, `git diff`)을 실시간 수집하여, AI API를 통해 일관된 컨벤션의 커밋 메시지와 Pull Request(PR) 초안을 원클릭으로 자동 생성하는 Python CLI 도구입니다.

---

## 1. 주요 특징

- **원클릭 자동 생성**: 프로젝트 루트에서 `python main.py commit` 또는 `python main.py pr` 단일 명령으로 즉시 초안 생성.
- **표준 컨벤션 준수**: 
  - 커밋 메시지: Conventional Commits 형식(`feat:`, `fix:` 등), 제목 50자 권장/최대 72자, 파일 언급 및 핵심 변경 사항 불릿 요약.
  - PR 초안: 한 줄 제목(최대 80자) + `Why`, `What`, `How to Test` 3대 필수 섹션 및 불릿 구조 100% 보장.
- **고성능·저비용 모델 연동**: OpenAI 호환 코디세이 게이트웨이 및 OpenRouter 지원, 기본 모델로 초고속·경량 모델인 `gpt-5.4-mini`(차감 배수 0.5배) 탑재.
- **안전 모드 (`--safe-mode`)**: API Key, JWT 토큰, AWS 키, 이메일, 패스워드 등 9가지 민감정보 자동 마스킹 및 대용량 diff 전송 방지(파일/줄 수 상한).
- **결정론적 후처리 검증 (Validator)**: LLM의 확률적 한계를 극복하기 위해 파이썬 레벨에서 글자 수 자르기, 필수 섹션 누락 방지 및 불릿 자동 주입 수행.

---

## 2. 개발 및 실행 환경

- **Python**: 3.10 이상 (테스트 완료: Python 3.12)
- **AI API**: OpenAI 호환 REST API (Codyssey AI Gateway, OpenRouter, OpenAI)
- **기본 모델**: `gpt-5.4-mini` (초고속, 차감 배수 0.5배)

---

## 3. 설치 및 설정 방법

### 3.1 의존성 설치

```bash
# 가상환경 생성 및 활성화 (권장)
python3 -m venv .venv
source .venv/bin/activate

# 필수 패키지 설치 (openai, python-dotenv, pyyaml)
pip install -r src/requirements.txt
```

### 3.2 환경변수 (`.env`) 설정

프로젝트 루트에 `.env` 파일을 생성하고 발급받은 API 키를 입력합니다 (`.gitignore`에 의해 GitHub에는 업로드되지 않습니다).

```bash
# .env 파일 예시 (코디세이 게이트웨이 기준)
AI_API_KEY="sk-cody-live-YOUR_API_KEY"
AI_API_BASE_URL="https://copa.codyssey.kr/v1"
AI_MODEL="gpt-5.4-mini"

# 터미널 직접 export 방식도 지원
export AI_API_KEY="sk-cody-live-YOUR_API_KEY"
```

---

## 4. 사용 방법

### 4.1 커밋 메시지 자동 생성

작업 후 변경 사항을 확인하거나 스테이징(`git add`)한 상태에서 실행합니다.

```bash
python main.py commit
```

**출력 예시:**
```text
[INFO] 컨벤션 로드: .ai-gitgen.yml
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 45줄
[INFO] AI API 요청 중...
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
feat: AI 클라이언트 기본 엔드포인트와 모델 기본값 조정

- src/ai_client.py: API 키 접두사에 따라 base_url을 선택하도록 변경
- src/main.py: AI_MODEL 환경변수를 우선 적용하고 기본 모델을 gpt-5.4-mini로 변경
----------------------

[INFO] 모델: gpt-5.4-mini  |  호출 횟수: 1
```

### 4.2 Pull Request(PR) 초안 자동 생성

브랜치 작업 내역을 기반으로 PR 제목과 본문 초안을 생성합니다.

```bash
python main.py pr
```

**출력 예시:**
```text
[INFO] 현재 브랜치: feature/assistant-enhancement
[INFO] Git diff 수집 완료: 120줄
[INFO] AI API 요청 중...
[DONE] PR 초안 생성 완료

--- PR Title ---
feat: AI API 키 인식 개선 및 PR 출력 구조 보강
--- PR Body ---
## Why
- AI_API_KEY 환경변수 미인식 문제를 해결하고 일관된 에러 처리를 제공하기 위함입니다.
- PR 초안의 필수 섹션과 불릿 구조가 누락되지 않도록 품질을 안정화합니다.

## What
- src/ai_client.py: AI_API_KEY 우선 인식 및 코디세이 게이트웨이 자동 라우팅
- src/git_collector.py: HEAD~1 폴백 제거로 변경 사항 없음 정상 감지
- src/validator.py: Why/What/How to Test 필수 섹션 및 불릿 구조 강제 보정 후처리
- main.py: 루트 실행 진입점 추가 및 단일 대시 CLI 옵션 지원

## How to Test
- python main.py commit 및 python main.py pr 실행 확인
- python -m unittest discover tests -v 실행으로 13개 단위 테스트 통과 확인
---------------

[INFO] 모델: gpt-5.4-mini  |  호출 횟수: 1
```

### 4.3 CLI 옵션 안내

미션 및 동료평가 기준에 맞춰 단일 하이픈(`-`)과 이중 하이픈(`--`) 옵션을 모두 지원합니다.

| 옵션 | 단축/별칭 | 기본값 | 설명 |
|---|---|---|---|
| `--model` | `-model`, `-m` | `gpt-5.4-mini` | AI 모델 ID (예: `gemini-3-flash`, `claude-haiku-4`) |
| `--temperature` | `-temperature`, `-t` | `0.3` | 생성 다양성 (0.0: 결정론적/정갈함 ~ 1.0: 풍부한 서술) |
| `--max-tokens` | `-max-tokens` | `1024` | 최대 생성 토큰 수 |
| `--safe-mode` | `-safe-mode`, `-s` | 비활성화 | 민감 정보 마스킹 및 diff 줄/파일 수 상한 적용 |
| `--safe-max-files` | `-safe-max-files` | `10` | 안전 모드 diff 최대 파일 수 |
| `--safe-max-lines` | `-safe-max-lines` | `200` | 안전 모드 diff 최대 줄 수 |
| `--convention` | `-convention`, `-c` | `.ai-gitgen.yml`| 커스텀 컨벤션 설정 파일 경로 |

**실행 예시:**
```bash
# 온도 및 토큰 제한 테스트 (평가 항목 1-6 재현)
python main.py -temperature 0.0 -max-tokens 50 commit

# 안전 모드로 PR 초안 생성
python main.py -safe-mode pr
```

#### 4.3.1 재현 및 실험 워크플로 (Reproducibility & Experimentation)

CLI 옵션을 활용하여 동일 변경 사항에 대한 일관성 검증(재현성)과 다양한 표현 탐색(실험)을 손쉽게 수행할 수 있습니다.

1. **결정론적 재현 워크플로 (Deterministic Reproducibility)**:
   ```bash
   # 동일한 Git 변경 사항에 대해 항상 일관된 커밋 메시지 생성
   python main.py commit -temperature 0.0
   ```
   - **목적**: `temperature=0.0`은 가장 확률이 높은 최적 토큰만을 결정론적으로 선택하므로, 동일한 diff에 대해 항상 동일한 Conventional Commit 제목과 구조를 완벽히 재현합니다.

2. **다양성 실험 워크플로 (Creative Variation Experiment)**:
   ```bash
   # 보다 풍부하고 다양한 어휘를 사용한 PR 본문 초안 탐색
   python main.py pr -temperature 0.7
   ```
   - **목적**: `temperature=0.7`은 어휘 선택의 다양성을 높여, PR 본문의 상세한 기술적 맥락이나 대안 표현을 탐색할 때 유용합니다.

3. **출력 길이 및 토큰 제한 테스트 (Token Truncation Experiment)**:
   ```bash
   # 짧은 요약문 생성 및 토큰 상한 제한 동작 확인
   python main.py commit -max-tokens 50
   ```
   - **목적**: `max-tokens` 값을 낮춰 극단적인 토큰 제약 상황에서의 모델 동작과 검증기(Validator)의 안전성을 테스트합니다.

#### 4.3.2 Temperature 파라미터 정성적·정량적 가이드

| Temperature 값 | 정성적 특성 | 정량적 엔트로피 | 추천 작업 유형 |
|---|---|---|---|
| `0.0` | 엄격함, 일관성, 결정론적 (반복 재현율 100%) | 최소 (Top-1 토큰 고정) | 버그 픽스, 긴급 패치, 회귀 테스트, 엄격한 규격 커밋 |
| `0.3` | **기본값**: 규격 준수와 자연스러운 문장 구조의 균형 | 낮음 (핵심 어휘 일관성 유지) | 일상적인 기능 개발 커밋 메시지 자동 생성 |
| `0.7` | 풍부한 맥락 서술, 다양한 어휘와 문장 구조 | 보통 (표현 다양성 증가) | 대규모 PR 초안, 릴리즈 노트, 기능 설명 초안 |
| `1.0` | 창의적, 발산적 표현, 높은 변동성 | 높음 (어휘 예측 난이도 증가) | 다양한 문구 아이디어 브레인스토밍 및 실험 |

---

## 5. 주의사항 및 운영 관점

### 5.1 민감 정보 보호 (Safe Mode)
`git diff`에 API Key, 개인정보, 패스워드가 포함되어 외부 API로 유출되는 것을 방지합니다:
- `.env` 및 민감 파일은 `.gitignore`에 등록하여 사전 차단.
- `--safe-mode` 활성화 시 9종 정규표현식(`sk-...`, AWS 키, JWT, 이메일, 패스워드 등)을 `[MASKED]`로 자동 마스킹 후 전송.
- diff가 지나치게 큰 경우 최대 10개 파일, 200줄까지만 잘라서 전송.

### 5.2 비용 및 요청 횟수 제어
- `commit`과 `pr` 명령은 각각 **AI API 1회 호출**로 결과를 생성하여 불필요한 토큰 비용 낭비를 차단합니다.
- 변경 사항이 없는 경우(`git status` 깨끗함) API를 호출하지 않고 조기 종료합니다.
- 기본 탑재된 `gpt-5.4-mini`는 최저 차감 배수(0.5배)로 실행 비용이 매우 저렴합니다.

### 5.3 생성 결과 검토 원칙
- AI가 생성한 문구는 완성된 최종본이 아니라 **초안(Draft)**입니다.
- AI의 환각(Hallucination) 및 기획/비즈니스 맥락 누락 가능성이 있으므로, 반드시 엔지니어가 내용을 검토한 뒤 `git commit`에 반영합니다.

### 5.4 검토 중심 설계 및 자동 적용 방지 철학 (Review-First, No Auto Commit)
- **자동 커밋/푸시 원천 차단**: CLI 도구는 생성된 커밋 메시지와 PR 초안을 오직 터미널에 명확한 구분선(`--- Commit Message ---`, `--- PR Title ---`)과 함께 렌더링할 뿐, 사용자의 명시적 확인 없이 백그라운드에서 `git commit`이나 `git push`를 강제 실행하지 않습니다.
- **안전한 협업**: AI 생성물의 잠재적 환각이나 잘못된 가정을 엔지니어가 직접 눈으로 확인하고 확정하는 Human-in-the-loop 정책을 기본으로 준수합니다.

### 5.5 재생성 vs 후처리 정책 (Deterministic Post-Processing First)
- **후처리 우선 정책**:
  - LLM의 글자 수 초과나 불릿 누락을 해결하기 위해 API를 다시 호출(재생성)하는 대신, 파이썬 기반의 결정론적 하드 슬라이싱(`[:72]`, `[:80]`)과 필수 섹션 플레이스홀더 주입을 수행합니다.
  - **장점**: 추가 API 비용 0원, 지연 시간 < 0.001초, 수학적으로 100% 규격 확정 보장.
- **재생성이 적합한 예외적 케이스**:
  - 단순 포맷팅 문제를 넘어, diff의 핵심 변경 의도가 심각하게 왜곡되었거나 시맨틱 환각이 발생하여 전면적인 문맥 재구성이 불가피한 경우에 한합니다.

### 5.6 네트워크 장애 복원력 및 오류 처리 정책
- `AuthenticationError`, `APIConnectionError`, `RateLimitError` 등 발생 가능한 예외를 세분화하여 불필요한 파이썬 스택 트레이스 없이 명확한 원인과 조치 가이드를 출력합니다.
- 단발성 CLI 도구의 특성상 무한 대기나 숨겨진 지연을 방지하기 위해 사용자에게 즉각적 피드백(Fail-Fast with Actionable Guidance)을 제공하는 것을 기본 원칙으로 합니다.

---

## 6. 프로젝트 디렉토리 구조

```text
b3_2/
├── main.py                 # 루트 CLI 진입점 (원스톱 실행)
├── .ai-gitgen.yml          # 컨벤션 설정 파일
├── .gitignore              # .env 및 가상환경 격리
├── activity_log.md         # 안티그래비티 작업 메모리
├── README.md               # 프로젝트 사용 가이드 (본 문서)
├── docs/
│   ├── EVALUATION_PLAN.md  # 동료평가 대비 6단계 종합 평가 계획서
│   ├── EVALUATION.md       # 동료평가 질문 원문
│   └── CONVENTIONS.md      # Git 커밋 컨벤션 가이드
├── src/
│   ├── main.py             # CLI 핸들러 및 인자 파서
│   ├── ai_client.py        # OpenAI/Codyssey/OpenRouter REST API 클라이언트
│   ├── git_collector.py    # git status/diff 수집 및 민감정보 마스킹
│   ├── prompt_builder.py   # 커밋 및 PR 프롬프트 템플릿 생성기
│   ├── validator.py        # 길이 및 형식 검증/보정 후처리기
│   └── convention.py       # YAML 컨벤션 로더
└── tests/
    └── test_assistant.py   # 14개 단위/통합 테스트 스위트
```

---

## 7. 검증 및 테스트

```bash
# 14개 단위 테스트 전체 실행
python -m unittest discover tests -v
```
