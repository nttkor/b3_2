# B3-2 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기
## 동료평가 대비 종합 평가 계획서 (Evaluation Plan)

> **문서 버전:** 1.0.0  
> **기준 일자:** 2026-10-03 (KST)  
> **미션 과제:** B3-2 — AI 도구 학습 (클라우드와 AI API)  
> **평가 프레임워크:** `평가문항` → `요구사항` → `구현` → `검증` → `증빙` → `평가 설명`  
> **보너스 과제 처리:** 사용자 요청에 따라 **보너스 과제(항목 5)는 대상에서 제외**하고 필수 항목(항목 1~4) 100% PASS를 목표로 함.

---

## 1. 사전 분석 요약: 복사된 코드(`ref_site`, `src`) 진단 결과

### 1.1 `ref_site/` 코드 분석
- **현 상태:** 이전 미션인 **Mini Git**(커밋 그래프 DAG, 위상 정렬, BFS 최단 경로, 역색인, 정렬 알고리즘 직접 구현) 코드와 문서가 위치해 있음.
- **활용성 판단:** 
  - 본 미션(B3-2: AI 기반 Git 커밋/PR 자동 생성기)의 실행 코드가 아님.
  - 다만, 실제 Git 변경 사항(diff)을 생성하고 테스트해볼 수 있는 **샘플 프로젝트 저장소(Test Target)**로는 유용하게 활용 가능함.
- **결론:** 미션 핵심 소스로 사용할 수 없으며, 참고용 또는 테스트 데이터로만 활용.

### 1.2 `src/` 코드 분석 및 보강 필요성 (Gap Analysis)
- **현 상태:** AI 기반 커밋/PR 생성기의 기본 구조(`main.py`, `ai_client.py`, `git_collector.py`, `prompt_builder.py`, `validator.py`, `convention.py`)가 잘 분리되어 작성되어 있음.
- **치명적 결함 및 보강 필요 항목 (Urgent Fixes):**
  1. **환경변수 인식 결함 (Critical):**
     - 미션 규격은 `AI_API_KEY`를 명시하고 있으며 미설정 시 `[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.` 출력을 요구함.
     - 현재 `ai_client.py`는 `OPENROUTER_API_KEY`만 조회하므로, 평가자가 `export AI_API_KEY="xxx"`를 주입하면 키를 인식하지 못하고 실패함.
     - **보강안:** `AI_API_KEY`를 최우선 조회하고, 없을 경우 `OPENROUTER_API_KEY`, `OPENAI_API_KEY` 순으로 폴백 지원. 미설정 에러 메시지를 규격에 맞춤.
  2. **`python main.py pr`의 "변경 사항 없음" 감지 실패 (Critical):**
     - `git_collector.py`의 `get_diff()`에 `diff = self._run(['git', 'diff', 'HEAD~1']).strip()` 폴백 로직이 포함되어 있음.
     - 이로 인해 변경 사항이 없는 깨끗한 main 브랜치에서 `python main.py pr`을 실행해도 이전 커밋(`HEAD~1`)의 diff를 읽어와 AI 호출로 넘어가버림. (평가 항목 1-4 탈락 위험)
     - **보강안:** `HEAD~1` 폴백 제거. 변경 사항이 없으면 즉시 `[INFO] 변경 사항이 없습니다. PR 초안을 생성하지 않고 종료합니다.` 출력 후 정상 종료하도록 수정.
  3. **단일 하이픈 CLI 옵션 지원 누락 (Important):**
     - 미션 PDF 및 평가 문항에서 `-model`, `-temperature`, `-max-tokens` 형태의 옵션 입력이 명시됨.
     - 현재 `main.py`는 `--temperature`, `-t`만 정의되어 있어, 평가자가 `-temperature 0.7`을 입력하면 `argparse` 파싱 에러 발생.
     - **보강안:** `argparse` 옵션에 `--temperature`와 `-temperature`, `--max-tokens`와 `-max-tokens`, `--model`과 `-model`, `--safe-mode`와 `-safe-mode`를 모두 등록.
  4. **기본 모델 ID 오류:**
     - `main.py`에 `DEFAULT_MODEL = 'anthropic/claude-opus-4'`로 지정되어 있으나 이는 OpenRouter에 존재하지 않는 ID임 (`README.md`에는 `anthropic/claude-3.5-haiku`로 기술).
     - **보강안:** `DEFAULT_MODEL = 'anthropic/claude-3.5-haiku'`로 통일.
  5. **프로젝트 루트 실행 및 `.env` 로딩:**
     - 프로젝트 루트에서 `python main.py commit`으로 실행 가능하도록 루트 엔트리포인트 구성 또는 경로 설정 보강.
  6. **Validator의 불릿 및 섹션 보장 후처리:**
     - LLM 응답이 불안정하여 섹션 누락이나 불릿 누락이 발생하더라도 후처리(Post-processing) 단계에서 누락을 교정하고 불릿 포맷을 강제 보장하도록 보강.

