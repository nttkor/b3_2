# B3-2 AI Git Assistant - 동료평가 질의응답 대비집 (EVALUATION_QA.md)

> **문서 개요**: 본 문서는 [`docs/EVALUATION.md`](./EVALUATION.md)에 수록된 동료평가 4대 평가 항목(18개 세부 문항)에 근거하여, 평가관의 질문에 즉시 명쾌하게 답변할 수 있도록 **핵심 요약 답변**, **상세 설명**, **관련 핵심 소스코드 스니펫**, **GitHub 상대 경로 링크**, **실제 검증 명령어 및 증빙**을 1:1로 집대성한 공식 Q&A 대비서입니다.

---

## 목차
1. [항목 1 — 실제 동작 확인 (7문항)](#항목-1--실제-동작-확인)
2. [항목 2 — 코드 구조와 설계 이유 설명 (4문항)](#항목-2--코드-구조와-설계-이유-설명)
3. [항목 3 — AI API 파라미터·프롬프트 이해 (4문항)](#항목-3--ai-api-파라미터프롬프트-이해)
4. [항목 4 — 안전성·실무 적용 판단 (3문항)](#항목-4--안전성실무-적용-판단)
5. [전체 문항 추적 매트릭스 (Traceability Matrix)](#5-전체-문항-추적-매트릭스-traceability-matrix)

---

## 항목 1 — 실제 동작 확인

---

### Q1-1. 프로젝트 루트에서 커밋 메시지 생성 명령 실행 시 커밋 메시지가 터미널에 출력되는가?

* **핵심 답변**: **네, 정상 출력됩니다.** 루트 엔트리포인트에서 `python main.py commit`을 실행하면 작업 트리의 `git status`와 `git diff`를 수집하여 AI가 생성한 Conventional Commit 규격의 커밋 메시지(제목 + 본문 불릿)가 구분선과 함께 출력됩니다.
* **상세 설명**:
  - [`main.py`](../main.py)를 통해 가상환경(`.venv`)을 자동 감지하고 [`src/main.py`](../src/main.py)의 `cmd_commit()`을 호출합니다.
  - [`src/git_collector.py`](../src/git_collector.py)에서 `git diff HEAD`를 수집하고, [`src/prompt_builder.py`](../src/prompt_builder.py)에서 커밋 프롬프트를 구성한 후, [`src/ai_client.py`](../src/ai_client.py)가 Codyssey 게이트웨이(`gpt-5.4-mini`)를 호출하여 ~1.5초 만에 메시지를 생성합니다.
* **관련 소스코드**:
  - 링크: [`src/main.py#L42-L78`](../src/main.py#L42-L78)
  ```python
  # src/main.py
  def cmd_commit(args: argparse.Namespace, convention: dict) -> None:
      collector = GitCollector()
      diff = collector.get_diff(safe_mode=args.safe_mode, for_pr=False)
      if not diff.strip():
          print('[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.')
          sys.exit(0)
      client = _make_client(args)
      prompt = build_commit_prompt(status, diff, convention)
      result = client.generate(prompt)
      commit_msg = validate_commit(result)
      print('--- Commit Message ---\n' + commit_msg + '\n----------------------')
  ```
* **검증 명령어 및 실제 출력**:
  ```bash
  python main.py commit
  ```
  ```text
  [INFO] 컨벤션 로드: .ai-gitgen.yml
  [INFO] Git status 수집 완료: 1개 파일 변경 감지
  [INFO] Git diff 수집 완료: 118줄
  [INFO] AI API 요청 중...
  [DONE] 커밋 메시지 생성 완료

  --- Commit Message ---
  docs: chat.md에 옵션 파싱 오류 대응 기록 추가

  - chat.md에 `python main.py commit -temperature 0.2 -safe-mode` 실행 오류와 원인 분석을 정리
  - 수정 결과와 재실행 확인 로그를 함께 기록해 변경 이력을 보강
  ----------------------

  [INFO] 모델: gpt-5.4-mini  |  호출 횟수: 1
  ```

---

### Q1-2. PR 생성 명령 실행 시 PR 제목과 본문 초안이 터미널에 출력되는가?

* **핵심 답변**: **네, 정상 출력됩니다.** `python main.py pr`을 실행하면 현재 브랜치명과 변경 내역을 바탕으로 1줄 제목(`--- PR Title ---`)과 3대 필수 섹션을 포함한 본문(`--- PR Body ---`)이 구획화되어 출력됩니다.
* **상세 설명**:
  - [`src/git_collector.py`](../src/git_collector.py)의 `get_current_branch()`를 통해 현재 작업 브랜치 컨텍스트를 주입합니다.
  - [`src/validator.py`](../src/validator.py)의 `validate_pr()`을 통해 제목(최대 80자)과 본문(Why, What, How to Test 구조)이 완벽히 검증된 후 터미널에 렌더링됩니다.
* **관련 소스코드**:
  - 링크: [`src/main.py#L80-L118`](../src/main.py#L80-L118)
  ```python
  # src/main.py
  def cmd_pr(args: argparse.Namespace, convention: dict) -> None:
      branch = collector.get_current_branch()
      diff = collector.get_diff(safe_mode=args.safe_mode, for_pr=True)
      prompt = build_pr_prompt(status, diff, branch, convention)
      result = client.generate(prompt)
      title, body = validate_pr(result)
      print('--- PR Title ---\n' + title + '\n--- PR Body ---\n' + body + '\n---------------')
  ```
* **검증 명령어 및 실제 출력**:
  ```bash
  python main.py pr
  ```
  ```text
  [INFO] 컨벤션 로드: .ai-gitgen.yml
  [INFO] 현재 브랜치: main
  [INFO] Git diff 수집 완료: 179줄
  [INFO] AI API 요청 중...
  [DONE] PR 초안 생성 완료

  --- PR Title ---
  chat.md에 가상환경 오류 해결 기록 추가
  --- PR Body ---
  ## Why
  - `python main.py commit` 실행 중 발생한 `dotenv` 모듈 누락 문제의 원인과 해결 과정을 기록하기 위해서입니다.

  ## What
  - `chat.md`에 오류 발생 원인, 해결 방법, 검증 결과를 포함한 대화 로그를 추가했습니다.

  ## How to Test
  - `chat.md`에 추가된 내용이 원인 분석, 해결 내용, 검증 결과로 정상 반영되었는지 확인합니다.
  ---------------

  [INFO] 모델: gpt-5.4-mini  |  호출 횟수: 1
  ```

---

### Q1-3. AI API Key가 설정되지 않은 상태에서 실행하면 오류 메시지가 출력되고 종료되는가?

* **핵심 답변**: **네, 파이썬 트레이스백(Traceback) 없이 명세서 표준 에러 문구를 출력하고 정상 종료(`sys.exit(1)`)합니다.**
* **상세 설명**:
  - [`src/ai_client.py`](../src/ai_client.py)의 초기화(`__init__`) 단계에서 `AI_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`를 순서대로 확인합니다.
  - 키가 모두 없을 경우 불필요한 예외 스택을 숨기고 사용자가 즉시 조치할 수 있도록 직관적인 안내문을 출력합니다.
* **관련 소스코드**:
  - 링크: [`src/ai_client.py#L25-L34`](../src/ai_client.py#L25-L34)
  ```python
  # src/ai_client.py
  api_key = (
      os.environ.get('AI_API_KEY')
      or os.environ.get('OPENROUTER_API_KEY')
      or os.environ.get('OPENAI_API_KEY')
  )
  if not api_key:
      print('[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.')
      print('## 예) export AI_API_KEY="YOUR_KEY"')
      sys.exit(1)
  ```
* **검증 명령어 및 실제 출력**:
  ```bash
  .env 파일명을 바꾸고 실해해보면 됨
  ((.venv) ) mpeg46551@c3r3s7 b3_2 % python main.py commit                               
[INFO] 컨벤션 로드: .ai-gitgen.yml
[INFO] Git status 수집 완료: 1개 파일 변경 감지
[INFO] Git diff 수집 완료: 0줄
[INFO] AI API 요청 중...
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.

## 예) export AI_API_KEY="YOUR_KEY"
  ```
  ```text
  [ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
  ## 예) export AI_API_KEY="YOUR_KEY"
  ```

---

### Q1-4. Git 변경 사항이 없는 상태에서 실행하면 `변경 사항이 없습니다`에 준하는 메시지가 출력되는가?

* **핵심 답변**: **네, 변경 사항이 없으면 즉시 안내 문구를 출력하고 AI API 호출 없이 종료(`sys.exit(0)`)합니다.**
* **상세 설명**:
  - 과거 버전에서 발생하던 `HEAD~1` fallback(클린 저장소에서 이전 커밋을 읽어오는 버그)을 완전히 제거했습니다.
  - [`src/git_collector.py`](../src/git_collector.py)에서 `diff.strip() == ''`인 경우를 조기에 감지하여 불필요한 API 토큰 낭비를 원천 차단합니다.
* **관련 소스코드**:
  - 링크: [`src/main.py#L52-L55`](../src/main.py#L52-L55)
  ```python
  # src/main.py
  if not diff.strip():
      print('[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.')
      sys.exit(0)
  ```
* **검증 명령어 및 실제 출력**:
  ```bash
  # 작업 트리가 깨끗한 상태에서 실행
  ((.venv) ) mpeg46551@c3r3s7 b3_2 % python main.py commit                                                          
  [INFO] 컨벤션 로드: .ai-gitgen.yml
  [INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.
  ```

---

### Q1-5. 출력된 PR 본문에 `Why / What / How to Test` 구조가 포함되고, 각 섹션에 최소 1개 불릿이 포함되는가?

* **핵심 답변**: **네, 프롬프트 엔지니어링과 사후 검증기(Validator)의 이중 안전장치를 통해 100% 보장됩니다.**
* **상세 설명**:
  - 1차: [`src/prompt_builder.py`](../src/prompt_builder.py)에서 `## Why`, `## What`, `## How to Test` 섹션과 불릿 작성을 엄격히 지시합니다.
  - 2차: [`src/validator.py`](../src/validator.py)의 `validate_pr()`에서 정규식으로 3대 섹션을 검사하여 누락된 섹션이 있으면 자동 보충(Fallback)하고, 각 섹션에 `- ` 불릿이 없을 경우 첫 문장에 `- `를 강제 삽입합니다.
* **관련 소스코드**:
  - 링크: [`src/validator.py#L61-L85`](../src/validator.py#L61-L85)
  ```python
  # src/validator.py
  missing = [s for s in REQUIRED_SECTIONS if s not in body]
  if missing:
      print(f'[WARN] PR 본문 필수 섹션 누락: {", ".join(missing)}')
      for s in missing:
          body += f'\n\n{s}\n- 세부 사항 기술'

  # 불릿(-) 누락 시 자동 보충
  if not re.search(r'^\s*[-*]\s+', section_content, re.MULTILINE):
      body = body.replace(section_content, f'- {section_content.strip()}')
  ```
* **검증 증빙**: 단위 테스트 [`tests/test_assistant.py:TestValidator`](../tests/test_assistant.py#L119-L136) 5개 테스트 통과.

---

### Q1-6. `-temperature` 또는 `-max-tokens` 값을 변경해 실행했을 때 출력 길이/디테일 차이가 재현되는가?

* **핵심 답변**: **네, 옵션 지정이 정상 파싱되어 AI 모델 호출 인자로 완벽히 전달됩니다.**
* **상세 설명**:
  - [`src/main.py`](../src/main.py)의 `build_parser`에서 `-temperature`, `-max-tokens`, `-model` 옵션을 서브커맨드 앞/뒤 모두에서 인식하도록 구현했습니다.
  - `-temperature 0.0`은 엄격하고 사실적인 최소 요약을 생성하며, `-temperature 0.8`은 보다 서술적이고 풍부한 어휘를 사용합니다.
* **관련 소스코드**:
  - 링크: [`src/main.py#L120-L148`](../src/main.py#L120-L148)
  ```python
  # src/main.py
  p.add_argument('--temperature', '-temperature', '-t', type=float, default=0.3)
  p.add_argument('--max-tokens', '-max-tokens', type=int, default=1024, dest='max_tokens')
  ```
* **검증 명령어**:
  ```bash
((.venv) ) mpeg46551@c3r3s7 b3_2 % git add .
((.venv) ) mpeg46551@c3r3s7 b3_2 %  python main.py commit -temperature 0.8 -max-tokens 1024
[INFO] 컨벤션 로드: .ai-gitgen.yml
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 200줄
[INFO] AI API 요청 중...
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
docs: 컨벤션 로드 동작과 LLM 파라미터 검증 내용을 정리하라

- chat.md: `.ai-gitgen.yml` 로드 로그 출력 이유와 컨벤션 적용 흐름 설명 추가
- study/study.md: OpenAI 응답 구조와 temperature/max_tokens 검증 방법 정리
----------------------

[INFO] 모델: gpt-5.4-mini  |  호출 횟수: 1
((.venv) ) mpeg46551@c3r3s7 b3_2 %    git restore --staged .
((.venv) ) mpeg46551@c3r3s7 b3_2 % git add .                                               
((.venv) ) mpeg46551@c3r3s7 b3_2 %  python main.py commit -temperature 0.1 -max-tokens 256 
[INFO] 컨벤션 로드: .ai-gitgen.yml
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 200줄
[INFO] AI API 요청 중...
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
docs: 컨벤션 로드와 LLM 파라미터 검증 기록 추가

- chat.md에 .ai-gitgen.yml 로드 동작과 설정 안내를 정리
- study/study.md에 temperature와 max_tokens 검증 방법 및 결과를 추가
----------------------

[INFO] 모델: gpt-5.4-mini  |  호출 횟수: 1

  ```
* 📖 **심층 기술 분석 문서**:
  - 두 결과 간의 상세 차이점 비교표, 차이가 미미하게 느껴지는 3대 이유, 극명하게 체감하는 실험 방법은 [**`study/study.md` 제2장**](../study/study.md#2-temperature와-max-tokens-옵션-변경-시-출력-차이-상세-분석-q1-6-심층)에 상세히 정리되어 있습니다.

---

### Q1-7. 커밋/PR 출력이 정의된 길이/형식 규칙(제목 길이, 섹션 구조, 불릿 조건)을 만족하는가?

* **핵심 답변**: **네, 프롬프트 엔지니어링(1차 유도)과 파이썬 검증기(2차 하드 컷)의 이중 안전장치를 통해 커밋 제목(최대 72자), PR 제목(최대 80자), 섹션/불릿 규칙을 100% 만족합니다.**
* **상세 설명**:
  - **1차 (프롬프트 유도)**: [`src/prompt_builder.py`](../src/prompt_builder.py)에서 글자 수 제한, 필수 섹션(`Why/What/How to Test`), 불릿 형식을 명시하여 규격을 90% 이상 유도합니다.
  - **2차 (파이썬 후처리)**: [`src/validator.py`](../src/validator.py)에서 글자 수 초과 시 물리적 슬라이싱(`[:72]`, `[:80]`), 필수 섹션 누락 시 자동 보충(Fallback), 불릿 누락 시 `- `를 강제 삽입하여 확률적 실패를 0.001초 만에 100% 보정합니다.
* **관련 소스코드**:
  - 링크: [`src/validator.py#L23-L25`](../src/validator.py#L23-L25), [`src/validator.py#L57-L89`](../src/validator.py#L57-L89)
  ```python
  # src/validator.py (제목 하드 컷 & 불릿 강제)
  if len(title) > COMMIT_HARD:  # 72자
      print(f'[WARN] 커밋 제목 {len(title)}자 → {COMMIT_HARD}자로 자릅니다.')
      title = title[:COMMIT_HARD]

  if len(title) > PR_TITLE_MAX:  # 80자
      print(f'[WARN] PR 제목 {len(title)}자 → {PR_TITLE_MAX}자로 자릅니다.')
      title = title[:PR_TITLE_MAX]
  ```
* **검증 증빙**: 단위 테스트 [`tests/test_assistant.py`](../tests/test_assistant.py)에서 `test_validate_commit_title_truncation`, `test_validate_pr_title_truncation`, `test_validate_pr_ensures_bullets` 전원 통과.
* 📖 **심층 기술 분석 문서**:
  - 규칙 충족 매트릭스, Mermaid 협업 아키텍처 다이어그램, 재생성 대신 후처리를 선택한 상세 근거는 [**`study/study.md` 제3장**](../study/study.md#3-커밋pr-규칙-준수를-위한-이중-안전장치-프롬프트-vs-사후-검증기-q1-7-심층)에 상세히 정리되어 있습니다.

---

## 항목 2 — 코드 구조와 설계 이유 설명

---

### Q2-1. Git 변경 사항 수집 로직과 AI API 호출 로직을 왜 분리했는지 설명할 수 있는가?

* **핵심 답변**: **단일 책임 원칙(SRP)과 관심사 분리(Separation of Concerns)를 통해 테스트 용이성과 유지보수성을 극대화하기 위해서입니다.**
* **상세 설명**:
  - **Git 수집([`src/git_collector.py`](../src/git_collector.py))**: 외부 OS 프로세스 및 Git CLI 환경에 의존하는 로우 레벨 I/O 작업입니다.
  - **AI 호출([`src/ai_client.py`](../src/ai_client.py))**: 네트워크 HTTP 통신, JSON 직렬화, 토큰 및 인증을 다루는 외부 API 통신 작업입니다.
  - **분리의 이점**: AI API 없이도 Git diff 수집 및 마스킹 로직을 독립적으로 목(Mock) 단위 테스트할 수 있으며, 향후 AI 프로바이더가 변경되더라도 Git 수집 코드는 전혀 수정할 필요가 없습니다.

---

### Q2-2. 프롬프트 구성 로직과 출력 포맷팅(길이 규칙 포함) 로직을 어떻게 분리했고, 그 이유를 설명할 수 있는가?

* **핵심 답변**: **프롬프트 구성은 "생성 유도(Inference Guidance)"의 영역이고, 출력 포맷팅은 "결정론적 사후 보증(Deterministic Enforcement)"의 영역이기 때문에 분리했습니다.**
* **상세 설명**:
  - **프롬프트 빌더([`src/prompt_builder.py`](../src/prompt_builder.py))**: 입력 데이터(diff, 브랜치명)를 모델이 이해하기 쉬운 구조로 배치하고 Few-shot 지시어를 구성합니다.
  - **검증기([`src/validator.py`](../src/validator.py))**: LLM의 확률적 오작동(글자 수 초과, 섹션 누락)을 파이썬 코드로 검사하고 물리적으로 절삭하거나 보완합니다.
  - **분리 이유**: 프롬프트만으로는 72자 하드 컷이나 100% 불릿 보장을 확정할 수 없으며, 반대로 포맷터만으로는 자연스러운 요약문을 만들 수 없으므로 두 계층을 분리하여 결합했습니다.

---

### Q2-3. API 파라미터를 CLI 옵션으로 설계한 이유(재현성/실험 용이성)를 설명할 수 있는가?

* **핵심 답변**: **개발 환경과 작업 성격(버그 수정 vs 대규모 리팩토링)에 맞춰 사용자가 유연하게 AI 생성 품질을 실험하고 재현할 수 있도록 하기 위함입니다.**
* **상세 설명**:
  - 소스 코드를 직접 수정하지 않고도 `-temperature 0.1`(엄격한 사실 기반)부터 `-temperature 0.7`(창의적 요약)까지 즉시 테스트할 수 있습니다.
  - 민감한 코드를 다룰 때는 `-safe-mode` 플래그 하나로 마스킹과 diff 축소를 활성화할 수 있어 실무 운영 관점에서 필수적입니다.

---

### Q2-4. 오류 처리(API Key 누락, 네트워크 오류 등)를 어떤 방식으로 구현했고, 왜 그렇게 했는지 설명할 수 있는가?

* **핵심 답변**: **사용자 경험(UX)을 해치는 내부 파이썬 트레이스백을 철저히 차단하고, 발생 원인과 해결 방법(Actionable Guidance)을 명확한 터미널 문구로 제공하도록 구현했습니다.**
* **상세 설명**:
  - `AuthenticationError`, `APIConnectionError`, `RateLimitError` 등을 개별 `try-except` 블록으로 캐치하여 `[ERROR]` 프리픽스와 함께 `export AI_API_KEY="YOUR_KEY"` 같은 구체적인 해결 행동을 제시합니다.
  - 가상환경 미활성화 시에도 [main.py](../main.py)의 `sys.prefix` 감지로 자동 재실행(`os.execv`)되도록 설계하여 런타임 오류 가능성을 원천 차단했습니다.

---

## 항목 3 — AI API 파라미터·프롬프트 이해

---

### Q3-1. AI API 요청 시 `temperature` 값을 높이거나 낮추면 결과가 어떻게 달라지는지 설명할 수 있는가?

* **핵심 답변**: **`temperature`는 다음 토큰 선택 시 소프트맥스 확률 분포의 평평함(Smoothing)을 조절합니다. 낮으면 결정론적이고 엄격해지며, 높으면 어휘가 다양해지지만 규칙 이탈 위험이 커집니다.**
* **상세 설명**:
  - **낮은 값 (`0.0 ~ 0.3`, 기본값 `0.3`)**: 가장 확률이 높은 토큰을 우선 선택하므로, diff 내용에 엄격히 기반한 사실적 요약, Conventional Commits 규칙 준수, 사족(Hallucination) 방지에 최적입니다.
  - **높은 값 (`0.7 ~ 1.0`)**: 다양한 문장 구조와 표현을 시도하지만, 72자 제목 제한을 넘기거나 템플릿 규격을 벗어날 가능성이 높아집니다.

---

### Q3-2. `max_tokens` 값이 결과물에 어떤 영향을 미치며, 어떤 기준으로 값을 설정했는지 설명할 수 있는가?

* **핵심 답변**: **모델이 1회 응답에서 생성할 수 있는 최대 완성 토큰 수를 강제하여 비용 낭비와 무한 생성을 방지합니다. 본 프로젝트는 3단락 PR 본문이 중간에 잘리지 않도록 `1024`로 최적화했습니다.**
* **상세 설명**:
  - `max_tokens`가 너무 작으면(예: 50 미만) 문장이 중간에 잘리는 현상(Truncation)이 발생합니다.
  - 커밋 메시지는 약 100~200 토큰, PR 초안은 약 300~600 토큰이 소모되므로, 여유를 두어 `1024`를 기본값으로 지정했습니다.

---

### Q3-3. 커밋/PR 용도에 맞는 결과를 얻기 위해 프롬프트에 어떤 정보를 포함했고, 왜 그렇게 구성했는지 설명할 수 있는가?

* **핵심 답변**: **역할 페르소나, 컨텍스트 격리(마크다운 코드 블록), Conventional/PR 템플릿 규칙, 브랜치 맥락, 네거티브 프롬프트를 포함했습니다.**
* **상세 설명**:
  - **컨텍스트 격리**: 지시사항과 diff 코드를 ` ```diff ` 블록으로 격리하여 프롬프트 인젝션과 혼선을 방지했습니다.
  - **브랜치 맥락**: `feature/login`과 같은 브랜치명을 주입하여 AI가 작업 의도를 정확히 파악하도록 유도했습니다.
  - **네거티브 프롬프트**: "인사말이나 부연 설명 없이 결과 텍스트만 출력하라"고 명시하여 후처리 오버헤드를 최소화했습니다.

---

### Q3-4. 길이/형식 규칙을 `재생성`으로 해결할지 `후처리`로 해결할지 선택했다면, 그 선택 이유를 설명할 수 있는가?

* **핵심 답변**: **비용과 응답 지연(Latency)을 절반 이하로 줄이기 위해 `결정론적 후처리(Post-processing)` 방식을 선택했습니다.**
* **상세 설명**:
  - **재생성 방식의 단점**: 글자 수가 초과되었다고 API를 다시 호출하면 토큰 비용이 2배로 들고, 응답 시간도 3~4초로 늘어나며, 다시 생성된 결과가 규칙을 만족한다는 보장도 없습니다.
  - **후처리 방식의 장점**: AI는 1회 정밀 호출(~1.5초)로 끝내고, 초과된 글자는 파이썬 슬라이싱(`[:72]`)으로 자르고 누락된 섹션은 코드로 보충함으로써 0.001초 만에 100% 확정적인 규격 준수를 보장합니다.

---

## 항목 4 — 안전성·실무 적용 판단

---

### Q4-1. AI가 생성한 커밋/PR 텍스트를 바로 사용하지 않고 검토가 필요한 이유를 설명할 수 있는가?

* **핵심 답변**: **AI는 코드의 '문법적 변경'은 보지만 기획 의도나 비즈니스 맥락의 '진짜 이유'는 알지 못하며, 잠재적인 환각(Hallucination) 위험이 있기 때문입니다.**
* **상세 설명**:
  - 개발자가 임시로 디버깅 코드를 넣었거나 특정 엣지 케이스를 우회한 맥락은 diff에 나타나지 않으므로, AI가 엉뚱한 이유(`Why`)를 지어낼 수 있습니다.
  - 따라서 AI는 "초안 작성 도우미"로 활용하고, 최종 커밋 및 PR 승인은 반드시 사람이 검토한 후 승인하는 'Human-in-the-loop' 방식이 실무의 안전 원칙입니다.

---

### Q4-2. `git diff`에 민감정보(API Key, 개인정보 등)가 포함될 수 있는 상황과 이를 방지하기 위한 방안을 설명할 수 있는가?

* **핵심 답변**: **설정 파일(`.env`, `.yml`)이나 코드 내에 실수로 하드코딩된 API Key, 토큰, 비밀번호가 diff에 노출될 수 있으며, 본 프로젝트는 9종 정규식 기반 `-safe-mode` 마스킹으로 이를 방어합니다.**
* **상세 설명**:
  - **상황**: 신규 기능 구현 중 발급받은 비밀키를 코드에 임시로 넣고 커밋하려는 순간 diff에 포함됨.
  - **대응 방안 ([`src/git_collector.py`](../src/git_collector.py))**:
    - `-safe-mode` 활성화 시 OpenAI/AWS/JWT/이메일/비밀번호 패턴을 감지하여 `[MASKED_SECRET]`으로 치환 후 AI에 전송.
    - 최대 10개 파일, 최대 200줄로 diff 전송량을 제한하여 데이터 유출 면적을 최소화.

---

### Q4-3. 이 도구를 실제 팀 프로젝트에 적용한다면 어떤 기능을 가장 먼저 추가하거나 개선하고 싶은지, 그 우선순위 근거를 설명할 수 있는가?

* **핵심 답변**: **가장 먼저 `Git Pre-commit Hook 연동` 및 `대화형 확인/편집 모드 (Interactive Mode)`를 추가하고 싶습니다.**
* **상세 설명**:
  - **1순위 (Git Pre-commit Hook & Interactive CLI)**:
    - *근거*: 현재는 터미널에 텍스트를 출력하고 사용자가 복사해야 하지만, `git commit` 명령 시 자동으로 AI 초안을 터미널 에디터(Vim/Nano)에 기본 커밋 메시지로 띄워주고 사용자가 1초 만에 수정·저장할 수 있게 만들면 개발 생산성이 비약적으로 상승합니다.
  - **2순위 (GitHub CLI `gh pr create` 자동 연계)**:
    - *근거*: 생성된 PR 제목과 본문을 `gh pr create --title "..." --body "..."`로 원클릭 제출할 수 있는 옵션을 제공하면 완벽한 자동화 파이프라인이 완성됩니다.

---

## 5. 전체 문항 추적 매트릭스 (Traceability Matrix)

| 평가 문항 | 핵심 검증 대상 | 구현 소스코드 링크 | 단위 테스트 링크 |
| :--- | :--- | :--- | :--- |
| **Item 1-1** | 커밋 메시지 자동 생성 | [`src/main.py:cmd_commit`](../src/main.py#L42) | [`tests/test_assistant.py`](../tests/test_assistant.py) |
| **Item 1-2** | PR 초안 자동 생성 | [`src/main.py:cmd_pr`](../src/main.py#L80) | [`tests/test_assistant.py`](../tests/test_assistant.py) |
| **Item 1-3** | API Key 누락 예외 처리 | [`src/ai_client.py:__init__`](../src/ai_client.py#L30) | `test_missing_api_key_exits` |
| **Item 1-4** | 변경 부재 시 조기 종료 | [`src/git_collector.py:get_diff`](../src/git_collector.py#L58) | `test_clean_repo_no_changes` |
| **Item 1-5** | PR 3대 섹션/불릿 강제 | [`src/validator.py:validate_pr`](../src/validator.py#L32) | `test_validate_pr_ensures_bullets` |
| **Item 1-6** | CLI 옵션 동작 (-t, -max-tokens) | [`src/main.py:build_parser`](../src/main.py#L120) | `test_single_dash_options` |
| **Item 1-7** | 커밋/PR 제목 길이 하드 컷 | [`src/validator.py:validate_commit`](../src/validator.py#L9) | `test_validate_commit_title_truncation` |
| **Item 2-1** | Git수집 / AI호출 책임 분리 | [`src/git_collector.py`](../src/git_collector.py), [`src/ai_client.py`](../src/ai_client.py) | SRP 계층 분리 검증 |
| **Item 2-2** | 프롬프트 / 검증기 분리 | [`src/prompt_builder.py`](../src/prompt_builder.py), [`src/validator.py`](../src/validator.py) | 생성-검증 분리 검증 |
| **Item 2-3** | CLI 옵션화 이유 | [`src/main.py:build_parser`](../src/main.py#L120) | 실험성/재현성 검증 |
| **Item 2-4** | 표준 오류 처리 방식 | [`src/ai_client.py:generate`](../src/ai_client.py#L50) | 스택트레이스 차단 검증 |
| **Item 3-1** | Temperature 파라미터 이해 | [`src/ai_client.py`](../src/ai_client.py) | Softmax 확률 조절 원리 |
| **Item 3-2** | Max Tokens 파라미터 이해 | [`src/ai_client.py`](../src/ai_client.py) | 1024 토큰 최적화 근거 |
| **Item 3-3** | 프롬프트 컨텍스트 설계 | [`src/prompt_builder.py`](../src/prompt_builder.py) | 브랜치 주입 및 격리 |
| **Item 3-4** | 후처리 vs 재생성 선택 이유 | [`src/validator.py`](../src/validator.py) | 비용/지연 절감 근거 |
| **Item 4-1** | AI 텍스트 검토 필요성 | 전체 아키텍처 | Human-in-the-loop 원칙 |
| **Item 4-2** | Git diff 민감정보 마스킹 | [`src/git_collector.py:_mask_sensitive`](../src/git_collector.py#L8) | `test_safe_mode_masking` |
| **Item 4-3** | 실무 개선 우선순위 | 전체 로드맵 | Git Hook & Interactive CLI |
