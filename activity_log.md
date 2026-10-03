# Antigravity Activity Log & Project Memory

## 1. Project Overview
- **Project:** B3-2 AI Git Assistant (내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기)
- **Root Directory:** `/Users/mpeg46551/b3_2`
- **Python Virtualenv:** `/Users/mpeg46551/b3_2/.venv` (Python 3.12)
- **Evaluation Plan:** `/Users/mpeg46551/b3_2/docs/EVALUATION_PLAN.md`
- **Peer Evaluation Questions:** `/Users/mpeg46551/b3_2/docs/EVALUATION.md`
- **Conventions:** `/Users/mpeg46551/b3_2/docs/CONVENTIONS.md`

## 2. Directory Structure & Key Files
- `main.py`: Root CLI entry point (`python main.py commit`, `python main.py pr`)
- `src/`:
  - `main.py`: CLI command dispatcher and argument parser (`-model`, `-temperature`, `-max-tokens`, `-safe-mode`, etc.)
  - `ai_client.py`: AI API client with `AI_API_KEY` prioritization, base URL fallback, and user-friendly error messages.
  - `git_collector.py`: Git status/diff collector with `is_git_repo` check and safe mode regex masking/truncation.
  - `prompt_builder.py`: Prompt generator for commit messages and PR drafts (Why, What, How to Test).
  - `validator.py`: Post-processor enforcing title length (50/72 chars, 80 chars) and ensuring all PR sections with bullet points.
  - `convention.py`: Loads `.ai-gitgen.yml` configuration.
  - `README.md`: User guide documentation.
- `tests/`:
  - `test_assistant.py`: Comprehensive test suite for `GitCollector`, `AIClient`, `PromptBuilder`, `Validator`, and CLI option parsing.
- `docs/`:
  - `EVALUATION_PLAN.md`: 6-step evaluation plan for peer review.
  - `EVALUATION.md`: Original peer evaluation questions.
  - `CONVENTIONS.md`: Commit message standards (Why, What, Impact, Verification).

## 3. Execution History & Status
- **2026-10-03 (KST)**:
  - Fixed terminal path escaping issue for `doc/B3_2미션 - AI 도구 학습.pdf`.
  - Diagnosed `ref_site/` (Mini Git reference) and `src/` (AI Assistant codebase).
  - Identified & resolved critical bugs:
    - Added `AI_API_KEY` support and exact error message formatting in `src/ai_client.py`.
    - Removed `HEAD~1` fallback in `src/git_collector.py` so clean git status correctly triggers "변경 사항이 없습니다".
    - Added single-dash flag support (`-temperature`, `-max-tokens`, etc.) in `src/main.py`.
    - Created root `main.py` entry point.
    - Enhanced `src/validator.py` with bullet enforcement and section completion.
  - Authored comprehensive evaluation plan: `docs/EVALUATION_PLAN.md`.
  - Created automated test suite: `tests/test_assistant.py` (13 tests all passing).
- **2026-10-03 16:58 (KST)**:
  - Configured `.env` with Codyssey OpenAI proxy endpoint (`https://copa.codyssey.kr/v1`).
  - Integrated `gpt-5.4-mini` as the primary default model (0.5 deduction weight, fast response speed, full temperature support).
  - Enhanced `src/ai_client.py` with automatic base URL routing for `sk-cody-` keys.
  - Verified live execution of `python main.py commit` and `python main.py pr` using real Codyssey API Gateway.
- **2026-10-03 17:00 (KST)**:
  - Synchronized and pushed all local commits to GitHub remote repository (`https://github.com/nttkor/b3_2`).
  - Working directory clean, all tests passing.
- **2026-10-03 17:05 (KST)**:
  - Enforced detailed commit message policy in Rule 2 across `GEMINI.md`, `AGENTS.md`, and `doc/CONVENTIONS.md`.
  - Defined explicit structure: Why, What (file/logic breakdown), Impact, Verification.
- **2026-10-03 17:09 (KST)**:
  - Authored comprehensive root `README.md` meeting all 3 final deliverables and section requirements from the mission PDF.
  - Linked all documentation (`EVALUATION_PLAN.md`, `CONVENTIONS.md`) and verified 100% mission readiness.