---

## 2. 항목별 세부 평가 계획 (6단계 프레임워크)

```text
Evaluation Question(평가문항)
→ Requirement(요구사항)
→ Implementation(구현)
→ Verification(검증)
→ Evidence(증빙)
→ Evaluation Explanation(평가 설명)
```

---

### [항목 1 — 실제 동작 확인] (판정: PASS / FAIL)

#### 1-1. 프로젝트 루트에서 커밋 메시지 생성 명령 실행 시 커밋 메시지가 터미널에 출력되는가?
- **Requirement:** 
  - Git 루트에서 `python main.py commit` 실행 시 `git status`와 `git diff`를 수집하여 AI 호출 후 커밋 메시지 출력.
- **Implementation:** 
  - `main.py` -> `cmd_commit()` -> `GitCollector`로 diff 수집 -> `PromptBuilder` -> `AIClient.generate()` -> `validator.validate_commit()`.
- **Verification:**
  ```bash
  # 1. 테스트 변경 사항 생성 및 스테이징
  echo "// test comment" >> test_sample.txt
  git add test_sample.txt

  # 2. 커밋 메시지 생성 실행
  python main.py commit
  ```
- **Evidence:**
  ```text
  [INFO] Git status 수집 완료: 1개 파일 변경 감지
  [INFO] Git diff 수집 완료: 4줄
  [INFO] AI API 요청 중...
  [DONE] 커밋 메시지 생성 완료

  --- Commit Message ---
  feat: test_sample 파일 내 설명 주석 추가

  - test_sample.txt 파일 변경
  - 코드 이해를 돕기 위한 테스트 주석 추가
  ----------------------

  [INFO] 모델: anthropic/claude-3.5-haiku  |  호출 횟수: 1
  ```
- **Evaluation Explanation:**
  - Git 상태를 실시간 수집하여 명령 1회로 터미널에 명확한 구분선과 함께 커밋 메시지 초안을 출력합니다.

---

#### 1-2. PR 생성 명령 실행 시 PR 제목과 본문 초안이 터미널에 출력되는가?
- **Requirement:** 
  - `python main.py pr` 실행 시 브랜치명 및 diff를 수집하여 PR 제목(1줄)과 본문(Why/What/How to Test) 출력.
- **Implementation:** 
  - `main.py` -> `cmd_pr()` -> `GitCollector.get_diff(for_pr=True)` -> `build_pr_prompt()` -> `validate_pr()`.
- **Verification:**
  ```bash
  python main.py pr
  ```
- **Evidence:**
  ```text
  [INFO] 현재 브랜치: feature/test-branch
  [INFO] Git diff 수집 완료: 12줄
  [INFO] AI API 요청 중...
  [DONE] PR 초안 생성 완료

  --- PR Title ---
  feat: 테스트 주석 및 기능 개선 반영
  --- PR Body ---
  ## Why
  - 코드 가독성 향상 및 동료 검토 편의성을 위해 주석을 추가했습니다.

  ## What
  - test_sample.txt에 테스트 주석 반영
  - 변경 사항 요약 자동화 검증

  ## How to Test
  - python main.py pr 실행 후 제목 및 본문 양식 확인
  ---------------

  [INFO] 모델: anthropic/claude-3.5-haiku  |  호출 횟수: 1
  ```
