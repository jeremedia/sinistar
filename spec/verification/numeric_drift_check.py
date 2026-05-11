#!/usr/bin/env python3
"""
Numeric drift check.

Detects bare numeric claims in prose chapters that should instead cite a
YAML record. The pattern caught the spec out twice across pass-3 and
pass-4 review cycles: the YAML value was updated but a narrative
mention (e.g., "4 sinibomb hits", "30,000 points") drifted out of sync.

For each (concept_label, regex, yaml_ref) tuple, we scan every prose
chapter for matches of the regex. For each match, we require the
matching YAML reference (e.g. `tunables.yaml#pieces_required`) to appear
within WINDOW lines of the match. If it doesn't, the line is reported
as a drift candidate.

Run: python3 spec/verification/numeric_drift_check.py
Exit 0 if clean, non-zero on violations.

To add a new concept:
  1. Add a (label, regex, yaml_ref) entry to CHECKS.
  2. Run; fix flagged lines by adding the yaml_ref inline.
  3. Add an exception below if a match is a legitimate non-spec mention
     (historical note, prototype value, etc).
"""

import glob
import os
import re
import sys

SPEC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINDOW = 12  # lines above/below in which the yaml_ref must appear.
             # Wide enough that a table-header citation covers all rows;
             # narrow enough that drift in nearby prose stays visible.

# (label, regex, required_yaml_ref)
# regex is matched case-insensitively across the whole prose document.
CHECKS = [
    # Sinistar HP
    (
        "sinistar_sinibomb_hits",
        r"\b(\d+)\s+sinibomb hits?\b",
        "tunables.yaml#pieces_required",
    ),
    # Sinistar assembly
    (
        "sinistar_assembly_pieces",
        r"\b(\d+)\s+(crystals|skull pieces|pieces deliver)",
        "tunables.yaml#assembly_pieces",
    ),
    # Bay capacity. Only match the actual capacity claim (20 sinibombs).
    # "+1 sinibomb to bay" and "12 sinibomb hits" should NOT trigger.
    (
        "sinibomb_bay",
        r"\b20\s+sinibombs?\b|\bMAXBOMBS?\s*=\s*20\b|\bmax_in_bay\s*=\s*20\b",
        "tunables.yaml#max_in_bay",
    ),
    # Extra ship thresholds
    (
        "first_extra_ship_at",
        r"\b30,?000\s*(?:points)?\s+(?:for\s+)?(?:the\s+)?first\s+extra",
        "operator-defaults.yaml#first_extra_ship_at",
    ),
    (
        "extra_ship_factor",
        r"(?:every|each)\s+30,?000\s+points",
        "operator-defaults.yaml#additional_extra_ship_factor",
    ),
    # Starting ships
    (
        "starting_ships",
        r"\b(?:starts?|default\s+is)\s+(?:with\s+)?(\d+)\s+ships?\b",
        "operator-defaults.yaml#ships_per_game",
    ),
    # Scoring values
    (
        "score_sinistar",
        r"\b15[,\s]?000\s+(?:points|pts)\b",
        "scoring.yaml#destroy_sinistar",
    ),
    (
        "score_warrior_kill",
        r"\bwarrior[^.]{0,40}\b500\s+(?:points|pts|score)",
        "scoring.yaml#kill_warrior",
    ),
    (
        "score_worker_kill",
        r"\bworker[^.]{0,40}\b150\s+(?:points|pts|score)",
        "scoring.yaml#kill_worker",
    ),
    (
        "score_crystal",
        r"\bcrystal[^.]{0,40}\b200\s+(?:points|pts|score)",
        "scoring.yaml#collect_crystal",
    ),
    # Frame rate
    (
        "tick_rate",
        r"\b60\s*hz\b",
        "tunables.yaml#tick_rate_hz",
    ),
    # Vibration mechanic constants
    (
        "vibration_max",
        r"\bRchMax\s*=\s*96\b|\bvibration_max\s*=\s*96\b|\b96\s+richter\b",
        "tunables.yaml#vibration_max",
    ),
    (
        "crystal_toss_threshold",
        r"\bCrProb\s*=\s*16\b|\bthreshold\s+(?:of|=)\s+16\b",
        "tunables.yaml#crystal_toss_threshold",
    ),
    # Sinistar AI
    (
        "sinistar_stun",
        r"\b(\d+)\s+stun\s+frames?\b|\bstuns?\s+(?:sinistar\s+)?for\s+(\d+)\s+frames?\b",
        "tunables.yaml#stun_per_hit_frames",
    ),
    # Warrior cooldown
    (
        "warrior_inhibitor",
        r"\b(\d+)\s*-?\s*frame\s+(?:warrior\s+)?(?:cooldown|inhibitor)\b",
        "tunables.yaml#shooting_inhibitor_max",
    ),
]