- **2026-10-03 17:12 (KST)**:
  - Unified `doc` and `docs` into a single `docs/` directory per user request (`git mv doc docs`).
  - Removed legacy symlink and updated all markdown file references.
- **2026-10-03 17:25 (KST)**:
  - User updated `.env` with personal Codyssey API key (`sk-cody-live-...`).
  - Formatted `.env` into clean standard environment variable syntax (`AI_API_KEY`, `AI_API_BASE_URL`, `AI_MODEL`) to eliminate `python-dotenv` parsing warnings.
  - Verified live execution of `python main.py commit` with `gpt-5.4-mini` (1.8s, full success).
  - Deleted obsolete `ref_site/` directory (commit `443ee22`) and added `chat.md` (commit `e9249b8`).
  - Synchronized and pushed all commits to remote GitHub repository (`https://github.com/nttkor/b3_2`). Working directory clean.
- **2026-10-03 17:30 (KST)**:
  - Added transparent `.venv` auto-detection and re-execution (`os.execv`) to `main.py` and `src/main.py`.
  - Resolves `ModuleNotFoundError: No module named 'dotenv'` when invoked from terminal without manual `source .venv/bin/activate`.
  - Added user-friendly installation error guidance if dependencies are missing.
- **2026-10-03 17:37 (KST)**:
  - Diagnosed root cause of `ModuleNotFoundError: No module named 'dotenv'` even after `source .venv/bin/activate`:
    - macOS `/etc/zprofile` contained Ansible-managed `alias python='$PYTHON_HOME/bin/python3.12'` pointing to global Homebrew Python (`/usr/local/opt/python@3.12`).
    - Because `.venv/bin/python` is a symlink to that same Homebrew binary, `Path(sys.executable).resolve() != _venv_python.resolve()` evaluated to `False`.
  - Refactored auto-venv detection to compare `Path(sys.prefix).resolve() != _venv_dir.resolve()` across `main.py` and `src/main.py`.
  - Added automatic unaliasing (`unalias python python3 pip pip3`) in `.venv/bin/activate` for interactive shells.
  - Verified live execution with global Python binary (`/usr/local/opt/python@3.12/bin/python3.12 main.py commit`) successfully redirecting to `.venv` and completing AI commit generation.
  - All 13 unit tests passed in 0.060s.
- **2026-10-03 17:43 (KST)**:
  - User successfully verified both `python main.py commit` and `python main.py pr` in terminal.
  - Commit message format validated (`docs: chat.md에 가상환경 오류 해결 기록 추가` + bullets).
  - PR draft structure validated (Title + `## Why`, `## What`, `## How to Test` with bullet points).
  - Both CLI commands operating with `gpt-5.4-mini` via Codyssey Gateway with ~1.5s response time.
- **2026-10-03 17:47 (KST)**:
  - Resolved CLI argument parsing issue when options are placed after subcommands (`python main.py commit -temperature 0.2 -safe-mode`).
  - Refactored `src/main.py:build_parser` to register common options on both root parser and subparsers (`commit`, `pr`) with `argparse.SUPPRESS` defaults on subparsers to prevent accidental overwrites.
  - Added unit test `test_options_after_subcommand` in `tests/test_assistant.py` (14/14 tests passing).
  - Verified live execution of `python main.py commit -temperature 0.2 -safe-mode`.
- **2026-10-03 17:51 (KST)**:
  - User successfully tested and confirmed live execution of `python main.py commit -temperature 0.2 -safe-mode`.
  - Confirmed safe mode activation message: `[INFO] 안전 모드: 파일 최대 10개 / 줄 최대 200줄`.
  - Accurately generated conventional commit message for `chat.md` updates.
  - Full evaluation scope (Items 1~4) verified and functional.
- **2026-10-03 17:55 (KST)**:
  - Authored comprehensive answers for all 5 assignment goals in `docs/b6-2-mission.md` (Section 3).
  - Detailed REST API lifecycle, hyperparameter behaviors, Git CLI integration flow, prompt engineering & structure constraints, and post-processing validation rationale.
