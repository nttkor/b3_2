"""컨벤션 설정 관리 모듈 (src/convention.py).

이 모듈은 프로젝트 루트의 컨벤션 설정 파일(`.ai-gitgen.yml`)을 탐색 및 파싱하여,
커밋 메시지 및 PR 초안 작성 시 적용할 언어, 접두어(Prefix) 규칙, 필수 섹션 목록,
안전 모드(Safe-mode) 임계치 등의 전역 정책을 공급하는 역할을 담당합니다.

주요 특징:
    1. 무중단 폴백(Graceful Fallback):
       - PyYAML 라이브러리가 설치되지 않았거나 설정 파일이 존재하지 않는 경우에도
         예외를 발생시키지 않고 기본값(`DEFAULTS`)으로 자동 폴백하여 안정성을 보장합니다.
    2. 설정 우선순위 및 딕셔너리 병합:
       - 기본 설정(`DEFAULTS`)에 사용자가 정의한 YAML 설정을 오버레이(Unpacking Merge)하여
         일부 설정만 정의되어 있어도 누락 없는 완전한 설정 딕셔너리를 제공합니다.
"""

from pathlib import Path

# PyYAML 라이브러리 가용성 사전 검사
try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# 프로젝트 표준 기본 설정값 (설정 파일 부재 또는 파싱 불가 시 폴백)
DEFAULTS: dict = {
    'commit_language': 'ko',                        # 커밋 메시지 기본 언어 (ko: 한국어, en: English)
    'commit_prefix': True,                          # Conventional Commit 접두어(feat, fix 등) 강제 여부
    'pr_language': 'ko',                            # PR 초안 기본 언어
    'pr_sections': ['Why', 'What', 'How to Test'],  # PR 본문 필수 3대 섹션
    'safe_max_files': 10,                           # 안전 모드 시 최대 diff 수집 파일 수
    'safe_max_lines': 200,                          # 안전 모드 시 최대 diff 수집 라인 수
}


def load(path: str | None = None) -> dict:
    """컨벤션 설정 파일(.ai-gitgen.yml)을 로드하여 기본값과 병합된 최종 설정을 반환한다.

    지정된 경로 또는 기본 경로('.ai-gitgen.yml')에서 YAML 파일을 찾아 파싱합니다.
    파일이 존재하지 않거나 PyYAML 모듈이 없는 경우 기본 설정(`DEFAULTS`)의 복사본을 반환합니다.

    Args:
        path (str | None, optional): 사용자 지정 컨벤션 YAML 파일 경로.
            None일 경우 프로젝트 루트의 '.ai-gitgen.yml'을 탐색합니다. Defaults to None.

    Returns:
        dict: 기본값(`DEFAULTS`) 위에 사용자 정의 설정이 오버레이된 최종 컨벤션 딕셔너리.

    Raises:
        None: 파일 부재, 모듈 누락 등 어떠한 예외 상황에서도 크래시 없이
            경고 로그 출력 후 기본 설정(`DEFAULTS`) 복사본을 안전하게 반환합니다.
    """
    # 탐색 대상 설정 파일 경로 결정
    config_path = Path(path) if path else Path('.ai-gitgen.yml')

    # 설정 파일이 디스크에 실존하는지 확인
    if config_path.exists():
        # PyYAML 라이브러리가 미설치된 환경인 경우 경고 후 기본값으로 안전 폴백
        if not _HAS_YAML:
            print('[WARN] pyyaml 미설치 — 컨벤션 파일 무시. pip install pyyaml')
            return DEFAULTS.copy()

        # YAML 파일을 안전하게 파싱 (임의 코드 실행을 방지하기 위해 safe_load 사용)
        with open(config_path, encoding='utf-8') as f:
            data = _yaml.safe_load(f) or {}

        # 기본값과 사용자가 정의한 'convention' 하위 키의 설정값 병합
        merged = {**DEFAULTS, **data.get('convention', {})}
        print(f'[INFO] 컨벤션 로드: {config_path}')
        return merged

    # 사용자가 명시적으로 경로를 지정했으나 파일이 존재하지 않는 경우 경고 출력
    if path:
        print(f'[WARN] 컨벤션 파일 없음: {path}  →  기본값 사용')

    # 파일이 없으면 기본 설정값 복사본 반환
    return DEFAULTS.copy()