# Lines on which a flagged match should be ignored.
# Use sparingly — prefer adding the yaml_ref to the prose.
# Format: (filename_basename, label, partial_line_text)
EXEMPTIONS = [
    # Historical / prototype values, explicitly framed as "the original
    # development default was N", not as a current spec claim.
    ("07-scoring.md", "extra_ship_factor", "original development default was 5,000"),
    ("11-operator-config.md", "extra_ship_factor", "originally $05"),
    # Attract-mode demo phase 1 references "≥4 needed in the original" —
    # that's the attract demo's own threshold, not the live game's HP.
    ("08-game-flow.md", "sinistar_sinibomb_hits", "≥4 needed in"),
    # Numeric mentions inside fenced code blocks are pseudocode and
    # carry their own yaml_ref nearby; allow.
    # (Implementation note: fenced-block detection is done below.)
]


def is_in_fence(lines, line_idx):
    """Return True if line_idx falls inside a ``` fenced block."""
    fences = 0
    for i in range(line_idx):
        if lines[i].lstrip().startswith("```"):
            fences += 1
    return fences % 2 == 1


def has_yaml_ref_nearby(lines, line_idx, yaml_ref):
    lo = max(0, line_idx - WINDOW)
    hi = min(len(lines), line_idx + WINDOW + 1)
    for i in range(lo, hi):
        if yaml_ref in lines[i]:
            return True
    return False


def is_exempt(basename, label, line_text):
    for ex_file, ex_label, ex_partial in EXEMPTIONS:
        if ex_file == basename and ex_label == label and ex_partial in line_text:
            return True
    return False


def main():
    md_files = sorted(glob.glob(os.path.join(SPEC_ROOT, "*.md")))
    violations = []
    matches_total = 0

    for md in md_files:
        basename = os.path.basename(md)
        with open(md) as fh:
            text = fh.read()
        lines = text.splitlines()

        for label, regex, yaml_ref in CHECKS:
            pat = re.compile(regex, re.IGNORECASE)
            for line_idx, line in enumerate(lines):
                if pat.search(line):
                    matches_total += 1
                    if is_in_fence(lines, line_idx):
                        continue
                    if is_exempt(basename, label, line):
                        continue
                    if not has_yaml_ref_nearby(lines, line_idx, yaml_ref):
                        violations.append(
                            (basename, line_idx + 1, label, yaml_ref, line.strip())
                        )

    print("Numeric drift check")
    print(f"  prose files scanned: {len(md_files)}")
    print(f"  total numeric matches: {matches_total}")
    print(f"  violations: {len(violations)}")
    print()

    if violations:
        for basename, lineno, label, yaml_ref, line in violations:
            print(f"  {basename}:{lineno}")
            print(f"    label:     {label}")
            print(f"    expected:  reference {yaml_ref} within {WINDOW} lines")
            print(f"    line:      {line[:120]}")
            print()
        print(f"Fix each by adding `{yaml_ref}` to the same or adjacent line,")
        print("or add an exemption to EXEMPTIONS in this script if the match is")
        print("a legitimate non-spec mention.")
        return 1

    print("Clean — no drift detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
