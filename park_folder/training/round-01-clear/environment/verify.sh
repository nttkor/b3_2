#!/usr/bin/env bash
# B3-2 R01 verification-only helper.
# Reference mode: bash verify.sh
# Runtime evidence gate: bash verify.sh --runtime

set -u

PASS=0
FAIL=0
MODE="${1:-reference}"
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROUND_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
REFERENCE="$ROUND_DIR/reference"
REPO_ROOT=$(cd "$SCRIPT_DIR/../../.." && pwd)
TEST_OUT=$(mktemp /tmp/b3-2-tests.XXXXXX)
trap 'rm -f "$TEST_OUT"' EXIT

pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "[FAIL] Python not found"
    echo "Result: 0 PASS / 1 FAIL"
    exit 1
fi

VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if $PYTHON -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'; then
    pass "Python >= 3.10 ($VERSION)"
else
    fail "Python >= 3.10 required ($VERSION)"
fi

for file in \
  "$REFERENCE/main.py" \
  "$REFERENCE/mini_git/__init__.py" \
  "$REFERENCE/mini_git/models.py" \
  "$REFERENCE/mini_git/algorithms.py" \
  "$REFERENCE/mini_git/repository.py" \
  "$REFERENCE/mini_git/cli.py" \
  "$REFERENCE/tests/test_mini_git.py" \
  "$REFERENCE/README.md" \
  "$ROUND_DIR/docs/requirements-mapping.md" \
  "$ROUND_DIR/docs/evaluation-qa.md" \
  "$ROUND_DIR/evidence/README.md"; do
    [ -f "$file" ] && pass "file exists: ${file#$REPO_ROOT/}" || fail "file missing: ${file#$REPO_ROOT/}"
done

# Parse source without compileall so verification does not intentionally create __pycache__.
if REFERENCE="$REFERENCE" PYTHONDONTWRITEBYTECODE=1 $PYTHON <<'PY'
import ast
import os
import pathlib
import sys

root = pathlib.Path(os.environ["REFERENCE"])
for path in root.rglob("*.py"):
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        print(f"syntax error: {path}: {exc}")
        sys.exit(1)
PY
then
    pass "Python AST syntax parse"
else
    fail "Python AST syntax parse"
fi

if PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$REFERENCE" $PYTHON -m unittest discover \
    -s "$REFERENCE/tests" -p 'test_*.py' >"$TEST_OUT" 2>&1; then
    pass "Reference unit tests"
else
    fail "Reference unit tests"
    cat "$TEST_OUT"
fi

# The mission bans Python sorting APIs and graph-specific libraries.
if REFERENCE="$REFERENCE" PYTHONDONTWRITEBYTECODE=1 $PYTHON <<'PY'
import ast
import os
import pathlib
import sys

root = pathlib.Path(os.environ["REFERENCE"]) / "mini_git"
forbidden_graph_roots = {"networkx", "igraph", "graph_tool"}
violations = []
for path in root.glob("*.py"):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "sorted":
                violations.append((path.name, node.lineno, "sorted()"))
            if isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
                violations.append((path.name, node.lineno, ".sort()"))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in forbidden_graph_roots:
                    violations.append((path.name, node.lineno, alias.name))
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".", 1)[0] in forbidden_graph_roots:
                violations.append((path.name, node.lineno, node.module))
if violations:
    for item in violations:
        print("forbidden:", item)
    sys.exit(1)
PY
then
    pass "no standard sort API / graph library in Mini Git core"
else
    fail "forbidden sorting API or graph library detected"
fi

if PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$REFERENCE" $PYTHON - <<'PY'
from mini_git.cli import execute
from mini_git.repository import MiniGitRepository

r = MiniGitRepository()
checks = [
    execute(r, 'INIT "Alice Kim"').startswith("Initialized"),
    "c000001" in execute(r, 'COMMIT "root commit"'),
    execute(r, "BRANCH feature/a").startswith("Created branch"),
    execute(r, "SWITCH feature/a").startswith("Switched"),
    "c000002" in execute(r, 'COMMIT "add login feature"'),
    "c000001" in execute(r, "ANCESTORS c000002"),
    "add login feature" in execute(r, "SEARCH login"),
    "Alice Kim" in execute(r, 'SEARCH --author="Alice Kim"'),
    "c000001" in execute(r, "LOG --sort-by=date"),
    "c000001" in execute(r, "LOG --sort-by=author"),
]
raise SystemExit(0 if all(checks) else 1)
PY
then
    pass "required command smoke test"
else
    fail "required command smoke test"
fi

if command -v git >/dev/null 2>&1 && git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    TRACKED=$(git -C "$REPO_ROOT" ls-files 'training/round-01-clear/**' | \
      grep -E '(^|/)(\.env($|\.)|.*\.(key|pem)$|secrets/)' || true)
    [ -z "$TRACKED" ] && pass "no tracked Secret-pattern files" || fail "tracked Secret-pattern files detected"
else
    pass "git Secret filename scan skipped outside worktree"
fi

if [ "$MODE" = "--runtime" ] || [ "$MODE" = "runtime" ]; then
    RUNTIME_DIR="$ROUND_DIR/evidence/runtime"
    for file in verify.txt repl.txt evaluation.md; do
        if [ -s "$RUNTIME_DIR/$file" ]; then
            pass "runtime evidence exists: evidence/runtime/$file"
        else
            fail "runtime evidence missing: evidence/runtime/$file"
        fi
    done
fi

echo
printf 'Result: %d PASS / %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