- **Evaluation Explanation:**
  - 현재 브랜치 맥락과 diff를 종합하여 PR 제목 1줄과 지정된 3대 필수 섹션(Why/What/How to Test)의 초안을 구획화하여 출력합니다.

---

#### 1-3. AI API Key가 설정되지 않은 상태에서 실행하면 오류 메시지가 출력되고 종료되는가?
- **Requirement:** 
  - `AI_API_KEY` 환경변수 미설정 시 명확한 에러 안내 메시지를 출력하고 프로세스가 비정상 비정상 크래시(Traceback) 없이 `exit code 1`로 종료되어야 함.
- **Implementation:** 
  - `ai_client.py`의 `AIClient.__init__()`에서 환경변수 검사 후 즉시 에러 출력 및 `sys.exit(1)`.
- **Verification:**
  ```bash
  # API Key 환경변수를 제거한 격리 환경에서 실행
  env -u AI_API_KEY -u OPENROUTER_API_KEY -u OPENAI_API_KEY python main.py commit
  echo "Exit Code: $?"
  ```
- **Evidence:**
  ```text
  [ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
  ## 예) export AI_API_KEY="YOUR_KEY"
  Exit Code: 1
  ```
- **Evaluation Explanation:**
  - 하드코딩을 방지하고 환경변수를 강제하며, 미설정 시 사용자에게 즉각 조치 가능한 가이드라인(`export AI_API_KEY=...`)을 제공하고 정상 에러 종료합니다.

---

#### 1-4. Git 변경 사항이 없는 상태에서 실행하면 `변경 사항이 없습니다`에 준하는 메시지가 출력되는가?
- **Requirement:** 
  - 워킹 트리와 스테이징 영역이 깨끗한 상태에서 `commit` 또는 `pr` 실행 시, 불필요한 AI API 호출 없이 종료 메시지를 출력하고 `exit code 0`으로 종료.
- **Implementation:** 
  - `GitCollector.count_changed_files()` 검사 및 `diff` 존재 여부 확인 후 조기 종료.
- **Verification:**
  ```bash
  # 깨끗한 Git 워킹 트리 상태에서 실행
  git status
  python main.py commit
  python main.py pr
  ```
- **Evidence:**
  ```text
  # commit 실행 시:
  [INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.

  # pr 실행 시:
  [INFO] 변경 사항이 없습니다. PR 초안을 생성하지 않고 종료합니다.
  ```
- **Evaluation Explanation:**
  - 변경 사항이 없는 상황에서 외부 AI API를 호출하여 비용이 낭비되는 것을 원천 차단하고 즉시 사용자에게 상황을 알립니다.

---

#### 1-5. 출력된 PR 본문에 `Why / What / How to Test` 구조가 포함되고, 각 섹션에 최소 1개 불릿이 포함되는가?
- **Requirement:** 
  - PR 본문은 반드시 `## Why`, `## What`, `## How to Test` 헤더를 포함하고 각 섹션 하위에 `-` 불릿 포인트가 1개 이상 존재해야 함.
- **Implementation:** 
  - `prompt_builder.py`에서 템플릿 명시 + `validator.py`의 `validate_pr()`에서 정규표현식 검증 및 누락 시 자동 보정(후처리).
- **Verification:**
  ```bash
  python main.py pr
  ```
- **Evidence:**
  ```markdown
  ## Why
  - 기능 구현 배경 및 목적 기술

  ## What
  - 수정한 핵심 파일 및 로직 요약

  ## How to Test
  - 로컬 테스트 실행 방법 및 확인 절차
  ```
- **Evaluation Explanation:**
  - 프롬프트 레벨에서의 지시뿐만 아니라 후처리 검증기를 통해 세 섹션의 존재와 불릿 포맷을 이중으로 보장합니다.

---

