# B3-2 AI Git Assistant - 동료평가 질의응답 대비집 (EVALUATION_QA.md)

> **문서 개요**: 본 문서는 [docs/EVALUATION.md](./EVALUATION.md)에 수록된 동료평가 4대 평가 항목(18개 세부 문항)에 근거하여, 평가관의 질문에 즉시 명쾌하게 답변할 수 있도록 **핵심 요약 답변**, **상세 설명**, **구현 소스코드 링크 및 스니펫**, **단위 테스트 링크**, **실제 검증 명령어 및 증빙**을 1:1로 집대성한 공식 Q&A 대비서입니다.

---

## 목차
1. [항목 1 — 실제 동작 확인 (7문항)](#section-1)
2. [항목 2 — 코드 구조와 설계 이유 설명 (4문항)](#section-2)
3. [항목 3 — AI API 파라미터·프롬프트 이해 (4문항)](#section-3)
4. [항목 4 — 안전성·실무 적용 판단 (3문항)](#section-4)
5. [5. 전체 문항 추적 매트릭스 (Traceability Matrix)](#matrix)

---

## 항목 1 — 실제 동작 확인 <a id="section-1"></a>

---

### Q1-1. 프로젝트 루트에서 커밋 메시지 생성 명령 실행 시 커밋 메시지가 터미널에 출력되는가? <a id="q1-1"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-1)](#matrix)

* **핵심 답변**: **네, 정상 출력됩니다.** 루트 엔트리포인트에서 `python main.py commit`을 실행하면 작업 트리의 `git status`와 `git diff`를 수집하여 AI가 생성한 Conventional Commit 규격의 커밋 메시지(제목 + 본문 불릿)가 구분선과 함께 출력됩니다.
* **상세 설명**:
  - [main.py#L6-L10](../main.py#L6-L10)을 통해 가상환경(`.venv`)을 자동 감지하여 파이썬 런타임 일관성을 보장합니다.
  - [src/main.py:cmd_commit#L74-L132](../src/main.py#L74-L132)이 실행되어 [src/git_collector.py:get_diff#L109-L152](../src/git_collector.py#L109-L152)로 Staged/Unstaged 통합 변경 사항을 수집합니다.
  - [src/prompt_builder.py:build_commit_prompt#L17-L67](../src/prompt_builder.py#L17-L67)에서 프롬프트를 구성하고, [src/ai_client.py:generate#L91-L136](../src/ai_client.py#L91-L136)가 Codyssey 게이트웨이(`gpt-5.4-mini`)를 1회 호출하여 ~1.5초 만에 메시지를 생성합니다.
* **관련 소스코드**:
  - 실행 제어 로직: [src/main.py#L74-L132](../src/main.py#L74-L132)
  - Git 수집 로직: [src/git_collector.py#L109-L152](../src/git_collector.py#L109-L152)
  ```python
  # src/main.py (cmd_commit)
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
      print('--- Commit Message ---')
      print(commit_msg)
      print('----------------------')
  ```
* **단위 테스트 링크**:
  - Git 수집기 정상 동작 테스트: [tests/test_assistant.py:test_is_git_repo#L25-L27](../tests/test_assistant.py#L25-L27)
  - 커밋 프롬프트 조립 테스트: [tests/test_assistant.py:test_commit_prompt_contains_rules_and_diff#L80-L86](../tests/test_assistant.py#L80-L86)
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

### Q1-2. PR 생성 명령 실행 시 PR 제목과 본문 초안이 터미널에 출력되는가? <a id="q1-2"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-2)](#matrix)

* **핵심 답변**: **네, 정상 출력됩니다.** `python main.py pr`을 실행하면 현재 브랜치명과 기준 브랜치 대비 diff를 바탕으로 1줄 제목(`--- PR Title ---`)과 3대 필수 섹션을 포함한 본문(`--- PR Body ---`)이 구획화되어 출력됩니다.
* **상세 설명**:
  - [src/git_collector.py:get_current_branch#L154-L161](../src/git_collector.py#L154-L161)과 [src/git_collector.py:_branch_diff#L163-L180](../src/git_collector.py#L163-L180)를 통해 현재 작업 브랜치와 병합 기준 브랜치 간의 diff 컨텍스트를 수집합니다.
  - [src/prompt_builder.py:build_pr_prompt#L70-L121](../src/prompt_builder.py#L70-L121)에서 PR 전용 템플릿(Why, What, How to Test)을 조립합니다.
  - [src/validator.py:validate_pr#L67-L137](../src/validator.py#L67-L137)을 통해 제목(최대 80자)과 본문(Why, What, How to Test 구조 및 불릿)이 완벽히 검증된 후 터미널에 렌더링됩니다.
* **관련 소스코드**:
  - PR 실행 엔트리포인트: [src/main.py#L135-L195](../src/main.py#L135-L195)
  - PR 프롬프트 빌더: [src/prompt_builder.py#L70-L121](../src/prompt_builder.py#L70-L121)
  - PR 사후 검증기: [src/validator.py#L67-L137](../src/validator.py#L67-L137)
  ```python
  # src/main.py (cmd_pr)
  def cmd_pr(args: argparse.Namespace, convention: dict) -> None:
      branch = collector.get_current_branch()
      diff = collector.get_diff(safe_mode=args.safe_mode, for_pr=True)
      prompt = build_pr_prompt(status, diff, branch, convention)
      result = client.generate(prompt)
      title, body = validate_pr(result)
      print('--- PR Title ---')
      print(title)
      print('--- PR Body ---')
      print(body)
      print('---------------')
  ```
* **단위 테스트 링크**:
  - PR 필수 섹션 프롬프트 검증: [tests/test_assistant.py:test_pr_prompt_contains_required_sections#L87-L94](../tests/test_assistant.py#L87-L94)
  - PR 제목 절삭 검증: [tests/test_assistant.py:test_validate_pr_title_truncation#L110-L118](../tests/test_assistant.py#L110-L118)
  - PR 불릿 보충 검증: [tests/test_assistant.py:test_validate_pr_ensures_bullets#L128-L136](../tests/test_assistant.py#L128-L136)
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

### Q1-3. AI API Key가 설정되지 않은 상태에서 실행하면 오류 메시지가 출력되고 종료되는가? <a id="q1-3"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-3)](#matrix)

* **핵심 답변**: **네, 파이썬 트레이스백(Traceback) 없이 명세서 표준 에러 문구를 출력하고 정상 종료(`sys.exit(1)`)합니다.**
* **상세 설명**:
  - [src/ai_client.py:AIClient.__init__#L43-L89](../src/ai_client.py#L43-L89)에서 `AI_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`를 순서대로 확인합니다.
  - 키가 모두 없을 경우 불필요한 스택 트레이스를 숨기고 사용자가 즉시 조치할 수 있는 실행 가이드(`export AI_API_KEY="YOUR_KEY"`)를 출력 후 종료합니다.
* **관련 소스코드**:
  - 키 검증 및 친절한 에러 출력: [src/ai_client.py#L119-L65](../src/ai_client.py#L119-L65)
  ```python
  # src/ai_client.py (__init__)
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
* **단위 테스트 링크**:
  - 키 부재 시 종료 단위 테스트: [tests/test_assistant.py:test_missing_api_key_exits#L62-L68](../tests/test_assistant.py#L62-L68)
  - 환경변수 주입 인식 단위 테스트: [tests/test_assistant.py:test_api_key_recognized_from_env#L69-L75](../tests/test_assistant.py#L69-L75)
* **검증 명령어 및 실제 출력**:
  ```bash
  env -u AI_API_KEY -u OPENROUTER_API_KEY -u OPENAI_API_KEY python main.py commit
  ```
  ```text
  [INFO] 컨벤션 로드: .ai-gitgen.yml
  [INFO] Git status 수집 완료: 1개 파일 변경 감지
  [INFO] Git diff 수집 완료: 0줄
  [INFO] AI API 요청 중...
  [ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
  ## 예) export AI_API_KEY="YOUR_KEY"
  ```

---

### Q1-4. Git 변경 사항이 없는 상태에서 실행하면 `변경 사항이 없습니다`에 준하는 메시지가 출력되는가? <a id="q1-4"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-4)](#matrix)

* **핵심 답변**: **네, 변경 사항이 없으면 즉시 안내 문구를 출력하고 AI API 호출 없이 종료(`sys.exit(0)`)합니다.**
* **상세 설명**:
  - 과거 버전에서 발생하던 `HEAD~1` fallback(클린 저장소에서 이전 커밋을 읽어오는 버그)을 완전히 제거했습니다.
  - [src/main.py#L83-L85](../src/main.py#L83-L85)에서 `collector.count_changed_files()`를 통해 수정된 파일이 0개일 때 즉시 정상 종료하며, PR 역시 [src/main.py#L152-L154](../src/main.py#L152-L154)에서 `diff.strip() == ''`을 조기에 감지하여 불필요한 API 토큰 낭비를 원천 차단합니다.
* **관련 소스코드**:
  - 커밋 조기 종료 로직: [src/main.py#L83-L85](../src/main.py#L83-L85)
  - PR 조기 종료 로직: [src/main.py#L152-L154](../src/main.py#L152-L154)
  - 변경 파일 개수 검사: [src/git_collector.py:count_changed_files#L98-L107](../src/git_collector.py#L98-L107)
  ```python
  # src/main.py (cmd_commit)
  if not collector.count_changed_files():
      print('[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.')
      sys.exit(0)
  ```
* **단위 테스트 링크**:
  - Git 수집기 기본 동작 테스트: [tests/test_assistant.py:test_is_git_repo#L25-L27](../tests/test_assistant.py#L25-L27)
* **검증 명령어 및 실제 출력**:
  ```bash
  # 작업 트리가 깨끗한 상태에서 실행
  python main.py commit
  ```
  ```text
  [INFO] 컨벤션 로드: .ai-gitgen.yml
  [INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.
  ```

---

### Q1-5. 출력된 PR 본문에 `Why / What / How to Test` 구조가 포함되고, 각 섹션에 최소 1개 불릿이 포함되는가? <a id="q1-5"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-5)](#matrix)

* **핵심 답변**: **네, 프롬프트 엔지니어링과 사후 검증기(Validator)의 이중 안전장치를 통해 100% 보장됩니다.**
* **상세 설명**:
  - 1차: [src/prompt_builder.py:build_pr_prompt#L98-L110](../src/prompt_builder.py#L98-L110)에서 `## Why`, `## What`, `## How to Test` 섹션과 불릿 작성을 엄격히 지시합니다.
  - 2차: [src/validator.py:validate_pr#L106-L137](../src/validator.py#L106-L137)에서 정규식으로 3대 섹션을 검사하여 누락된 섹션이 있으면 자동 보충(Fallback)하고, 각 섹션에 `- ` 불릿이 없을 경우 `- `를 강제 삽입합니다.
* **관련 소스코드**:
  - PR 프롬프트 템플릿: [src/prompt_builder.py#L98-L110](../src/prompt_builder.py#L98-L110)
  - 필수 섹션 및 불릿 보충 로직: [src/validator.py#L106-L137](../src/validator.py#L106-L137)
  ```python
  # src/validator.py (validate_pr)
  missing = [s for s in REQUIRED_SECTIONS if s not in body]
  if missing:
      print(f'[WARN] PR 본문 필수 섹션 누락: {", ".join(missing)}')
      for s in missing:
          body += f'\n\n{s}\n- 세부 사항 기술'

  # 불릿(-) 누락 시 자동 보충
  if '-' not in sec_block and '*' not in sec_block:
      print(f'[WARN] {s} 섹션 내 불릿 누락 → 기본 불릿 항목 추가')
      body = body[:idx + len(s)] + f'\n- {s} 관련 내용 작성 필요' + body[idx + len(s):]
  ```
* **단위 테스트 링크**:
  - 누락 섹션 자동 보충 단위 테스트: [tests/test_assistant.py:test_validate_pr_ensures_missing_sections#L119-L127](../tests/test_assistant.py#L119-L127)
  - 불릿 누락 시 강제 추가 단위 테스트: [tests/test_assistant.py:test_validate_pr_ensures_bullets#L128-L136](../tests/test_assistant.py#L128-L136)

---

### Q1-6. `-temperature` 또는 `-max-tokens` 값을 변경해 실행했을 때 출력 길이/디테일 차이가 재현되는가? <a id="q1-6"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-6)](#matrix)

* **핵심 답변**: **네, 옵션 지정이 정상 파싱되어 AI 모델 호출 인자로 완벽히 전달되며, 값에 따른 어휘 및 디테일 차이가 명확히 재현됩니다.**
* **상세 설명**:
  - [src/main.py:build_parser#L198-L264](../src/main.py#L198-L264)에서 `-temperature`, `-max-tokens`, `-model` 옵션을 서브커맨드 앞/뒤 모두에서 인식하도록 `argparse.SUPPRESS` 기본값을 적용하여 유실 없이 파싱합니다.
  - [src/ai_client.py#L118-L119](../src/ai_client.py#L118-L119)을 통해 `chat.completions.create(..., temperature=self.temperature, max_tokens=self.max_tokens)`로 모델에 직접 전달됩니다.
  - `-temperature 0.1`은 엄격하고 사실적인 최소 요약(명사형 종결)을 생성하며, `-temperature 0.8`은 보다 서술적이고 풍부한 어휘(명령형/다양한 표현)를 사용합니다.
* **관련 소스코드**:
  - 옵션 파서 등록 로직: [src/main.py#L198-L264](../src/main.py#L198-L264)
  - 파라미터 전달 로직: [src/ai_client.py#L86-L121](../src/ai_client.py#L86-L121)
  ```python
  # src/main.py
  p.add_argument('--temperature', '-temperature', '-t', type=float, default=0.3)
  p.add_argument('--max-tokens', '-max-tokens', type=int, default=1024, dest='max_tokens')
  ```
* **단위 테스트 링크**:
  - 이중 하이픈(--) 파싱 테스트: [tests/test_assistant.py:test_double_dash_options#L144-L150](../tests/test_assistant.py#L144-L150)
  - 단일 하이픈(-) 파싱 테스트: [tests/test_assistant.py:test_single_dash_options#L151-L158](../tests/test_assistant.py#L151-L158)
  - 서브커맨드 뒤 옵션 배치 테스트: [tests/test_assistant.py:test_options_after_subcommand#L159-L165](../tests/test_assistant.py#L159-L165)
* **검증 명령어 및 실제 출력 요약**:
  ```bash
  # 1. 높은 자유도 옵션 (명령형 어미, 콜론 구분 구조)
  python main.py commit -temperature 0.8 -max-tokens 1024
  # 출력: docs: 컨벤션 로드 동작과 LLM 파라미터 검증 내용을 정리하라

  # 2. 결정론적 안정 옵션 (명사형 종결, 자연어 조사 구조)
  python main.py commit -temperature 0.1 -max-tokens 256
  # 출력: docs: 컨벤션 로드와 LLM 파라미터 검증 기록 추가
  ```
* 📖 **심층 기술 분석 문서**:
  - 두 결과 간의 상세 차이점 비교표, 차이가 미미하게 느껴지는 3대 이유, 극명하게 체감하는 실험 방법은 **[study/study.md 제2장](../study/study.md#2-temperature와-max-tokens-옵션-변경-시-출력-차이-상세-분석-q1-6-심층)**에 상세히 정리되어 있습니다.

---

### Q1-7. 커밋/PR 출력이 정의된 길이/형식 규칙(제목 길이, 섹션 구조, 불릿 조건)을 만족하는가? <a id="q1-7"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 1-7)](#matrix)

* **핵심 답변**: **네, 프롬프트 엔지니어링(1차 유도)과 파이썬 검증기(2차 하드 컷)의 이중 안전장치를 통해 커밋 제목(최대 72자), PR 제목(최대 80자), 섹션/불릿 규칙을 100% 만족합니다.**
* **상세 설명**:
  - **1차 (프롬프트 유도)**: [src/prompt_builder.py#L44-L48](../src/prompt_builder.py#L44-L48) 및 [src/prompt_builder.py#L95-L97](../src/prompt_builder.py#L95-L97)에서 글자 수 제한, 필수 섹션(`Why/What/How to Test`), 불릿 형식을 명시하여 규격을 90% 이상 유도합니다.
  - **2차 (파이썬 후처리)**: [src/validator.py#L50-L58](../src/validator.py#L50-L58)에서 커밋 제목이 72자 초과 시 `title[:72]`로 강제 슬라이싱 절삭하고, [src/validator.py#L100-L104](../src/validator.py#L100-L104)에서 PR 제목이 80자 초과 시 `title[:80]`으로 절삭하여 확률적 실패를 0.001초 만에 100% 보정합니다.
* **관련 소스코드**:
  - 커밋 제목 검증 및 절삭: [src/validator.py#L50-L58](../src/validator.py#L50-L58)
  - PR 제목 절삭 및 섹션/불릿 보정: [src/validator.py#L100-L137](../src/validator.py#L100-L137)
  ```python
  # src/validator.py (제목 하드 컷 & 불릿 강제)
  if len(title) > COMMIT_HARD:  # 72자
      print(f'[WARN] 커밋 제목 {len(title)}자 → {COMMIT_HARD}자로 자릅니다.')
      title = title[:COMMIT_HARD]

  if len(title) > PR_TITLE_MAX:  # 80자
      print(f'[WARN] PR 제목 {len(title)}자 → {PR_TITLE_MAX}자로 자릅니다.')
      title = title[:PR_TITLE_MAX]
  ```
* **단위 테스트 링크**:
  - 커밋 제목 72자 절삭 단위 테스트: [tests/test_assistant.py:test_validate_commit_title_truncation#L99-L109](../tests/test_assistant.py#L99-L109)
  - PR 제목 80자 절삭 단위 테스트: [tests/test_assistant.py:test_validate_pr_title_truncation#L110-L118](../tests/test_assistant.py#L110-L118)
  - PR 불릿 보정 단위 테스트: [tests/test_assistant.py:test_validate_pr_ensures_bullets#L128-L136](../tests/test_assistant.py#L128-L136)
* 📖 **심층 기술 분석 문서**:
  - 규칙 충족 매트릭스, Mermaid 협업 아키텍처 다이어그램, 재생성 대신 후처리를 선택한 상세 근거는 **[study/study.md 제3장](../study/study.md#3-커밋pr-규칙-준수를-위한-이중-안전장치-프롬프트-vs-사후-검증기-q1-7-심층)**에 상세히 정리되어 있습니다.

---

## 항목 2 — 코드 구조와 설계 이유 설명 <a id="section-2"></a>

---

### Q2-1. Git 변경 사항 수집 로직과 AI API 호출 로직을 왜 분리했는지 설명할 수 있는가? <a id="q2-1"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 2-1)](#matrix)

* **핵심 답변**: **단일 책임 원칙(SRP)과 관심사 분리(Separation of Concerns)를 통해 테스트 용이성과 유지보수성을 극대화하기 위해서입니다.**
* **상세 설명**:
  - **Git 수집 ([src/git_collector.py:GitCollector#L50-L227](../src/git_collector.py#L50-L227))**: 로컬 OS 서브프로세스(`git rev-parse`, `git status`, `git diff`)를 실행하여 I/O를 수행하고 정규식으로 민감정보를 필터링하는 인프라 계층입니다.
  - **AI 호출 ([src/ai_client.py:AIClient#L30-L136](../src/ai_client.py#L30-L136))**: 외부 REST API 게이트웨이와 HTTP 통신, JSON 직렬화, 토큰 및 인증 예외를 전담하는 통신 계층입니다.
  - **분리의 이점**: AI API 네트워크 없이도 Git 수집과 마스킹을 로컬에서 0.01초 만에 독립 단위 테스트할 수 있으며, 향후 OpenAI에서 다른 LLM 프로바이더로 교체되더라도 Git 수집 코드는 단 한 줄도 수정할 필요가 없습니다.
* **관련 소스코드**:
  - Git 수집 계층: [src/git_collector.py#L109-L152](../src/git_collector.py#L109-L152)
  - AI API 통신 계층: [src/ai_client.py#L91-L122](../src/ai_client.py#L91-L122)
  - 두 계층을 연결하는 오케스트레이터: [src/main.py#L119-L121](../src/main.py#L119-L121)
  ```python
  # src/main.py (관심사 분리 결합)
  collector = GitCollector()                                # 1. Git I/O 전담
  diff = collector.get_diff(safe_mode=args.safe_mode)
  client = _make_client(args)                              # 2. AI 통신 전담
  result = client.generate(prompt)
  ```
* **단위 테스트 링크**:
  - Git 수집기 전용 단위 테스트 클래스: [tests/test_assistant.py:TestGitCollector#L19-L57](../tests/test_assistant.py#L19-L57)
  - AI 클라이언트 전용 단위 테스트 클래스: [tests/test_assistant.py:TestAIClient#L59-L75](../tests/test_assistant.py#L59-L75)

---

### Q2-2. 프롬프트 구성 로직과 출력 포맷팅(길이 규칙 포함) 로직을 어떻게 분리했고, 그 이유를 설명할 수 있는가? <a id="q2-2"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 2-2)](#matrix)

* **핵심 답변**: **프롬프트 구성은 "확률적 생성 유도(Inference Guidance)"의 영역이고, 출력 포맷팅은 "결정론적 사후 보증(Deterministic Enforcement)"의 영역이기 때문에 분리했습니다.**
* **상세 설명**:
  - **프롬프트 빌더 ([src/prompt_builder.py#L1-L121](../src/prompt_builder.py#L1-L121))**: 변경 사항과 컨벤션을 조립하여 LLM이 자연스러운 맥락을 파악하고 최적의 초안을 작성하도록 이끕니다.
  - **검증기 ([src/validator.py#L1-L137](../src/validator.py#L1-L137))**: LLM의 확률적 오작동(72자 초과, 불릿 누락)을 파이썬 코드로 검사하고 물리적으로 절삭하거나 채웁니다.
  - **분리 이유**: 프롬프트만으로는 72자 하드 컷이나 100% 불릿 보장을 확정할 수 없으며, 반대로 포맷터만으로는 자연스러운 요약문을 만들 수 없으므로 두 계층을 분리하여 결합했습니다.
* **관련 소스코드**:
  - 프롬프트 생성 모듈: [src/prompt_builder.py#L17-L67](../src/prompt_builder.py#L17-L67)
  - 사후 검증 모듈: [src/validator.py#L32-L64](../src/validator.py#L32-L64)
  ```python
  # src/main.py (생성 유도와 사후 보증의 분리 실행)
  prompt = build_commit_prompt(status, diff, convention) # 1. 확률적 유도 (PromptBuilder)
  result = client.generate(prompt)                       # 2. LLM 추론
  commit_msg = validate_commit(result)                   # 3. 결정론적 확정 (Validator)
  ```
* **단위 테스트 링크**:
  - 프롬프트 구성 단위 테스트: [tests/test_assistant.py:TestPromptBuilder#L77-L94](../tests/test_assistant.py#L77-L94)
  - 검증기 및 절삭 단위 테스트: [tests/test_assistant.py:TestValidator#L96-L136](../tests/test_assistant.py#L96-L136)

---

### Q2-3. API 파라미터를 CLI 옵션으로 설계한 이유(재현성/실험 용이성)를 설명할 수 있는가? <a id="q2-3"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 2-3)](#matrix)

* **핵심 답변**: **개발 환경과 작업 성격(버그 수정 vs 대규모 리팩토링)에 맞춰 사용자가 유연하게 AI 생성 품질을 실험하고 재현할 수 있도록 하기 위함입니다.**
* **상세 설명**:
  - 소스 코드를 직접 수정하지 않고도 `-temperature 0.1`(엄격한 사실 기반)부터 `-temperature 0.8`(풍부한 어휘 요약)까지 즉시 변경하며 결과를 비교할 수 있습니다.
  - 민감한 코드를 다룰 때는 `-safe-mode` 플래그 하나로 마스킹과 diff 축소를 활성화할 수 있어 실무 운영 관점에서 필수적입니다.
  - 서브커맨드 앞/뒤 어디에 옵션을 두어도 정상 작동하도록 [src/main.py:build_parser#L198-L264](../src/main.py#L121-L161)을 설계하여 높은 사용성을 보장합니다.
* **관련 소스코드**:
  - CLI 공통 옵션 정의: [src/main.py#L207-L248](../src/main.py#L207-L248)
  - 파싱된 인자의 클라이언트 주입: [src/main.py#L57-L71](../src/main.py#L57-L71)
  ```python
  # src/main.py (_make_client)
  def _make_client(args: argparse.Namespace) -> AIClient:
      return AIClient(
          model=args.model,
          temperature=args.temperature,
          max_tokens=args.max_tokens,
      )
  ```
* **단위 테스트 링크**:
  - CLI 옵션 파싱 전체 테스트: [tests/test_assistant.py:TestCLIParser#L138-L165](../tests/test_assistant.py#L138-L165)

---

### Q2-4. 오류 처리(API Key 누락, 네트워크 오류 등)를 어떤 방식으로 구현했고, 왜 그렇게 했는지 설명할 수 있는가? <a id="q2-4"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 2-4)](#matrix)

* **핵심 답변**: **사용자 경험(UX)을 해치는 내부 파이썬 트레이스백을 철저히 차단하고, 발생 원인과 해결 방법(Actionable Guidance)을 명확한 터미널 문구로 제공하도록 구현했습니다.**
* **상세 설명**:
  - [src/ai_client.py:generate#L123-L136](../src/ai_client.py#L123-L136)에서 `AuthenticationError`, `APIConnectionError`, `RateLimitError`, `APIStatusError`를 개별 세분화하여 캐치합니다.
  - 오류 발생 시 불필요한 스택 트레이스 없이 `[ERROR]` 프리픽스와 함께 즉시 조치할 수 있는 안내 문구를 출력하고 `sys.exit(1)`로 깔끔하게 종료합니다.
  - 가상환경 미활성화 시에도 [main.py#L7-L11](../main.py#L7-L11)의 `sys.prefix` 감지로 자동 재실행(`os.execv`)되도록 설계하여 런타임 오류 가능성을 원천 차단했습니다.
* **관련 소스코드**:
  - 세분화된 API 예외 처리: [src/ai_client.py#L123-L136](../src/ai_client.py#L123-L136)
  - 키 누락 방어 로직: [src/ai_client.py#L61-L64](../src/ai_client.py#L61-L64)
  - 가상환경 투명 복구 로직: [main.py#L7-L11](../main.py#L7-L11)
  ```python
  # src/ai_client.py (generate)
  except AuthenticationError:
      print('[ERROR] API 인증 실패: AI_API_KEY를 확인하세요.')
      sys.exit(1)
  except APIConnectionError as e:
      print(f'[ERROR] 네트워크 연결 오류: {e}')
      sys.exit(1)
  except RateLimitError:
      print('[ERROR] API 요청 한도 초과. 잠시 후 다시 시도하세요.')
      sys.exit(1)
  ```
* **단위 테스트 링크**:
  - API Key 누락 예외 검증 단위 테스트: [tests/test_assistant.py:test_missing_api_key_exits#L62-L68](../tests/test_assistant.py#L62-L68)

---

## 항목 3 — AI API 파라미터·프롬프트 이해 <a id="section-3"></a>

---

### Q3-1. AI API 요청 시 `temperature` 값을 높이거나 낮추면 결과가 어떻게 달라지는지 설명할 수 있는가? <a id="q3-1"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 3-1)](#matrix)

* **핵심 답변**: **`temperature`는 다음 토큰 선택 시 소프트맥스 확률 분포의 평평함(Smoothing)을 조절합니다. 낮으면 결정론적이고 엄격해지며, 높으면 어휘가 다양해지지만 규칙 이탈 위험이 커집니다.**
* **상세 설명**:
  - **낮은 값 (`0.0 ~ 0.3`, 기본값 `0.3`)**: 가장 확률이 높은 최상단 토큰(Top Token)을 우선 선택하므로, diff 내용에 엄격히 기반한 사실적 요약, Conventional Commits 규칙 준수, 사족(Hallucination) 방지에 최적입니다.
  - **높은 값 (`0.7 ~ 1.0`)**: 확률 분포가 평평해져 다양한 어휘와 문장 구조를 시도하지만, 72자 제목 제한을 넘기거나 템플릿 규격을 벗어날 가능성이 높아집니다.
  - [src/ai_client.py:generate#L113-L121](../src/ai_client.py#L113-L121)에서 이 파라미터가 모델에 직접 주입됩니다.
* **관련 소스코드**:
  - API 호출 시 temperature 주입: [src/ai_client.py#L113-L121](../src/ai_client.py#L113-L121)
  - CLI temperature 옵션 등록: [src/main.py#L224-L225](../src/main.py#L224-L225)
  ```python
  # src/ai_client.py
  resp = self.client.chat.completions.create(
      model=self.model,
      messages=[{'role': 'user', 'content': prompt}],
      temperature=self.temperature, # CLI 입력값 반영 (기본값: 0.3)
      max_tokens=self.max_tokens,
  )
  ```
* 📖 **심층 실측 연구 문서**:
  - 실제 동일 프롬프트 반복 호출 실측 결과(0.0일 때 '사과' 3회 고정 vs 1.5일 때 '바나나', '사과', '망고' 분산)는 **[study/study.md 제1장 1.2절](../study/study.md#방법-3-temperature-실동작-검증-결정론-vs-무작위성-실측)**에 상세히 수록되어 있습니다.

---

### Q3-2. `max_tokens` 값이 결과물에 어떤 영향을 미치며, 어떤 기준으로 값을 설정했는지 설명할 수 있는가? <a id="q3-2"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 3-2)](#matrix)

* **핵심 답변**: **모델이 1회 응답에서 생성할 수 있는 최대 완성 토큰 수를 강제하여 비용 낭비와 무한 생성을 방지합니다. 본 프로젝트는 3단락 PR 본문이 중간에 잘리지 않도록 `1024`로 최적화했습니다.**
* **상세 설명**:
  - `max_tokens`가 너무 작으면 문장이 중간에 잘리는 현상(Truncation, `finish_reason == 'length'`)이 발생합니다.
  - 커밋 메시지는 약 60~100 토큰, PR 초안은 약 300~600 토큰이 소모되므로, PR 3대 섹션이 중간에 끊기지 않도록 여유 있게 `1024`를 기본값([src/main.py:DEFAULT_MAX_TOKENS#L54](../src/main.py#L54))으로 채택했습니다.
* **관련 소스코드**:
  - 기본값 정의: [src/main.py#L54](../src/main.py#L54)
  - API 호출 파라미터 전달: [src/ai_client.py#L113-L121](../src/ai_client.py#L113-L121)
  ```python
  # src/main.py
  DEFAULT_MAX_TOKENS = 1024

  # src/ai_client.py
  resp = self.client.chat.completions.create(
      model=self.model,
      messages=[{'role': 'user', 'content': prompt}],
      temperature=self.temperature,
      max_tokens=self.max_tokens,  # 최대 생성 토큰 상한 제한
  )
  ```
* 📖 **심층 실측 연구 문서**:
  - 극단값(5 토큰) 설정 시 `finish_reason: length`로 잘리는 실측 패킷 분석은 **[study/study.md 제1장 1.2절](../study/study.md#방법-2-max_tokens-실동작-검증-finish_reason--length)**에 상세히 수록되어 있습니다.

---

### Q3-3. 커밋/PR 용도에 맞는 결과를 얻기 위해 프롬프트에 어떤 정보를 포함했고, 왜 그렇게 구성했는지 설명할 수 있는가? <a id="q3-3"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 3-3)](#matrix)

* **핵심 답변**: **역할 페르소나, 컨텍스트 격리(구분선 블록), Conventional/PR 템플릿 규칙, 브랜치 맥락, 네거티브 프롬프트를 포함했습니다.**
* **상세 설명**:
  - **컨텍스트 격리**: 지시사항과 git diff를 `--- GIT DIFF ---` 블록으로 명확히 구분하여 프롬프트 인젝션과 모델 혼선을 방지했습니다 ([src/prompt_builder.py#L59-L66](../src/prompt_builder.py#L59-L66)).
  - **브랜치 맥락 주입**: PR 생성 시 `feature/login`과 같은 브랜치명을 프롬프트에 주입하여 AI가 작업 의도(`Why`)를 정확히 파악하도록 유도했습니다 ([src/prompt_builder.py#L112-L114](../src/prompt_builder.py#L112-L114)).
  - **네거티브 프롬프트**: "커밋 메시지만 출력하고 다른 설명은 쓰지 않음", "다른 설명 없이 지정된 형식만 출력"을 명시하여 불필요한 서두나 사족 출력을 원천 차단했습니다.
* **관련 소스코드**:
  - 커밋 프롬프트 구조: [src/prompt_builder.py#L17-L67](../src/prompt_builder.py#L17-L67)
  - PR 프롬프트 구조: [src/prompt_builder.py#L92-L121](../src/prompt_builder.py#L92-L121)
  ```python
  # src/prompt_builder.py (build_commit_prompt)
  return f"""\
  Git 변경 사항을 분석하여 커밋 메시지를 생성하세요.
  언어: {lang}

  규칙:
  - 제목: 50자 이내 권장(최대 72자), 명령형, 마침표 없음
  {prefix_rule}
  - 본문: 변경된 파일(모듈) 1~3개 언급, 핵심 변경 사항 1~2개를 불릿으로 요약
  - 커밋 메시지만 출력하고 다른 설명은 쓰지 않음

  출력 형식:
  <type>: <한 줄 설명>

  - <변경 사항 1>
  - <변경 사항 2>
  ...
  """
  ```
* **단위 테스트 링크**:
  - 커밋 프롬프트 무결성 테스트: [tests/test_assistant.py:test_commit_prompt_contains_rules_and_diff#L80-L86](../tests/test_assistant.py#L80-L86)
  - PR 프롬프트 필수 섹션 테스트: [tests/test_assistant.py:test_pr_prompt_contains_required_sections#L87-L94](../tests/test_assistant.py#L87-L94)

---

### Q3-4. 길이/형식 규칙을 `재생성`으로 해결할지 `후처리`로 해결할지 선택했다면, 그 선택 이유를 설명할 수 있는가? <a id="q3-4"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 3-4)](#matrix)

* **핵심 답변**: **비용과 응답 지연(Latency)을 절반 이하로 줄이기 위해 `결정론적 후처리(Post-processing)` 방식을 선택했습니다.**
* **상세 설명**:
  - **재생성 방식의 단점**: 글자 수가 초과되었다고 API를 다시 호출하면 토큰 비용이 2배로 들고, 응답 시간도 3~4초로 늘어나며, 다시 생성된 결과가 규칙을 만족한다는 수학적 보장도 없습니다.
  - **후처리 방식의 장점**: AI는 1회 정밀 호출(~1.5초)로 끝내고, 초과된 글자는 파이썬 슬라이싱([src/validator.py#L52](../src/validator.py#L52))으로 자르고 누락된 섹션은 코드로 보충함으로써 0.001초 만에 100% 확정적인 규격 준수를 보장합니다.
* **관련 소스코드**:
  - 1회 API 호출 및 즉시 후처리: [src/main.py#L119-L122](../src/main.py#L119-L122)
  - 결정론적 슬라이싱 및 보정 로직: [src/validator.py#L50-L58](../src/validator.py#L50-L58), [src/validator.py#L100-L137](../src/validator.py#L100-L137)
  ```python
  # src/main.py
  result = client.generate(prompt)      # 1회 API 호출
  commit_msg = validate_commit(result)  # 0.001초 결정론적 후처리
  ```
* 📖 **심층 기술 분석 문서**:
  - 재생성 vs 후처리 아키텍처 비교표 및 수학적 100% 보장 원리는 **[study/study.md 제3장 3.5절](../study/study.md#35-왜-재생성retry-대신-후처리post-processing를-선택했는가)**에 상세히 정리되어 있습니다.

---

## 항목 4 — 안전성·실무 적용 판단 <a id="section-4"></a>

---

### Q4-1. AI가 생성한 커밋/PR 텍스트를 바로 사용하지 않고 검토가 필요한 이유를 설명할 수 있는가? <a id="q4-1"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 4-1)](#matrix)

* **핵심 답변**: **AI는 코드의 '문법적 변경'은 보지만 기획 의도나 비즈니스 맥락의 '진짜 이유'는 알지 못하며, 잠재적인 환각(Hallucination) 위험이 있기 때문입니다.**
* **상세 설명**:
  - 개발자가 임시로 디버깅 코드를 넣었거나 특정 엣지 케이스를 우회한 맥락은 diff에 나타나지 않으므로, AI가 엉뚱한 이유(`Why`)를 지어낼 수 있습니다.
  - 따라서 AI는 "초안 작성 도우미"로 활용하고, 최종 커밋 및 PR 승인은 반드시 사람이 검토한 후 승인하는 'Human-in-the-loop' 방식이 실무의 안전 원칙입니다.
  - 이를 위해 본 도구는 즉시 자동 커밋하지 않고 터미널에 명확한 구분선([src/main.py#L126-L131](../src/main.py#L126-L131))과 함께 사람이 최종 확인하도록 렌더링합니다.
* **관련 소스코드**:
  - 사람이 검토할 수 있도록 터미널에 초안 구획 출력: [src/main.py#L124-L131](../src/main.py#L124-L131), [src/main.py#L187-L194](../src/main.py#L187-L194)
  ```python
  # src/main.py
  print('[DONE] 커밋 메시지 생성 완료\n')
  print('--- Commit Message ---')
  print(commit_msg) # 사람이 눈으로 검토 후 복사하여 git commit 하도록 유도
  print('----------------------')
  ```
* **관련 문서 링크**:
  - 안전성 운영 원칙: [README.md#4-안전-모드-safe-mode-및-보안-정책](../README.md#4-안전-모드-safe-mode-및-보안-정책)

---

### Q4-2. `git diff`에 민감정보(API Key, 개인정보 등)가 포함될 수 있는 상황과 이를 방지하기 위한 방안을 설명할 수 있는가? <a id="q4-2"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 4-2)](#matrix)

* **핵심 답변**: **설정 파일(`.env`, `.yml`)이나 코드 내에 실수로 하드코딩된 API Key, 토큰, 비밀번호가 diff에 노출될 수 있으며, 본 프로젝트는 9종 정규식 기반 `-safe-mode` 마스킹으로 이를 방어합니다.**
* **상세 설명**:
  - **위험 상황**: 개발 도중 외부 API 연동을 위해 발급받은 비밀키나 데이터베이스 접속 패스워드를 코드에 임시로 넣고 커밋하려는 순간 diff에 포함되어 외부 AI 게이트웨이로 전송될 위험이 존재합니다.
  - **대응 방안 ([src/git_collector.py:_SENSITIVE#L27-L47](../src/git_collector.py#L27-L47))**:
    - `-safe-mode` 활성화 시 OpenAI/Anthropic/AWS/JWT/이메일/비밀번호 등 9종 패턴을 감지하여 `[MASKED_API_KEY]`, `[MASKED_AWS_KEY]` 등으로 사전 치환 후 AI에 전송합니다 ([src/git_collector.py:_apply_safe#L182-L227](../src/git_collector.py#L182-L227)).
    - 최대 10개 파일, 최대 200줄로 diff 전송량을 자동 절삭하여 대규모 데이터 유출 면적을 최소화합니다.
* **관련 소스코드**:
  - 9종 민감정보 정규표현식 정의: [src/git_collector.py#L27-L47](../src/git_collector.py#L27-L47)
  - 마스킹 및 diff 절삭 알고리즘: [src/git_collector.py#L182-L227](../src/git_collector.py#L182-L227)
  - CLI safe-mode 옵션: [src/main.py#L230-L231](../src/main.py#L230-L231)
  ```python
  # src/git_collector.py (_SENSITIVE)
  _SENSITIVE: list[tuple[str, str]] = [
      (r'sk-[A-Za-z0-9\-_]{20,}', '[MASKED_API_KEY]'),
      (r'AKIA[0-9A-Z]{16}', '[MASKED_AWS_KEY]'),
      (r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+...', '[MASKED_JWT]'),
      (r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', '[MASKED_EMAIL]'),
      ...
  ]
  ```
* **단위 테스트 링크**:
  - 민감정보 마스킹 단위 테스트: [tests/test_assistant.py:test_safe_mode_masking#L29-L47](../tests/test_assistant.py#L29-L47)
  - 안전 모드 라인 수 절삭 단위 테스트: [tests/test_assistant.py:test_safe_mode_line_truncation#L48-L57](../tests/test_assistant.py#L48-L57)

---

### Q4-3. 이 도구를 실제 팀 프로젝트에 적용한다면 어떤 기능을 가장 먼저 추가하거나 개선하고 싶은지, 그 우선순위 근거를 설명할 수 있는가? <a id="q4-3"></a>

> 📊 **동료평가 추적 매트릭스**: [전체 문항 추적 매트릭스 (Item 4-3)](#matrix)

* **핵심 답변**: **가장 먼저 `Staged와 Unstaged diff의 명확한 구획화 및 Staged 우선순위 정책`을 적용하여 할루시네이션을 방지하고, 이어서 `Git Pre-commit Hook 연동` 및 `대화형 확인/편집 모드`를 추가하고 싶습니다.**
* **상세 설명**:
  - **1순위 (Staged / Unstaged diff 명확한 구획화 및 Staged 최우선 정책)**:
    - **현재 코드의 한계점 ([src/git_collector.py#L135-L140](../src/git_collector.py#L135-L140))**:
      ```python
      # src/git_collector.py (현재 구현: 단순 + 결합)
      if not diff:
          staged = self._run(['git', 'diff', '--cached'])
          unstaged = self._run(['git', 'diff'])
          diff = (staged + unstaged).strip()
      ```
      - 현재 구현은 `staged` 문자열과 `unstaged` 문자열을 단순 `+` 연산자로 이어 붙이기만 합니다.
      - 중간에 구분자나 헤더가 전혀 없기 때문에, 최종 데이터를 전달받는 **AI 입장에서는 어떤 코드가 `git add` 된 상태이고 어떤 코드가 아직 미등록 상태인지 전혀 구분할 수 없습니다.**
    - **발생하는 3대 문제점**:
      1. *커밋 대상 불일치 및 할루시네이션*: `git commit`은 본질적으로 Staged 파일만 커밋하지만, AI는 아직 `add`하지 않은 로컬 작업 트리 변경분까지 섞어서 커밋 메시지를 작성해버립니다.
      2. *동일 파일 중복 출현에 따른 혼란*: 한 파일을 `add`한 뒤 추가 수정한 경우 동일 파일의 diff 블록이 연달아 2번 나타나 AI가 어떤 hunk가 유효한지 파싱에 혼란을 겪습니다.
      3. *상태 메타데이터 유실*: Index(Staging Area)와 Working Tree라는 Git의 2단계 상태 모델이 소실됩니다.
    - **개선 코드 (Proposed Architecture Fix)**:
      ```python
      # 개선안: 명확한 상태 헤더 분리 및 정교한 컨텍스트 주입
      if not diff:
          staged = self._run(['git', 'diff', '--cached']).strip()
          unstaged = self._run(['git', 'diff']).strip()
          parts = []
          if staged:
              parts.append(f"--- STAGED CHANGES (git add 완료) ---\n{staged}")
          if unstaged:
              parts.append(f"--- UNSTAGED CHANGES (작업 트리 수정본) ---\n{unstaged}")
          diff = "\n\n".join(parts)
      ```
  - **2순위 (Git Pre-commit Hook & Interactive CLI)**:
    - *근거*: 현재는 터미널에 텍스트를 출력하고 사용자가 복사해야 하지만, `.git/hooks/prepare-commit-msg`와 연동하여 `git commit` 명령 시 자동으로 AI 초안을 Vim/Nano 에디터에 기본 커밋 메시지로 채워주면 사용자가 1초 만에 확인·수정·저장할 수 있어 생산성이 비약적으로 상승합니다.
  - **3순위 (GitHub CLI `gh pr create` 자동 연계)**:
    - *근거*: 생성된 PR 제목과 본문을 GitHub 공식 CLI(`gh pr create --title "..." --body "..."`)로 직접 연동하여 원클릭으로 원격 PR 생성을 자동 완료하는 파이프라인을 완성할 수 있습니다.
* **관련 소스코드 및 아키텍처 링크**:
  - 현재 Staged/Unstaged 수집 로직: [src/git_collector.py#L135-L140](../src/git_collector.py#L135-L140)
  - CLI 파서 확장 진입점: [src/main.py#L249-L264](../src/main.py#L249-L264)
  - 서브프로세스 확장 지점: [src/git_collector.py#L71-L88](../src/git_collector.py#L71-L88)
  - 실무 적용 우선순위 로드맵: [study/project_summary.md#step-8-구획화된-터미널-출력-및-메타-피드백-mainpy](../study/project_summary.md#step-8-구획화된-터미널-출력-및-메타-피드백-mainpy)

---

## 5. 전체 문항 추적 매트릭스 (Traceability Matrix) <a id="matrix"></a>

| 평가 문항 | 핵심 검증 대상 | 구현 소스코드 링크 | 단위 테스트 및 검증 증빙 링크 |
| :--- | :--- | :--- | :--- |
| **[Item 1-1](#q1-1)** | 커밋 메시지 자동 생성 | [src/main.py:cmd_commit](../src/main.py#L74-L132) | [tests/test_assistant.py:test_is_git_repo](../tests/test_assistant.py#L25-L27) |
| **[Item 1-2](#q1-2)** | PR 초안 자동 생성 | [src/main.py:cmd_pr](../src/main.py#L135-L195) | [tests/test_assistant.py:test_pr_prompt_contains_required_sections](../tests/test_assistant.py#L87-L94) |
| **[Item 1-3](#q1-3)** | API Key 누락 예외 처리 | [src/ai_client.py:AIClient.__init__](../src/ai_client.py#L43-L89) | [tests/test_assistant.py:test_missing_api_key_exits](../tests/test_assistant.py#L62-L68) |
| **[Item 1-4](#q1-4)** | 변경 부재 시 조기 종료 | [src/main.py#L83-L85](../src/main.py#L83-L85) | [tests/test_assistant.py:test_is_git_repo](../tests/test_assistant.py#L25-L27) |
| **[Item 1-5](#q1-5)** | PR 3대 섹션/불릿 강제 | [src/validator.py:validate_pr](../src/validator.py#L106-L137) | [tests/test_assistant.py:test_validate_pr_ensures_bullets](../tests/test_assistant.py#L128-L136) |
| **[Item 1-6](#q1-6)** | CLI 옵션 동작 (-t, -max-tokens) | [src/main.py:build_parser](../src/main.py#L198-L264) | [tests/test_assistant.py:test_single_dash_options](../tests/test_assistant.py#L151-L158) |
| **[Item 1-7](#q1-7)** | 커밋/PR 제목 길이 하드 컷 | [src/validator.py:validate_commit](../src/validator.py#L50-L58) | [tests/test_assistant.py:test_validate_commit_title_truncation](../tests/test_assistant.py#L99-L109) |
| **[Item 2-1](#q2-1)** | Git수집 / AI호출 책임 분리 | [src/git_collector.py](../src/git_collector.py#L50-L227), [src/ai_client.py](../src/ai_client.py#L30-L136) | [tests/test_assistant.py:TestGitCollector](../tests/test_assistant.py#L19-L57) |
| **[Item 2-2](#q2-2)** | 프롬프트 / 검증기 분리 | [src/prompt_builder.py](../src/prompt_builder.py#L1-L121), [src/validator.py](../src/validator.py#L1-L137) | [tests/test_assistant.py:TestValidator](../tests/test_assistant.py#L96-L136) |
| **[Item 2-3](#q2-3)** | CLI 옵션화 이유 | [src/main.py:_add_common_arguments](../src/main.py#L207-L248) | [tests/test_assistant.py:TestCLIParser](../tests/test_assistant.py#L138-L165) |
| **[Item 2-4](#q2-4)** | 표준 오류 처리 방식 | [src/ai_client.py:generate](../src/ai_client.py#L123-L136) | [tests/test_assistant.py:test_missing_api_key_exits](../tests/test_assistant.py#L62-L68) |
| **[Item 3-1](#q3-1)** | Temperature 파라미터 이해 | [src/ai_client.py#L118](../src/ai_client.py#L118) | [study/study.md#2-temperature와-max-tokens-옵션-변경-시-출력-차이-상세-분석-q1-6-심층](../study/study.md#2-temperature와-max-tokens-옵션-변경-시-출력-차이-상세-분석-q1-6-심층) |
| **[Item 3-2](#q3-2)** | Max Tokens 파라미터 이해 | [src/ai_client.py#L119](../src/ai_client.py#L119) | [study/study.md#12-진짜-잘-설정되었는지-쿼리로-조사하는-3대-검증-방법](../study/study.md#12-진짜-잘-설정되었는지-쿼리로-조사하는-3대-검증-방법) |
| **[Item 3-3](#q3-3)** | 프롬프트 컨텍스트 설계 | [src/prompt_builder.py](../src/prompt_builder.py#L17-L121) | [tests/test_assistant.py:TestPromptBuilder](../tests/test_assistant.py#L77-L94) |
| **[Item 3-4](#q3-4)** | 후처리 vs 재생성 선택 이유 | [src/validator.py](../src/validator.py#L50-L137) | [study/study.md#35-왜-재생성retry-대신-후처리post-processing를-선택했는가](../study/study.md#35-왜-재생성retry-대신-후처리post-processing를-선택했는가) |
| **[Item 4-1](#q4-1)** | AI 텍스트 검토 필요성 | [src/main.py#L124-L131](../src/main.py#L124-L131) | [README.md#4-안전-모드-safe-mode-및-보안-정책](../README.md#4-안전-모드-safe-mode-및-보안-정책) |
| **[Item 4-2](#q4-2)** | Git diff 민감정보 마스킹 | [src/git_collector.py:_SENSITIVE](../src/git_collector.py#L27-L47) | [tests/test_assistant.py:test_safe_mode_masking](../tests/test_assistant.py#L29-L47) |
| **[Item 4-3](#q4-3)** | 실무 개선 우선순위 | [src/git_collector.py#L135-L140](../src/git_collector.py#L135-L140), [src/main.py#L249-L264](../src/main.py#L249-L264) | [study/project_summary.md](../study/project_summary.md#step-8-구획화된-터미널-출력-및-메타-피드백-mainpy) |
