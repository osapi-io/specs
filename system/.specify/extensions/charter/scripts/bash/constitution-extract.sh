#!/usr/bin/env bash
# constitution-extract.sh — Extract content of a specific section from constitution.md
# Usage: constitution-extract.sh <SECTION_ID> [CONSTITUTION_PATH]
#
# Extracts everything between the section marker and the next marker (or end of
# file / speckit footer). Strips the speckit top comment and bottom metadata.
#
# Supports typed markers (<!-- [TYPE] ID SECTION -->) and legacy markers
# (<!-- [ID] SECTION -->). The SECTION_ID argument is always just the plain ID
# (e.g., "global/compliance", "PROJECT SPECIFIC") — callers do not include the
# type tag.
set -euo pipefail

SECTION_NAME="${1:?Usage: constitution-extract.sh <SECTION_ID> [CONSTITUTION_PATH]}"
CONSTITUTION_PATH="${2:-.specify/memory/constitution.md}"

if [[ ! -f "$CONSTITUTION_PATH" ]]; then
  echo ""
  exit 0
fi

awk -v section="$SECTION_NAME" '
BEGIN { in_section=0; found=0; n=0 }

# Match any section marker (typed or legacy) and extract the ID.
# Typed:  <!-- [TYPE] ID SECTION -->
# Legacy: <!-- [ID] SECTION -->
/^[[:space:]]*<!-- \[/ {
  s = $0
  name = ""

  # Try typed marker: contains "] " (closing bracket followed by space then ID)
  close_bracket = index(s, "] ")
  if (close_bracket > 0) {
    # Verify it looks like a typed marker: bracket content is A-Z only
    open_bracket = index(s, "[")
    if (open_bracket > 0 && open_bracket < close_bracket) {
      tag = substr(s, open_bracket + 1, close_bracket - open_bracket - 1)
      # Tag is uppercase letters only → typed marker
      if (tag ~ /^[A-Z]+$/) {
        rest = substr(s, close_bracket + 2)
        section_end = index(rest, " SECTION -->")
        if (section_end > 0) {
          name = substr(rest, 1, section_end - 1)
        }
      }
    }
  }

  # Fall back to legacy marker: <!-- [ID] SECTION -->
  if (name == "") {
    open_bracket = index(s, "[")
    close_bracket = index(s, "]")
    if (open_bracket > 0 && close_bracket > open_bracket) {
      name = substr(s, open_bracket + 1, close_bracket - open_bracket - 1)
    }
  }

  if (name != "") {
    if (name == section) {
      in_section=1
      found=1
      next
    } else if (in_section) {
      in_section=0
      exit
    }
  }
}

# Skip speckit footer metadata
in_section && /^\*Version\*:/ { in_section=0; hit_footer=1; exit }
in_section && /^\*\*Version\*\*:/ { in_section=0; hit_footer=1; exit }

# Collect content while in section
in_section { lines[n++] = $0 }

END {
  # Trim leading blank lines. The marker is followed by one in the composed
  # constitution but not in the snapshot, so keeping it reports every section
  # as modified.
  first = 0
  while (first < n && lines[first] == "") first++

  # Trim trailing blank lines so inter-section separators are not included
  last = n - 1
  while (last >= first && lines[last] == "") last--

  # The final section runs into the "---" rule that precedes the speckit
  # version footer. Drop it, and any blank lines it leaves behind. Only when
  # the footer was actually reached, so a fragment legitimately ending in a
  # horizontal rule keeps it.
  if (hit_footer) {
    while (last >= first && (lines[last] == "" || lines[last] == "---")) last--
  }

  for (i = first; i <= last; i++) print lines[i]
}
' "$CONSTITUTION_PATH"
