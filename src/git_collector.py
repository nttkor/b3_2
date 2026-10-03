"""Git 메타데이터 수집 및 안전 모드(Safe-mode) 필터링 모듈 (src/git_collector.py).

이 모듈은 로컬 Git 저장소의 작업 상태(`git status`), 코드 변경 내역(`git diff`),
현재 작업 브랜치 정보를 서브프로세스를 통해 안정적으로 수집하고,
외부 AI 게이트웨이로 민감한 정보가 전송되지 않도록 필터링하는 데이터 수집 계층을 담당합니다.

주요 특징:
    1. 단일 책임 원칙(Single Responsibility Principle):
       - 네트워크나 AI 통신과 완전히 분리되어, 오직 로컬 Git 저장소의 상태를 질의하고
         결과 문자열을 정제하는 역할에만 집중합니다.
    2. 9종 정규식 기반 안전 모드(Safe-mode) 민감정보 마스킹:
       - API Key, AWS 자격증명, JWT 토큰, PEM 개인키, 비밀번호, 이메일, 신용카드 번호 등
         다양한 형태의 비밀정보를 정규식으로 실시간 감지하여 `[MASKED_*]`로 치환합니다.
    3. 전송량 제한 및 데이터 절삭:
       - 설정된 임계치(기본값: 파일 최대 10개, diff 최대 200줄)를 초과하는 대규모 diff를
         자동으로 생략/절삭하여 토큰 비용 폭증과 광범위한 코드 유출을 방지합니다.
"""

import re
import subprocess

# 안전 모드 기본 임계치 상수 (CLI 인자 또는 컨벤션 설정을 통해 오버라이드 가능)
DEFAULT_MAX_FILES = 10      # 기본 최대 수집 파일 수
DEFAULT_MAX_LINES = 200     # 기본 최대 수집 라인 수