#### 1-6. `-temperature` 또는 `-max-tokens` 값을 변경해 실행했을 때 출력 길이/디테일 차이가 재현되는가?
- **Requirement:** 
  - CLI 파라미터를 통해 temperature(0.0 vs 0.9) 및 max_tokens(100 vs 1000)를 전달하고 결과 차이를 시연할 수 있어야 함.
- **Implementation:** 
  - CLI 인자 파싱 -> `AIClient` 초기화 파라미터 전달 -> OpenAI 호환 API 요청 페이로드에 반영.
- **Verification:**
  ```bash
  # 1. max-tokens 제한 테스트 (극단적으로 짧은 출력 / 조기 종료 관찰)
  python main.py -max-tokens 50 commit

  # 2. temperature 비교 테스트 (0.0: 결정론적/정갈함 vs 0.9: 풍부하고 서술적인 표현)
  python main.py -temperature 0.0 commit
  python main.py -temperature 0.9 commit
  ```
- **Evidence:**
  - `-max-tokens 50`: 짧은 한 줄 요약만 출력되고 토큰 제한에 의해 본문 생략 또는 단축.
  - `-temperature 0.0`: 군더더기 없는 전형적인 conventional commit prefix와 직관적 단어 사용.
  - `-temperature 0.9`: 다양한 어휘와 상세한 서술형 불릿 포인트 생성.
- **Evaluation Explanation:**
  - AI 생성의 무작위성(temperature)과 생성 길이(max_tokens)를 CLI 옵션으로 직접 제어하여 모델의 행동 변화를 즉각 검증할 수 있습니다.

---

#### 1-7. 커밋/PR 출력이 정의된 길이/형식 규칙(제목 길이, 섹션 구조, 불릿 조건)을 만족하는가?
- **Requirement:** 
  - 커밋 제목: 50자 이내 권장 (최대 72자 하드 리밋).
  - PR 제목: 최대 80자 하드 리밋.
  - 커밋 본문: 1~3개 파일 언급 및 1~2개 불릿.
  - PR 본문: 3대 섹션 + 불릿 1개 이상.
- **Implementation:** 
  - `validator.py`의 `validate_commit()`, `validate_pr()` 함수에서 하드 리밋 초과 시 슬라이싱 및 경고, 형식 강제.
- **Verification:**
  - 단위 테스트(`tests/test_validator.py`) 및 실제 CLI 실행 결과를 통해 글자 수 및 라인 수 검증.
- **Evidence:**
  ```text
  [WARN] 커밋 제목 75자 → 72자로 자릅니다.
  ```
- **Evaluation Explanation:**
  - 모델의 생성 길이가 통제 범위를 벗어날 경우를 대비해 실무 Git 컨벤션(50/72 규칙, 80자 제한)을 만족하도록 후처리 계층에서 엄격하게 통제합니다.

---

### [항목 2 — 코드 구조와 설계 이유 설명] (판정: PASS / FAIL)

#### 2-1. Git 변경 사항 수집 로직과 AI API 호출 로직을 왜 분리했는지 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **단일 책임 원칙 (SRP) 및 관심사 분리 (Separation of Concerns):**
    - `GitCollector`: 로컬 시스템의 Git 환경 의존성(프로세스 실행, status/diff 파싱, 민감정보 마스킹)만 담당.
    - `AIClient`: 외부 네트워크 HTTP 통신, 인증 헤더, JSON 페이로드 구성, 통신 예외 처리만 담당.
  - **테스트 용이성 (Testability):**
    - Git 환경 없이 가짜(Mock) diff 문자열을 사용해 `AIClient`를 단독 테스트할 수 있고, 반대로 외부 인터넷이나 API Key 없이도 `GitCollector`의 diff 수집 및 마스킹 기능을 100% 독립 단위 테스트할 수 있습니다.
  - **유지보수성 및 확장성:**
    - AI 공급자(OpenRouter -> OpenAI -> 로컬 Ollama)를 변경하더라도 Git 수집 코드는 전혀 수정할 필요가 없습니다.

