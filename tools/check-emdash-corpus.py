#!/usr/bin/env python3
"""Corpus-level em-dash tracking (global rule §1: rare tendency, warnings only).

Walks a chapters directory, counts em/en dashes per file on masked prose
only (frontmatter, code blocks, inline code, URLs and HTML are excluded
via prose_global_rules.mask_non_prose), and reports per-file and corpus
totals. Warns when a file or the corpus total exceeds the acceptable
band — never fails: the exit code is always 0.

Defaults follow knowledge/global-rules/default-rules.md §1 ("roughly 1-5
occurrences across 5-10 chapters is acceptable"): warn when one file has
more than 3 dashes, or when the corpus total exceeds 5. Override with flags.

Usage: python tools/check-emdash-corpus.py <chapters-dir> [--glob PATTERN]
       [--per-file-warn N] [--corpus-warn N]
Exit codes: 0 always (warnings are advisory, never failures).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prose_global_rules as gr


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Corpus-level em-dash tracking: per-file and total counts, "
        "warnings only, exit 0 always."
    )
    parser.add_argument("path", help="Chapters directory to walk")
    parser.add_argument("--glob", default="*.md",
                        help="Filename pattern (recursive, default *.md)")
    parser.add_argument("--per-file-warn", type=int, default=3,
                        help="Warn when one file exceeds this many dashes")
    parser.add_argument("--corpus-warn", type=int, default=5,
                        help="Warn when the corpus total exceeds this many")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.is_dir():
        print(f"Not a directory: {args.path}", file=sys.stderr)
        return 0

    files = sorted(root.rglob(args.glob))
    counts: list[tuple[str, int]] = []
    for path in files:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            print(f"  {path.relative_to(root)}: unreadable ({error}), skipped")
            continue
        total = gr.count_em_dashes(gr.mask_non_prose(text))
        counts.append((str(path.relative_to(root)), total))

    print(f"em-dash corpus report: {root} ({len(counts)} file(s))")
    for name, total in counts:
        flag = "  <-- exceeds per-file warn" if total > args.per_file_warn else ""
        print(f"  {name}: {total}{flag}")
    corpus_total = sum(total for _, total in counts)
    print(f"corpus total: {corpus_total} em/en dash(es)")

    warned = False
    for name, total in counts:
        if total > args.per_file_warn:
            print(f"WARNING: {name} has {total} dashes "
                  f"(per-file warn threshold {args.per_file_warn}).")
            warned = True
    if corpus_total > args.corpus_warn:
        print(f"WARNING: corpus total {corpus_total} exceeds the acceptable band "
              f"(threshold {args.corpus_warn}; default-rules.md §1: roughly 1-5 "
              "across 5-10 chapters). Confirm each dash earns its place.")
        warned = True
    if not warned:
        print("No excess: within the rare-tendency band.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
