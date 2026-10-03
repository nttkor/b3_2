"""AI 기반 Git 커밋/PR 자동 생성기 - CLI 디스패처 및 실행 제어 모듈 (src/main.py).

이 모듈은 AI Git Assistant의 핵심 실행 진입점이자 사용자 명령어(CLI) 제어 모듈입니다.
터미널에서 전달된 인자 파싱(`argparse`), 가상환경 자동 재실행(Bootstrap), 환경변수 로드(`.env`),
컨벤션 설정 주입(`.ai-gitgen.yml`), Git 상태 및 diff 수집 파이프라인 호출,
AI API 통신 및 사후 검증 결과를 구획화된 터미널 뷰로 렌더링하는 전 과정을 조율합니다.

주요 특징:
    1. 가상환경 자동 부트스트랩 (Auto-venv Switching):
       - 사용자가 `source .venv/bin/activate`를 실행하지 않은 상태에서 일반 파이썬으로
         스크립트를 호출하더라도, `.venv/bin/python`을 감지하여 `os.execv`로 즉시 교체 재실행합니다.
    2. 단일 대시 및 이중 대시 CLI 옵션 전면 지원:
       - 미션 요구사항 및 사용자의 입력 습관을 고려하여 `--model`뿐만 아니라 `-model`, `-temperature`,
         `-max-tokens`, `-safe-mode` 등의 단일 대시 플래그를 서브커맨드 앞뒤 어디서든 파싱할 수 있도록 지원합니다.
    3. 명확한 터미널 구획 출력 (Delimited Output):
       - 생성된 커밋 메시지와 PR 초안(제목 및 3대 섹션 본문)을 명확한 구분선(`--- Commit Message ---`,
         `--- PR Title ---`, `--- PR Body ---`)으로 분리하여 개발자가 눈으로 확인 후 확정할 수 있도록 안내합니다.
"""

import argparse
import os
import sys
from pathlib import Path

# 가상환경(.venv)이 존재할 경우, source 활성화 없이도 .venv 파이썬으로 자동 재실행
_venv_dir = Path(__file__).resolve().parent.parent / '.venv'
_venv_python = _venv_dir / 'bin' / 'python'
if _venv_python.exists() and Path(sys.prefix).resolve() != _venv_dir.resolve():
    # 현재 프로세스를 가상환경 인터프리터로 덮어씌워 재실행
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

# 필수 패키지(python-dotenv 등) 임포트 검증 및 부재 시 가이드 출력
try:
    from dotenv import load_dotenv
except ModuleNotFoundError as e:
    print(f"[ERROR] 필수 패키지가 설치되지 않았습니다 ({e}).")
    print("## 해결 방법: source .venv/bin/activate  또는  pip install -r src/requirements.txt")
    sys.exit(1)

# .env 환경변수 로드 (현재 작업 디렉토리 우선 탐색 후 소스 디렉토리 탐색)
load_dotenv(Path.cwd() / '.env')
load_dotenv(Path(__file__).parent / '.env')

# 프로젝트 내부 모듈 임포트
import convention as conv
from ai_client import AIClient
from git_collector import GitCollector
from prompt_builder import build_commit_prompt, build_pr_prompt
from validator import validate_commit, validate_pr

# CLI 기본 하이퍼파라미터 상수 정의
DEFAULT_MODEL = os.environ.get('AI_MODEL', 'gpt-5.4-mini')  # 기본 AI 모델 (Codyssey 0.5 가중치 모델)
DEFAULT_TEMPERATURE = 0.3                                   # 기본 생성 무작위도 (규격 준수와 자연스러움의 균형)
DEFAULT_MAX_TOKENS = 1024                                   # 기본 최대 출력 토큰 한도


def _make_client(args: argparse.Namespace) -> AIClient:
    """파싱된 CLI 인자(args)를 바탕으로 AIClient 인스턴스를 생성한다.

    Args:
        args (argparse.Namespace): 사용자 입력 및 기본값이 반영된 CLI 인자 객체
            (`model`, `temperature`, `max_tokens` 속성 포함).

    Returns:
        AIClient: 초기화된 AI 네트워크 통신 클라이언트 객체.
    """
    return AIClient(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )


