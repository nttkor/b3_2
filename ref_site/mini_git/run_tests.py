"""테스트 실행기.

    python run_tests.py            전체 실행
    python run_tests.py -v         상세 출력
    python -m unittest tests.test_graph -v   특정 모듈만
"""

import sys
import unittest


def main() -> int:
    verbosity = 2 if "-v" in sys.argv else 1
    suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())