- **2026-10-03 18:00 (KST)**:
  - Authored detailed implementation answers for Section 4 (기능 요구 사항 4.1 ~ 4.6) in `docs/b6-2-mission.md`.
  - Applied GitHub-compatible relative paths (`../src/git_collector.py`, `../src/ai_client.py`, `../src/validator.py`, `../README.md`, etc.) for seamless navigation on GitHub web.
  - Linked verification commands, live output examples, and peer review item mappings across all subsections.
- **2026-10-03 18:02 (KST)**:
  - Removed obsolete legacy `docs/README.md` (Mini Git project documentation) to eliminate confusion.
  - Confirmed repository root `README.md` serves as the sole, authoritative project documentation.
- **2026-10-03 18:05 (KST)**:
  - Authored comprehensive architecture and folder index guide in `study/folder_index.md`.
  - Structured into directory tree view, file responsibility table with GitHub-compatible relative links, Mermaid system architecture flowchart, Mermaid class diagram, commit/PR sequence diagrams, and safe-mode security flowcharts.
- **2026-10-03 18:09 (KST)**:
  - Authored comprehensive execution lifecycle deep-dive document in `study/project_summary.md`.
  - Detailed the 8-step pipeline from process bootstrap (sys.prefix/os.execv), CLI parsing, Git inspection & clean repo early exit, safe-mode sanitization, prompt engineering, AI API 1-shot invocation, deterministic post-validation, to terminal rendering.
  - Included comparison matrix and edge case handling strategies.
- **2026-10-03 18:12 (KST)**:
  - Authored peer evaluation preparation guide in `docs/EVALUATION_QA.md` based strictly on `docs/EVALUATION.md`.
  - Covered all 18 evaluation questions across Items 1 to 4 with summary answers, deep explanations, relevant source code snippets, GitHub-compatible relative path links, verification commands, live terminal outputs, and an evaluation traceability matrix.
- **2026-10-03 18:43 (KST)**:
  - Investigated API response payloads and wire-level verification for `-temperature` and `-max-tokens`.
  - Proved that standard OpenAI REST API response bodies do not echo back request hyperparameters (`temperature`, `max_tokens`).
  - Demonstrated 3 empirical verification methods:
    1. Wire-level request body inspection via `with_raw_response` (`{"max_tokens":1024,"temperature":0.1}`).
    2. Truncation and finish reason verification via `finish_reason == 'length'` and `completion_tokens`.
    3. Output variance analysis across low (0.0/0.1) vs high (1.5) temperatures.
- **2026-10-03 19:58 (KST)**:
  - Refactored `docs/EVALUATION_QA.md` and `study/study.md` per user request:
    - Moved lengthy technical analyses, comparison tables, and architectural Mermaid diagrams from Q1-6 and Q1-7 into `study/study.md`.
    - Structured `study/study.md` into 3 core sections: API wire-level verification, parameter comparison deep-dive, and hybrid validation architecture.
    - Added GitHub-compatible relative markdown links between `docs/EVALUATION_QA.md` and `study/study.md`.
  - Verified 14/14 unit tests passing.
- **2026-10-03 20:50 (KST)**:
  - Added bidirectional traceability matrix links in `docs/EVALUATION_QA.md`:
    - Inserted `> 📊 **동료평가 추적 매트릭스**: [## 5. 전체 문항 추적 매트릭스 (Item X-Y)](#5-전체-문항-추적-매트릭스-traceability-matrix)` under all 18 question headings.
    - Added explicit anchor tags `<a id="qX-Y"></a>` for guaranteed GitHub markdown rendering.
    - Linked table items (`[**Item X-Y**](#qX-Y)`) in Section 5 back to their corresponding question headings.
  - Verified 14/14 unit tests passing.
- **2026-10-03 21:05 (KST)**:
  - Fully populated and enriched code links across all 18 questions in `docs/EVALUATION_QA.md`:
    - Added explicit `* **관련 소스코드**:` sections and code snippets with exact line links for Q2-1, Q2-2, Q2-3, Q2-4, Q3-1, Q3-2, Q3-3, Q3-4, Q4-1, Q4-2, Q4-3.
    - Linked all unit test methods (`tests/test_assistant.py#L...`) and deep study notes across the document.
    - Completed 100% clickable links in the Section 5 Traceability Matrix table (source code lines + test methods/deep links).
  - Verified 14/14 unit tests passing.




