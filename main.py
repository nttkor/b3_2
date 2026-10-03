"""AI 기반 Git 커밋/PR 자동 생성기 - 루트 엔트리포인트."""
import os
import sys
from pathlib import Path

# 가상환경(.venv)이 존재할 경우, source 활성화 없이도 .venv 파이썬으로 자동 재실행
_venv_python = Path(__file__).resolve().parent / '.venv' / 'bin' / 'python'
if _venv_python.exists() and Path(sys.executable).resolve() != _venv_python.resolve():
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

# src 디렉토리를 sys.path 최우선으로 등록하여 내부 모듈 참조 보장
SRC_DIR = Path(__file__).resolve().parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from main import main
except ModuleNotFoundError as e:
    print(f"[ERROR] 필수 패키지가 설치되지 않았습니다 ({e}).")
    print("## 해결 방법: 가상환경을 활성화하거나 패키지를 설치하세요:")
    print("## source .venv/bin/activate  또는  pip install -r src/requirements.txt")
    sys.exit(1)

if __name__ == '__main__':
    main()