# 안전 모드에서 감지 및 마스킹할 9종 민감 정보 정규표현식 매핑 테이블
_SENSITIVE: list[tuple[str, str]] = [
    # 1. OpenRouter / OpenAI 계열 API 키 패턴 (sk-or-, sk-...)
    (r'sk-or-[A-Za-z0-9\-_]{20,}', '[MASKED_OR_KEY]'),
    (r'sk-[A-Za-z0-9\-_]{20,}', '[MASKED_API_KEY]'),
    # 2. Anthropic API 키 패턴 (sk-ant-...)
    (r'sk-ant-[A-Za-z0-9\-_]{20,}', '[MASKED_ANT_KEY]'),
    # 3. AWS Access Key ID 패턴 (AKIA로 시작하는 20자리 식별자)
    (r'AKIA[0-9A-Z]{16}', '[MASKED_AWS_KEY]'),
    # 4. JSON Web Token (JWT) 패턴 (헤더.페이로드.서명 구조)
    (r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*', '[MASKED_JWT]'),
    # 5. PEM 형식의 개인키 블록 (RSA, EC, PRIVATE KEY 등)
    (r'-----BEGIN [A-Z ]+ KEY-----[\s\S]+?-----END [A-Z ]+ KEY-----',
     '[MASKED_PEM_KEY]'),
    # 6. 일반적인 비밀번호 및 토큰 할당문 패턴 (대소문자 무관 키워드 탐색)
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password|passwd)\s*[=:]\s*[\'"]?[A-Za-z0-9\-_/+]{8,}[\'"]?',
     r'\1=[MASKED]'),
    # 7. 개인 식별 이메일 주소 패턴
    (r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', '[MASKED_EMAIL]'),
    # 8. 신용카드 번호 패턴 (16자리 숫자 및 하이픈/공백 구분)
    (r'\b[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b', '[MASKED_CC]'),
]


class GitCollector:
    """Git 명령어 실행을 통해 status, diff, 브랜치 정보를 수집하고 민감정보를 필터링하는 수집기 클래스."""

    def is_git_repo(self) -> bool:
        """현재 작업 디렉토리가 유효한 Git 저장소(또는 워크트리) 내부인지 확인한다.

        `git rev-parse --is-inside-work-tree` 명령어를 실행하여 반환 코드가 0인지 검사합니다.

        Returns:
            bool: Git 저장소 내부이면 True, 아니면 False.

        Raises:
            None: Git 미설치 또는 서브프로세스 실패 시에도 크래시 없이 False를 반환합니다.
        """
        try:
            r = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],
                               capture_output=True, text=True)
            return r.returncode == 0
        except Exception:
            return False

    def _run(self, cmd: list[str]) -> str:
        """지정된 Git 명령어를 서브프로세스로 실행하고 표준 출력을 UTF-8 문자열로 반환한다.

        Args:
            cmd (list[str]): 실행할 명령어와 인자 리스트 (예: `['git', 'status']`).

        Returns:
            str: 명령어 실행 결과로 반환된 표준 출력(stdout) 문자열 (오류 발생 시 빈 문자열).

        Raises:
            None: 디코딩 오류 발생 시 errors='replace'로 처리하여 예외를 방지합니다.
        """
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding='utf-8', errors='replace')
            return r.stdout
        except Exception:
            return ''

    def get_status(self) -> str:
        """현재 작업 트리의 상세 Git 상태(`git status`) 전문을 반환한다.

        Returns:
            str: `git status` 실행 결과 문자열.
        """
        return self._run(['git', 'status'])

    def count_changed_files(self) -> int:
        """작업 트리에서 변경(수정, 추가, 삭제, 추적되지 않음 등)된 파일의 총 개수를 계산한다.

        `git status --porcelain` 명령의 출력 줄 수를 카운트하여 신속하게 파일 수를 산출합니다.

        Returns:
            int: 변경된 파일의 개수 (0이면 작업 트리가 깨끗한 상태).
        """
        out = self._run(['git', 'status', '--porcelain'])
        return len([l for l in out.splitlines() if l.strip()])

    def get_diff(self, safe_mode: bool = False, for_pr: bool = False,
                 safe_max_files: int = DEFAULT_MAX_FILES,
                 safe_max_lines: int = DEFAULT_MAX_LINES) -> str:
        """현재 작업 트리의 코드 변경 diff를 수집하고, 옵션에 따라 안전 필터링을 적용한다.

        커밋 메시지 생성 시에는 Staged 및 Unstaged 변경분을 통합 수집하며,
        PR 생성 시(`for_pr=True`)에는 기준 브랜치(main/master)와의 병합 기준점(merge-base)
        대비 전체 변경 내역을 수집합니다.

        Args:
            safe_mode (bool, optional): 민감정보 마스킹 및 전송량 제한 활성화 여부. Defaults to False.
            for_pr (bool, optional): PR용 브랜치 diff 수집 모드 활성화 여부. Defaults to False.
            safe_max_files (int, optional): 안전 모드 적용 시 최대 허용 파일 수. Defaults to DEFAULT_MAX_FILES.
            safe_max_lines (int, optional): 안전 모드 적용 시 최대 허용 diff 줄 수. Defaults to DEFAULT_MAX_LINES.

        Returns:
            str: 수집 및 필터링이 완료된 diff 문자열 (변경 사항이 없을 경우 빈 문자열 '').

        Raises:
            None
        """
        diff = ''
        # 1. PR 모드인 경우 브랜치 기반 diff 수집 시도
        if for_pr:
            diff = self._branch_diff()

        # 2. 커밋 모드이거나 브랜치 diff가 없는 경우: Staged + Unstaged diff 통합 수집
        if not diff:
            staged = self._run(['git', 'diff', '--cached'])
            unstaged = self._run(['git', 'diff'])
            diff = (staged + unstaged).strip()

        # 3. 안전 모드(-safe-mode) 활성화 시 민감정보 마스킹 및 크기 제한 적용
        if safe_mode:
            diff, stats = self._apply_safe(diff, safe_max_files, safe_max_lines)
            # 마스킹 및 절삭 통계 안내 출력
            if stats['masked']:
                print(f'[SAFE] 민감 패턴 {stats["masked"]}건 마스킹됨')
            if stats['files_trimmed']:
                print(f'[SAFE] 파일 {stats["files_trimmed"]}개 생략됨 (최대 {safe_max_files}개)')
            if stats['lines_trimmed']:
                print(f'[SAFE] {stats["lines_trimmed"]}줄 생략됨 (최대 {safe_max_lines}줄)')

        return diff

    def get_current_branch(self) -> str:
        """현재 체크아웃되어 있는 Git 브랜치 이름을 반환한다.

        Returns:
            str: 현재 브랜치 이름 (식별 불가 시 기본값 'main').
        """
        branch = self._run(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch or 'main'

    def _branch_diff(self) -> str:
        """기준 브랜치(main/master)와 현재 브랜치의 공통 조상(merge-base) 대비 diff를 산출한다.

        기준 브랜치 후보군('main', 'master', 'origin/main', 'origin/master')을 순차 탐색하여
        가장 먼저 매칭되는 병합 기준점(merge-base SHA)을 찾고 `git diff {sha}..HEAD`를 실행합니다.

        Returns:
            str: 기준 브랜치 대비 현재 브랜치의 diff 문자열 (찾지 못한 경우 빈 문자열 '').
        """
        for base in ['main', 'master', 'origin/main', 'origin/master']:
            r = subprocess.run(['git', 'merge-base', 'HEAD', base],
                               capture_output=True, text=True)
            if r.returncode == 0:
                sha = r.stdout.strip()
                diff = self._run(['git', 'diff', f'{sha}..HEAD'])
                if diff:
                    return diff
        return ''

    def _apply_safe(self, diff: str, max_files: int,
                    max_lines: int) -> tuple[str, dict]:
        """diff 문자열에 9종 민감정보 마스킹 및 파일/라인 수 한도 절삭을 적용한다.

        Args:
            diff (str): 원본 Git diff 문자열.
            max_files (int): 수집할 최대 파일 개수.
            max_lines (int): 수집할 최대 diff 줄 수.

        Returns:
            tuple[str, dict]: (안전 필터링된 diff 문자열, 처리 통계 딕셔너리).
                stats keys: 'masked' (마스킹된 패턴 건수),
                            'files_trimmed' (생략된 파일 수),
                            'lines_trimmed' (생략된 라인 수)
        """
        stats = {'masked': 0, 'files_trimmed': 0, 'lines_trimmed': 0}

        # 1. 9종 정규식 패턴을 순회하며 민감 정보 마스킹 치환
        for pattern, repl in _SENSITIVE:
            new, n = re.subn(pattern, repl, diff, flags=re.DOTALL)
            diff = new
            stats['masked'] += n

        # 2. 파일 수 제한 검사: 'diff --git' 헤더 카운트를 통해 허용된 파일 수 초과 시 절삭
        lines = diff.splitlines()
        total_files = sum(1 for l in lines if l.startswith('diff --git'))
        filtered, file_count = [], 0
        for line in lines:
            if line.startswith('diff --git'):
                file_count += 1
                if file_count > max_files:
                    stats['files_trimmed'] = total_files - max_files
                    filtered.append(
                        f'\n[SAFE] 나머지 {stats["files_trimmed"]}개 파일 생략됨')
                    break
            filtered.append(line)

        # 3. 라인 수 제한 검사: 최대 허용 줄 수(max_lines) 초과 시 하드 절삭
        result = '\n'.join(filtered)
        result_lines = result.splitlines()
        if len(result_lines) > max_lines:
            stats['lines_trimmed'] = len(result_lines) - max_lines
            result = '\n'.join(result_lines[:max_lines])
            result += f'\n\n[SAFE] {stats["lines_trimmed"]}줄 생략됨'

        return result, stats
