#!/usr/bin/env bash
# B6-2 R01 verification-only helper. Does not call an AI API.

set -u

PASS=0
FAIL=0
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROUND_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
REF="$ROUND_DIR/reference"
TMP_REPO=$(mktemp -d /tmp/codyssey-b6-2-git-XXXXXX)
trap 'rm -rf "$TMP_REPO" /tmp/b6-2-tests.out' EXIT

pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

if command -v python3 >/dev/null 2>&1; then PYTHON=python3; elif command -v python >/dev/null 2>&1; then PYTHON=python; else
  echo "[FAIL] Python not found"; echo "Result: 0 PASS / 1 FAIL"; exit 1
fi

$PYTHON -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' && pass "Python >= 3.10" || fail "Python >= 3.10"
command -v git >/dev/null 2>&1 && pass "git command" || fail "git command"

for file in \
  "$REF/git_ai/git_tools.py" \
  "$REF/git_ai/prompts.py" \
  "$REF/git_ai/ai_client.py" \
  "$REF/git_ai/validators.py" \
  "$REF/git_ai/cli.py" \
  "$REF/tests/test_git_ai.py"; do
  [ -f "$file" ] && pass "file exists: ${file#$ROUND_DIR/}" || fail "file missing: ${file#$ROUND_DIR/}"
done

if PYTHONPATH="$REF" $PYTHON -m compileall -q "$REF"; then pass "Python syntax compile"; else fail "Python syntax compile"; fi

if PYTHONPATH="$REF" $PYTHON -m unittest discover -s "$REF/tests" -p 'test_*.py' >/tmp/b6-2-tests.out 2>&1; then
  pass "Reference unit tests"
else
  fail "Reference unit tests (see /tmp/b6-2-tests.out)"
fi

# Verify real git status/diff collection inside a disposable local repository.
if command -v git >/dev/null 2>&1; then
  (
    cd "$TMP_REPO" || exit 1
    git init -q
    git config user.name "B6 Test"
    git config user.email "b6-test@example.invalid"
    printf 'first\n' > sample.txt
    git add sample.txt
    git commit -qm 'chore: seed test repo'
    printf 'second\n' >> sample.txt
    PYTHONPATH="$REF" $PYTHON - <<'PY'
from git_ai.git_tools import collect_changes
c = collect_changes()
raise SystemExit(0 if 'sample.txt' in c.status and '+second' in c.unstaged_diff else 1)
PY
  ) && pass "git status/diff collector" || fail "git status/diff collector"
fi

if grep -RInE '(sk-[A-Za-z0-9_-]{12,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|AI_API_KEY[[:space:]]*=[[:space:]]*[A-Za-z0-9_-]{12,})' "$ROUND_DIR" --exclude='verify.sh' >/tmp/b6-2-secret-scan.out 2>/dev/null; then
  fail "possible credential-like text detected"
else
  pass "no obvious credential-like value in Round files"
fi

if grep -Rq 'git status' "$REF/git_ai" && grep -Rq 'git diff' "$ROUND_DIR"; then pass "Git change collection documented"; else fail "Git change collection documentation"; fi
if grep -Rq -- '--temperature' "$REF/git_ai/cli.py" && grep -Rq -- '--max-tokens' "$REF/git_ai/cli.py" && grep -Rq -- '--model' "$REF/git_ai/cli.py"; then
  pass "model/temperature/max-tokens CLI options"
else
  fail "required AI CLI options"
fi

echo
printf 'Result: %d PASS / %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
