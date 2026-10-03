"""AI 기반 Git 커밋/PR 자동 생성기 - 루트 엔트리포인트 (main.py).

이 파일은 프로젝트 루트 디렉토리에서 `python main.py commit` 또는 `python main.py pr` 명령을
직접 실행할 수 있도록 지원하는 루트 부트스트랩 스크립트입니다.

주요 특징:
    1. 가상환경 자동 감지 및 프로세스 치환 (`os.execv`):
       - 사용자가 가상환경을 활성화하지 않고 글로벌 파이썬으로 실행하더라도,
         `.venv/bin/python`의 존재 여부와 `sys.prefix`를 비교하여
         가상환경 파이썬 프로세스로 즉각 전환(re-exec)합니다.
    2. 소스 경로(`src/`) 자동 주입:
       - `src/` 디렉토리를 `sys.path` 최상단(index 0)에 등록하여,
         하위 패키지 모듈 간의 상대 및 절대 임포트가 충돌 없이 원활히 동작하도록 보장합니다.
"""

import os
import sys
from pathlib import Path

# 가상환경(.venv)이 존재할 경우, source 활성화 없이도 .venv 파이썬으로 자동 재실행
_venv_dir = Path(__file__).resolve().parent / '.venv'
_venv_python = _venv_dir / 'bin' / 'python'
if _venv_python.exists() and Path(sys.prefix).resolve() != _venv_dir.resolve():
    # 현재 프로세스를 가상환경 인터프리터로 덮어씌워 재실행
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

# src 디렉토리를 sys.path 최우선으로 등록하여 내부 모듈 참조 보장
SRC_DIR = Path(__file__).resolve().parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 필수 패키지 임포트 검증
try:
    from main import main
except ModuleNotFoundError as e:
    print(f"[ERROR] 필수 패키지가 설치되지 않았습니다 ({e}).")
    print("## 해결 방법: 가상환경을 활성화하거나 패키지를 설치하세요:")
    print("## source .venv/bin/activate  또는  pip install -r src/requirements.txt")
    sys.exit(1)

if __name__ == '__main__':
    main()
