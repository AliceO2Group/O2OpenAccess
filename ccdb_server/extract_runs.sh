#!/usr/bin/env bash
# Usage: extract_runs.sh <period> [file...]
# Prints the path component following <period>, with leading zeros removed.
# Reads stdin if no file is given. Output is numerically sorted and unique.
set -euo pipefail

[[ $# -ge 1 ]] || { echo -e "Usage: ${0##*/} <period> [file...]\nN.B.! exact period name is required as 1st argument" >&2; exit 1; }
period="$1"; shift

awk -v p="$period" '
{
  n = split($0, a, "/")
  for (i = 1; i < n; i++)
    if (a[i] == p && a[i+1] ~ /^[0-9]+$/) {
      r = a[i+1]; sub(/^0+/, "", r)
      print r
      break
    }
}' "$@" | sort -nu