def cmd_commit(args: argparse.Namespace, convention: dict) -> None:
    """`commit` 서브커맨드를 실행하여 작업 트리의 커밋 메시지를 자동 생성하고 검증한다.

    Git 저장소 여부를 확인하고, 변경 사항이 없을 경우 조기 종료하며,
    Staged/Unstaged diff를 수집하여 AI 프롬프트를 구성한 뒤 커밋 메시지를 생성합니다.
    생성된 메시지는 사후 검증기를 통해 제목 길이(72자) 등이 보정되어 터미널에 출력됩니다.

    Args:
        args (argparse.Namespace): 커밋 명령에 필요한 CLI 인자 객체
            (`safe_mode`, `safe_max_files`, `safe_max_lines`, `model` 등).
        convention (dict): 로드된 프로젝트 컨벤션 딕셔너리.

    Raises:
        SystemExit: Git 저장소가 아닌 경우(`sys.exit(1)`), 또는 변경 사항이 없는 경우(`sys.exit(0)`).
    """
    collector = GitCollector()

    # 1. 유효한 Git 저장소인지 사전 검증 (동료평가 항목 1-1 / 2-1)
    if not collector.is_git_repo():
        print('[ERROR] Git 저장소가 아닙니다. Git이 초기화된 디렉토리에서 실행하세요.')
        sys.exit(1)

    # 2. 변경된 파일이 존재하는지 검증 (변경 사항 없을 시 조기 종료 - 동료평가 항목 1-4)
    if not collector.count_changed_files():
        print('[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.')
        sys.exit(0)

    # 3. 안전 모드 임계치 설정 (CLI 지정값 우선, 부재 시 컨벤션 설정, 최종 기본값 10/200)
    max_files = args.safe_max_files or convention.get('safe_max_files', 10)
    max_lines = args.safe_max_lines or convention.get('safe_max_lines', 200)

    # 4. Git 작업 상태 및 코드 diff 수집 (Staged + Unstaged 통합 수집)
    status = collector.get_status()
    diff = collector.get_diff(safe_mode=args.safe_mode,
                              safe_max_files=max_files, safe_max_lines=max_lines)
    file_count = collector.count_changed_files()
    diff_lines = len(diff.splitlines())

    # 5. 수집 현황 터미널 안내 출력
    print(f'[INFO] Git status 수집 완료: {file_count}개 파일 변경 감지')
    print(f'[INFO] Git diff 수집 완료: {diff_lines}줄')
    if args.safe_mode:
        print(f'[INFO] 안전 모드: 파일 최대 {max_files}개 / 줄 최대 {max_lines}줄')
    print('[INFO] AI API 요청 중...')

    # 6. AI 프롬프트 조립 및 API 단일 호출
    client = _make_client(args)
    prompt = build_commit_prompt(status, diff, convention)
    result = client.generate(prompt)

    # 7. 사후 검증기를 통한 제목 길이 절삭 및 불릿 형식 확정 보정
    commit_msg = validate_commit(result)

    # 8. 명확한 구분선과 함께 최종 커밋 메시지 초안 출력
    print('[DONE] 커밋 메시지 생성 완료\n')
    print('--- Commit Message ---')
    print(commit_msg)
    print('----------------------')
    print(f'\n[INFO] 모델: {args.model}  |  호출 횟수: 1')