#### 2-2. 프롬프트 구성 로직과 출력 포맷팅(길이 규칙 포함) 로직을 어떻게 분리했고, 그 이유를 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **역할 분리:**
    - `PromptBuilder` (사전 유도): 변경 사항 맥락(status, diff)과 컨벤션 규칙을 LLM이 이해하기 쉬운 자연어 및 Few-shot 템플릿 형태로 가공.
    - `Validator` (사후 검증 및 후처리): LLM의 비결정론적(Probabilistic) 응답을 소프트웨어 규격에 맞게 결정론적(Deterministic)으로 검증 및 잘라내기(Truncation).
  - **분리 이유:**
    - LLM은 "50자 이내로 써줘"라는 프롬프트를 받더라도 토큰 단위 생성 특성상 글자 수 제한을 완벽히 지키지 못하는 확률적 한계가 있습니다.
    - 따라서 프롬프트로 1차 유도를 하고, 코드 레벨의 Validator에서 2차로 하드 룰(72자 초과 시 자르기, 누락 섹션 주입)을 집행하는 2단계 방어 체계를 구축했습니다.

#### 2-3. API 파라미터를 CLI 옵션으로 설계한 이유(재현성/실험 용이성)를 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **실험 용이성 (Experimentation):** 소스코드를 매번 열어서 수정하지 않고도 터미널 명령어 레벨에서 `temperature`나 `max_tokens`를 조절해가며 변경 사항에 가장 적합한 설정을 탐색할 수 있습니다.
  - **재현성 (Reproducibility):** CI/CD 파이프라인이나 스크립트 자동화 시 `python main.py -temperature 0.0`과 같이 파라미터를 명시적으로 고정하여 매번 일관되고 재현 가능한 출력을 보장합니다.
  - **비용 최적화:** 간단한 수정일 때는 `-max-tokens 256`으로 절약하고, 대규모 리팩토링일 때는 `-max-tokens 2048`로 유연하게 설정할 수 있습니다.

#### 2-4. 오류 처리(API Key 누락, 네트워크 오류 등)를 어떤 방식으로 구현했고, 왜 그렇게 했는지 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **구현 방식:**
    - API Key 누락: 네트워크 요청을 보내기 전 초기화 시점에 조기 검증(Fail-Fast)하여 명확한 가이드 제공.
    - 통신 오류: `AuthenticationError`(401), `RateLimitError`(429), `APIConnectionError`(네트워크 단절), `APIStatusError`(5xx 서버 오류) 등 세분화된 예외 클래스를 개별 포획(`except`).
    - 깔끔한 CLI 출력: 사용자에게 불필요한 Python 내부 Traceback 스택을 감추고, `[ERROR]` 접두사가 붙은 조치 가능한 안내 메시지를 출력한 뒤 `sys.exit(1)` 처리.
  - **이유:** 실무 CLI 도구로서 사용자 경험(UX)을 극대화하고, 문제 발생 시 사용자가 즉시 원인(인증 실패인지, 인터넷 단절인지)을 파악하여 조치할 수 있도록 하기 위함입니다.

---

### [항목 3 — AI API 파라미터·프롬프트 이해] (판정: PASS / FAIL)

#### 3-1. AI API 요청 시 `temperature` 값을 높이거나 낮추면 결과가 어떻게 달라지는지 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **원리:** Next Token 예측 시 로짓(Logit) 값을 확률 분포로 변환하는 소프트맥스(Softmax) 함수의 분모에 적용되는 값입니다.
  - **낮출 때 (0.0 ~ 0.2):** 확률이 가장 높은 토큰만 선택(Greedy decoding에 수렴)하여 **일관되고, 정형화되며, 보수적인** 결과가 나옵니다. Git 커밋처럼 규격 준수가 중요한 작업에 적합합니다.
  - **높일 때 (0.7 ~ 1.0):** 낮은 확률의 토큰도 샘플링 대상이 되어 **창의적이고, 어휘가 다양하며, 문장이 풍부**해집니다. 단, 환각(Hallucination)이나 형식 이탈 가능성이 높아집니다.

