#!/usr/bin/env bash
set -euo pipefail

AFFECTED_FILE="${1:-affected.txt}"
REPORT_CSV="affected-report.csv"

if [[ ! -f "$AFFECTED_FILE" ]]; then
  echo "Usage: $0 path/to/affected.txt"
  exit 1
fi

echo "target,workspace,reason" > "$REPORT_CSV"

echo "== Direct usages in package.json =="
while read -r pkg; do
  echo "### Direct usages of $pkg ###"
  git grep -nE "\"${pkg}\"\\s*:\\s*\"[^\"]+\"" -- '**/package.json' || true
  echo
done < "$AFFECTED_FILE"

echo "== Transitive & direct chains (pnpm why -r) =="
while read -r pkg; do
  echo "===== $pkg ====="
  # Print human-readable
  pnpm -r why "$pkg" || true | tee /tmp/_why.out

  # Append a coarse CSV: target,workspace,reason_line
  awk -v target="$pkg" '
    /^[[:space:]]*Project:/ { ws=$2; gsub(/^[[:space:]]+|:$/, "", ws); next }
    NF>0 && ws!=""          { gsub(/^[[:space:]]+/, "", $0); printf("%s,%s,%s\n", target, ws, $0) }
  ' /tmp/_why.out >> "$REPORT_CSV" || true
  echo
done < "$AFFECTED_FILE"

echo "Report written to $REPORT_CSV"
