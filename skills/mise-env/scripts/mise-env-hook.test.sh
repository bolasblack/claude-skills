#!/bin/bash
# Tests for mise-env-hook.sh: it appends the mise hook-env line to $CLAUDE_ENV_FILE.
hook="$(cd "$(dirname "$0")" && pwd)/mise-env-hook.sh"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
fails=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: got [$2] want [$3]"; fails=$((fails+1)); fi; }

mkdir "$tmp/bin"; printf '#!/bin/sh\n' > "$tmp/bin/mise"; chmod +x "$tmp/bin/mise"
want='eval "$(mise hook-env -s bash -q)"'
PATH_WITH="$tmp/bin:/usr/bin:/bin"
PATH_WITHOUT="/usr/bin:/bin"

# 1. appends the line when mise is on PATH
: > "$tmp/env"; PATH="$PATH_WITH" CLAUDE_ENV_FILE="$tmp/env" bash "$hook"; rc=$?
check "appends line" "$(cat "$tmp/env")" "$want"; check "exit 0" "$rc" 0

# 2. keeps what other hooks already wrote
echo 'export OTHER=1' > "$tmp/env"; PATH="$PATH_WITH" CLAUDE_ENV_FILE="$tmp/env" bash "$hook"
check "appends, never overwrites" "$(head -1 "$tmp/env")" 'export OTHER=1'

# 3. CLAUDE_ENV_FILE empty: silent, writes nothing
out=$(PATH="$PATH_WITH" CLAUDE_ENV_FILE= bash "$hook" 2>&1); rc=$?
check "empty env file: no output" "$out" ""; check "empty env file: exit 0" "$rc" 0

# 4. mise missing: silent, writes nothing
: > "$tmp/env"; out=$(PATH="$PATH_WITHOUT" CLAUDE_ENV_FILE="$tmp/env" bash "$hook" 2>&1); rc=$?
check "no mise: no output" "$out" ""; check "no mise: file untouched" "$(cat "$tmp/env")" ""; check "no mise: exit 0" "$rc" 0

# 5. unwritable env file never blocks session start
PATH="$PATH_WITH" CLAUDE_ENV_FILE="$tmp/nodir/env" bash "$hook" 2>/dev/null; check "unwritable: exit 0" "$?" 0

[ "$fails" = 0 ] && echo "all passed"; exit "$fails"