#### 3-2. `max_tokens` 값이 결과물에 어떤 영향을 미치며, 어떤 기준으로 값을 설정했는지 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **영향:** 모델이 생성할 수 있는 최대 완성 토큰 수를 제한합니다. 값이 너무 작으면 문장이나 필수 섹션 중간에 생성이 끊기는 `finish_reason="length"` 현상이 발생합니다.
  - **설정 기준:**
    - **커밋 메시지 기본값 (512~1024):** 제목 1줄(~20토큰) + 본문 불릿 2줄(~100토큰)이면 충분하므로 1024는 어떤 상황에서도 끊김 없이 완전한 문장을 보장하면서 폭주를 막는 안전한 상한선입니다.
    - **PR 초안 기본값 (1024):** Why/What/How to Test의 3개 섹션과 각 불릿을 충분히 서술할 수 있는 실무 최적 크기입니다.

#### 3-3. 커밋/PR 용도에 맞는 결과를 얻기 위해 프롬프트에 어떤 정보를 포함했고, 왜 그렇게 구성했는지 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **포함 정보:**
    1. **시스템 역할 및 지침:** "Git 변경 사항을 분석하여 커밋/PR 메시지를 생성하는 도우미"
    2. **컨벤션 규칙:** Conventional commit 타입(`feat`, `fix` 등), 글자 수 제한, 불릿 개수
    3. **출력 스키마:** 불필요한 인사말("Here is your commit:")을 금지하고 지정된 헤더(`--- Commit Message ---` 또는 `TITLE:`)만 출력하도록 강제
    4. **입력 데이터 맥락:** 전체적인 변경 파일 파악을 위한 `git status` + 실제 변경 로직 확인을 위한 `git diff` + 작업 의도 파악을 위한 `현재 브랜치명`
  - **구성 이유:** 모델이 변경된 코드(diff)만 보면 작업의 거시적 맥락(새 파일 추가인지, 어떤 브랜치 작업인지)을 놓치기 쉬우므로, 메타데이터(status, branch)를 함께 제공하여 요약 품질을 극대화했습니다.

#### 3-4. 길이/형식 규칙을 `재생성`으로 해결할지 `후처리`로 해결할지 선택했다면, 그 선택 이유를 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **선택: 후처리(Post-processing) 방식 채택.**
  - **선택 이유:**
    1. **비용 및 지연시간(Latency) 최소화:** 미션 제약 사항에 "1회 실행 시 AI API 호출은 1회로 제한"이 강력히 권장되어 있습니다. 재생성(Retry)을 하면 네트워크 왕복 시간(2~4초)이 추가되고 토큰 비용이 2배로 증가합니다.
    2. **결정론적 신뢰성:** LLM에게 다시 생성을 요청하더라도 확률 모델 특성상 또다시 72자를 초과할 위험이 있습니다. 파이썬 코드 기반 후처리 슬라이싱은 100% 확실하게 글자 수와 포맷을 보장합니다.
    3. **실행 속도:** 파이썬 문자열 슬라이싱 및 정규식 후처리는 0.1ms 이내에 즉각 완료됩니다.

---

### [항목 4 — 안전성·실무 적용 판단] (판정: PASS / FAIL)

#### 4-1. AI가 생성한 커밋/PR 텍스트를 바로 사용하지 않고 검토가 필요한 이유를 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **환각(Hallucination) 위험:** 실제 수정하지 않은 내용이나 잘못 추론된 부수 효과를 AI가 작성할 수 있습니다.
  - **비즈니스 도메인 맥락 부재:** AI는 코드 차이점(diff)만 볼 뿐, 지라 티켓 내용, 기획 의도, 장애 대응 배경 등 코드 외적인 비즈니스 맥락을 알지 못합니다.
  - **코드 오너십 및 감사(Audit) 책임:** 커밋 로그와 PR은 형상 관리 및 감사 기록의 영구 자산이므로, 이를 병합하고 배포하는 최종 책임은 작성자(인간 엔지니어)에게 있습니다.

