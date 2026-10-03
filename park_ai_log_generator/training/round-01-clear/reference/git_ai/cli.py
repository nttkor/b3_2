from __future__ import annotations

import argparse
import sys

from .ai_client import AIClient, AIConfig
from .errors import GitAIError
from .git_tools import collect_changes
from .prompts import commit_prompt, pr_prompt
from .validators import validate_commit_output, validate_pr_output


DEFAULT_MODEL = "runtime-model"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 700


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-ai",
        description="Git status/diff를 AI API에 전달해 Commit/PR 초안을 생성합니다.",
    )
    parser.add_argument("command", choices=("commit", "pr"), help="생성할 문서 종류")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Runtime AI 모델 이름")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help="생성 다양성 파라미터")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="최대 생성 token 수")
    return parser


def validate_cli_options(args: argparse.Namespace) -> None:
    if args.temperature < 0:
        raise GitAIError("--temperature는 0 이상이어야 합니다.")
    if args.max_tokens <= 0:
        raise GitAIError("--max-tokens는 1 이상이어야 합니다.")
    if not str(args.model).strip():
        raise GitAIError("--model 값이 비어 있습니다.")


def run(argv: list[str] | None = None, client: AIClient | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        validate_cli_options(args)
        changes = collect_changes()
        if not changes.has_changes:
            print("변경 사항이 없습니다.")
            return 0

        config = AIConfig.from_runtime(
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        api = client or AIClient()

        if args.command == "commit":
            raw = api.generate(config, commit_prompt(changes))
            output = validate_commit_output(raw)
        else:
            raw = api.generate(config, pr_prompt(changes))
            output = validate_pr_output(raw)

        print(output)
        return 0

    except GitAIError as exc:
        print("[ERROR] {}".format(exc), file=sys.stderr)
        return 2


def main() -> None:
    raise SystemExit(run())
