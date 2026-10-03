# Antigravity Activity Log & Project Memory

## 1. Project Overview
- **Project:** B3-2 AI Git Assistant (내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기)
- **Root Directory:** `/Users/mpeg46551/b3_2`
- **Python Virtualenv:** `/Users/mpeg46551/b3_2/.venv` (Python 3.12)
- **Evaluation Plan:** `/Users/mpeg46551/b3_2/doc/EVALUATION_PLAN.md`
- **Peer Evaluation Questions:** `/Users/mpeg46551/b3_2/doc/EVALUATION.md`
- **Conventions:** `/Users/mpeg46551/b3_2/doc/CONVENTIONS.md` (`docs/CONVENTIONS.md`)

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
- `ref_site/`:
  - Contains Round 01 Mini Git codebase (`mini_git/`) and requirements. Not the AI assistant codebase, but can serve as a reference or test target.
- `tests/`:
  - `test_assistant.py`: Comprehensive test suite for `GitCollector`, `AIClient`, `PromptBuilder`, `Validator`, and CLI option parsing.

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
  - Authored comprehensive evaluation plan: `doc/EVALUATION_PLAN.md`.
  - Created automated test suite: `tests/test_assistant.py` (13 tests all passing).
- **2026-10-03 16:58 (KST)**:
  - Configured `.env` with Codyssey OpenAI proxy endpoint (`https://copa.codyssey.kr/v1`).
  - Integrated `gpt-5.4-mini` as the primary default model (0.5 deduction weight, fast response speed, full temperature support).
  - Enhanced `src/ai_client.py` with automatic base URL routing for `sk-cody-` keys.
  - Verified live execution of `python main.py commit` and `python main.py pr` using real Codyssey API Gateway.