#### 4-2. `git diff`에 민감정보(API Key, 개인정보 등)가 포함될 수 있는 상황과 이를 방지하기 위한 방안을 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **발생 상황:**
    - 개발자가 테스트 도중 API 키, DB 패스워드, JWT 토큰, 개인정보를 코드에 하드코딩하고 실수로 git stage에 올렸을 때
    - `.gitignore` 누락으로 `.env` 파일 내용이 diff에 노출되었을 때
  - **방지 방안 (3중 방어막):**
    1. **사전 방지:** `.gitignore`에 `.env` 등록 및 git pre-commit hook(TruffleHog, Gitleaks 등)을 통한 커밋 차단.
    2. **도구 내 안전 모드 (`--safe-mode`):** 정규표현식 기반으로 9종 민감 패턴(API Key, JWT, AWS Key, 이메일, 패스워드)을 `[MASKED]`로 자동 치환 후 LLM 전송.
    3. **전송 크기 상한 제한:** 대용량 diff 유출을 방지하기 위해 파일 수(최대 10개) 및 줄 수(최대 200줄)를 제한하여 전송.

#### 4-3. 이 도구를 실제 팀 프로젝트에 적용한다면 어떤 기능을 가장 먼저 추가하거나 개선하고 싶은지, 그 우선순위 근거를 설명할 수 있는가?
- **답변 핵심 (Explanation):**
  - **1순위 (최우선): Git Hook (`prepare-commit-msg`) 자동 연동**
    - **근거:** 엔지니어가 별도로 터미널에서 CLI를 실행하고 복사-붙여넣기하는 방식은 사용성이 떨어져 실무 도입이 어렵습니다. `git commit` 실행 시 훅이 자동으로 초안을 작성하여 에디터에 띄워주면 개발 워크플로우에 완벽히 통합됩니다.
  - **2순위: 이슈 트래커(Jira / GitHub Issues) 연동**
    - **근거:** 실무 커밋/PR은 반드시 티켓 번호(예: `[PROJ-1024]`)와 요구사항을 참조해야 합니다. 브랜치명이나 티켓 API에서 요구사항을 긁어와 Why 섹션에 자동 반영하면 설명 품질이 비약적으로 향상됩니다.
  - **3순위: 사내 로컬 LLM (Ollama / vLLM) 지원**
    - **근거:** 금융, 공공, 대기업 등 보안이 중요한 기업 환경에서는 소스코드가 외부 클라우드(OpenAI, Anthropic)로 나가는 것이 원천 금지되어 있으므로, 사내 폐쇄망 로컬 LLM 지원이 필수적입니다.

---

### [항목 5 — 보너스] (사용자 요청: 미선택 / 제외)
- 사용자 지침("미션중 보너스는 필요없다")에 따라 평가 대상에서 제외하며, 동료평가 시 보너스 항목은 미부여/스킵을 원칙으로 함.

---

## 3. 평가 준비를 위한 원스톱 사전 리허설 시나리오

동료평가 세션 직전 아래 순서대로 터미널 명령을 실행하여 모든 항목의 정상 동작을 1분 내에 입증합니다.

```bash
# [준비 1] 가상환경 활성화 및 패키지 확인
source .venv/bin/activate
pip list | grep -E "openai|python-dotenv|pyyaml"

# [준비 2] API 키 설정
export AI_API_KEY="sk-or-v1-YOUR_KEY"

# [검증 1] API 키 미설정 에러 테스트 (항목 1-3)
env -u AI_API_KEY -u OPENROUTER_API_KEY python main.py commit

# [검증 2] 변경 사항 없는 상태 테스트 (항목 1-4)
python main.py commit
python main.py pr

# [검증 3] 변경 사항 생성 후 커밋 메시지 생성 테스트 (항목 1-1, 1-7)
echo "# test" >> README.md
python main.py commit

# [검증 4] PR 초안 생성 테스트 (항목 1-2, 1-5, 1-7)
python main.py pr

# [검증 5] CLI 파라미터 제어 테스트 (항목 1-6)
python main.py -temperature 0.0 -max-tokens 50 commit
python main.py -temperature 0.9 -max-tokens 1024 commit

# [정리] 테스트 변경 사항 되돌리기
git checkout -- README.md
```