def cmd_pr(args: argparse.Namespace, convention: dict) -> None:
    """`pr` 서브커맨드를 실행하여 Pull Request 제목과 3대 섹션 본문 초안을 자동 생성한다.

    현재 브랜치와 기준 브랜치(main/master) 간의 diff를 수집하고,
    AI API를 통해 제목 및 Why/What/How to Test 섹션 초안을 작성한 뒤,
    사후 검증기를 통해 길이와 불릿 구조를 보정하여 터미널에 구획화하여 출력합니다.

    Args:
        args (argparse.Namespace): PR 명령에 필요한 CLI 인자 객체
            (`safe_mode`, `safe_max_files`, `safe_max_lines`, `model` 등).
        convention (dict): 로드된 프로젝트 컨벤션 딕셔너리.

    Raises:
        SystemExit: Git 저장소가 아닌 경우(`sys.exit(1)`), 또는 변경 사항이 없는 경우(`sys.exit(0)`).
    """
    collector = GitCollector()

    # 1. 유효한 Git 저장소인지 사전 검증
    if not collector.is_git_repo():
        print('[ERROR] Git 저장소가 아닙니다. Git이 초기화된 디렉토리에서 실행하세요.')
        sys.exit(1)

    # 2. 안전 모드 임계치 설정 (CLI 지정값 우선, 부재 시 컨벤션 설정)
    max_files = args.safe_max_files or convention.get('safe_max_files', 10)
    max_lines = args.safe_max_lines or convention.get('safe_max_lines', 200)

    # 3. 브랜치명 및 기준 브랜치 대비 diff 수집
    branch = collector.get_current_branch()
    diff = collector.get_diff(safe_mode=args.safe_mode, for_pr=True,
                              safe_max_files=max_files, safe_max_lines=max_lines)
    # 기준 브랜치 대비 변경 사항이 없을 경우 조기 종료
    if not diff.strip():
        print('[INFO] 변경 사항이 없습니다. PR 초안을 생성하지 않고 종료합니다.')
        sys.exit(0)

    # 4. 수집 현황 터미널 안내 출력
    status = collector.get_status()
    diff_lines = len(diff.splitlines())

    print(f'[INFO] 현재 브랜치: {branch}')
    print(f'[INFO] Git diff 수집 완료: {diff_lines}줄')
    if args.safe_mode:
        print(f'[INFO] 안전 모드: 파일 최대 {max_files}개 / 줄 최대 {max_lines}줄')
    print('[INFO] AI API 요청 중...')

    # 5. AI 프롬프트 조립 및 API 단일 호출
    client = _make_client(args)
    prompt = build_pr_prompt(status, diff, branch, convention)
    result = client.generate(prompt)

    # 6. 사후 검증기를 통한 PR 제목(80자) 절삭, 3대 섹션 누락 복구 및 불릿 보정
    title, body = validate_pr(result)

    # 7. 구획화된 터미널 뷰 렌더링
    print('[DONE] PR 초안 생성 완료\n')
    print('--- PR Title ---')
    print(title)
    print('--- PR Body ---')
    print(body)
    print('---------------')
    print(f'\n[INFO] 모델: {args.model}  |  호출 횟수: 1')


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서(ArgumentParser)를 구성하고 공통 옵션 및 서브커맨드를 등록한다.

    메인 파서와 서브파서(`commit`, `pr`)에 공통 옵션을 등록하며,
    서브커맨드 위치에 구애받지 않고 단일 대시(-model, -temperature 등) 및
    이중 대시(--model, --temperature 등)가 모두 원활하게 파싱되도록 상속 구조를 설계합니다.

    Returns:
        argparse.ArgumentParser: 구성 완료된 명령줄 인수 파서 객체.
    """
    def _add_common_arguments(p: argparse.ArgumentParser, is_sub: bool = False) -> None:
        """메인 파서 및 서브파서에 공통 인자를 등록하는 헬퍼 함수.

        Args:
            p (argparse.ArgumentParser): 인자를 추가할 파서 또는 서브파서 객체.
            is_sub (bool, optional): 서브파서 여부. 서브파서일 경우 메인 파서의 기본값을
                덮어쓰지 않도록 기본값을 `argparse.SUPPRESS`로 처리합니다. Defaults to False.
        """
        d_model = argparse.SUPPRESS if is_sub else DEFAULT_MODEL
        d_temp = argparse.SUPPRESS if is_sub else DEFAULT_TEMPERATURE
        d_tokens = argparse.SUPPRESS if is_sub else DEFAULT_MAX_TOKENS
        d_safe = argparse.SUPPRESS if is_sub else False
        d_conv = argparse.SUPPRESS if is_sub else None

        # 모델 식별자 옵션
        p.add_argument('--model', '-model', '-m', default=d_model,
                            help=f'AI 모델 ID (기본값: {DEFAULT_MODEL})')
        # 생성 온도(무작위도) 옵션
        p.add_argument('--temperature', '-temperature', '-t', type=float, default=d_temp,
                            help=f'생성 온도 0.0~1.0 (기본값: {DEFAULT_TEMPERATURE})')
        # 최대 출력 토큰 수 옵션
        p.add_argument('--max-tokens', '-max-tokens', type=int, default=d_tokens,
                            dest='max_tokens',
                            help=f'최대 출력 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})')
        # 안전 모드 플래그 옵션
        p.add_argument('--safe-mode', '-safe-mode', '-s', action='store_true', default=d_safe,
                            help='민감 정보 마스킹 + diff 크기 제한')
        # 안전 모드 파일 수 한도 옵션
        p.add_argument('--safe-max-files', '-safe-max-files', type=int,
                            default=argparse.SUPPRESS if is_sub else None,
                            dest='safe_max_files',
                            help='안전 모드 파일 수 제한 (기본값: 컨벤션 설정 또는 10)')
        # 안전 모드 라인 수 한도 옵션
        p.add_argument('--safe-max-lines', '-safe-max-lines', type=int,
                            default=argparse.SUPPRESS if is_sub else None,
                            dest='safe_max_lines',
                            help='안전 모드 줄 수 제한 (기본값: 컨벤션 설정 또는 200)')
        # 컨벤션 파일 경로 지정 옵션
        p.add_argument('--convention', '-convention', '-c', default=d_conv, metavar='FILE',
                            help='컨벤션 설정 파일 경로 (기본값: .ai-gitgen.yml)')

    # 최상위 파서 초기화
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='AI 기반 Git 커밋/PR 자동 생성기 (OpenRouter / Codyssey Gateway)',
    )
    _add_common_arguments(parser, is_sub=False)

    # 서브커맨드(`commit`, `pr`) 파서 등록
    sub = parser.add_subparsers(dest='command', metavar='command')
    p_commit = sub.add_parser('commit', help='커밋 메시지 자동 생성')
    _add_common_arguments(p_commit, is_sub=True)

    p_pr = sub.add_parser('pr', help='PR 제목/본문 초안 자동 생성')
    _add_common_arguments(p_pr, is_sub=True)

    return parser


def main() -> None:
    """CLI 프로그램 엔트리포인트 함수.

    명령줄 인자를 파싱하고, 컨벤션 설정을 로드한 뒤, 지정된 서브커맨드(`commit` 또는 `pr`)에
    맞춰 적절한 실행 핸들러를 호출합니다. 인자가 주어지지 않은 경우 도움말을 출력합니다.
    """
    parser = build_parser()
    args = parser.parse_args()

    # 컨벤션 파일 로드 (.ai-gitgen.yml 또는 사용자 지정 파일)
    convention = conv.load(args.convention)

    # 서브커맨드 분기 실행
    if args.command == 'commit':
        cmd_commit(args, convention)
    elif args.command == 'pr':
        cmd_pr(args, convention)
    else:
        # 서브커맨드가 누락된 경우 전체 도움말 출력
        parser.print_help()


if __name__ == '__main__':
    main()
