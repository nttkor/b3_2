"""AI 기반 Git 커밋/PR 자동 생성기 - 루트 엔트리포인트."""
import sys
from pathlib import Path

# src 디렉토리를 sys.path 최우선으로 등록하여 내부 모듈 참조 보장
SRC_DIR = Path(__file__).resolve().parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import main

if __name__ == '__main__':
    main()
