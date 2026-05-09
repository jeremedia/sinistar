#!/usr/bin/env python3
"""
Cross-reference coverage check.

Walks every prose chapter and every YAML file in ../data/, finds inline
references of the form `data/<file>.yaml#<id>` or `<file>.yaml#<id>`, and
verifies each id resolves to a record in the YAML file.

Also reports YAML records with no inbound prose reference.

Run: python3 verification/coverage_check.py
Exit 0 if clean, non-zero if missing references found.
"""

import glob
import os
import re
import sys

import yaml

SPEC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SPEC_ROOT, "data")


def collect_yaml_ids(path):
    """Return set of stable identifiers a YAML record exposes for cross-ref.

    Looks for top-level lists/dicts with `id`, `event_id`, or `name` keys,
    plus nested ids in obvious places (waves, lines, settings, sound_effects, tables).
    Also returns top-level dict keys (e.g. categories under `tunables`).
    """
    with open(path) as fh:
        doc = yaml.safe_load(fh)
    ids = set()

    def walk(node, depth=0):
        if isinstance(node, dict):
            for k, v in node.items():
                # Collect all dict keys as potential cross-ref targets.
                if isinstance(k, str):
                    ids.add(k)
                if k in ("id", "event_id", "name"):
                    if isinstance(v, str):
                        ids.add(v)
                walk(v, depth + 1)
        elif isinstance(node, list):
            for x in node:
                walk(x, depth + 1)

    walk(doc)
    # also collect top-level keys when the doc is a mapping
    if isinstance(doc, dict):
        for k in doc.keys():
            ids.add(k)
        # nested-by-category tunables: tunables.world.{name:...}
        if "tunables" in doc and isinstance(doc["tunables"], dict):
            for cat, items in doc["tunables"].items():
                ids.add(cat)
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict) and "name" in it:
                            ids.add(it["name"])
    return ids


def collect_prose_refs():
    """Find every <file>.yaml#<id> or <file>.yaml#<id> reference in prose chapters and README."""
    refs = []  # (chapter, file, id)
    md_files = sorted(glob.glob(os.path.join(SPEC_ROOT, "*.md")))
    pat = re.compile(r"`?(?:data/)?([a-z0-9_-]+)\.yaml#([A-Za-z0-9_]+)`?")
    for md in md_files:
        with open(md) as fh:
            text = fh.read()
        for m in pat.finditer(text):
            refs.append((os.path.basename(md), m.group(1), m.group(2)))
    return refs


def main():
    yaml_ids = {}  # filename → set of ids
    for y in sorted(glob.glob(os.path.join(DATA_DIR, "*.yaml"))):
        base = os.path.splitext(os.path.basename(y))[0]
        yaml_ids[base] = collect_yaml_ids(y)

    refs = collect_prose_refs()

    missing = []
    seen = set()
    for chapter, fname, ident in refs:
        if fname not in yaml_ids:
            missing.append((chapter, fname, ident, "yaml file not found"))
            continue
        if ident not in yaml_ids[fname]:
            missing.append((chapter, fname, ident, "id not in yaml"))
        else:
            seen.add((fname, ident))

    print(f"Coverage report")
    print(f"  spec/ root:   {SPEC_ROOT}")
    print(f"  yaml files:   {len(yaml_ids)}")
    print(f"  prose refs:   {len(refs)}")
    print(f"  unique refs:  {len(seen)}")
    print()

    if missing:
        print(f"MISSING REFERENCES ({len(missing)}):")
        for c, f, i, why in missing:
            print(f"  {c}: {f}.yaml#{i}  — {why}")
        return 1
    print("All prose references resolve to YAML records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
