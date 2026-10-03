#!/usr/bin/env python3
"""English prose checker — deterministic global-rule validation.

Framework counterpart to check-prose.py (which is Chinese-oriented).
Enforces the deterministic subset of the global writing rules
(knowledge/global-rules/): colon/semicolon bans, dialogue paragraph
architecture, plus the measurable AI-tell subset.

Usage: python3 tools/check-prose-en.py <manuscript path|-> [--pov NAME] [--min-words N]
Exit codes: 0 = no failures (warnings may exist); 1 = failures present; 2 = read error.

Deterministic failures (global hard rules):
- colon ":" in prose (user-explicit global default)
- semicolon ";" in prose (user-explicit global default)
- two structurally separate dialogue units in one paragraph
- AI road-sign phrases, reversal sentences, "as you know" exposition dialogue

Corpus-level tendencies (warnings, never failures):
- em dash: extremely rare (roughly 1-5 across 5-10 chapters acceptable)

Mechanical POV subset (warnings, opt-in with --pov):
- inner-state verbs attributed to other named characters
- narrator-foreshadowing patterns

SCOPE NOTES (honest limits):
- Checks run on masked prose only: frontmatter, code blocks, inline code,
  links, URLs, and HTML tags are masked first, so colons/semicolons in code
  or metadata never fail. Prose-only by construction.
- A full sentence-level "could the POV character know this?" audit needs
  semantic understanding and is NOT regex-feasible; --pov catches the
  mechanical subset only.
- Hedged perception ("seemed", "appeared", "she took that as...",
  "he wondered whether...") is epistemically REQUIRED marking
  (knowledge/cognition/epistemic-layers.md) and is deliberately NEVER
  flagged.
- Em dash is a tendency, not a ban: it is tracked and warned on excess,
  never a deterministic failure.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- patterns

# Blatant AI-artifact phrases -> failure.
HARD_ROAD_SIGNS = (
    "it's worth noting that",
    "it is worth noting that",
    "in today's fast-paced world",
    "as an ai language model",
    "as a language model",
)

# AI-leaning diction -> warning.
SOFT_AI_DICTION = (
    "delve", "tapestry", "vibrant", "bustling", "intricate",
    "testament to", "in the realm of", "a myriad of", "ever-evolving",
    "furthermore", "additionally", "consequently",
)

# Reversal sentences -> failure.
REVERSAL_PATTERNS = (
    re.compile(r"\bit was not\b[^.!?\n]{1,60}?\bit was\b", re.IGNORECASE),
    re.compile(r"\bit wasn't\b[^.!?\n]{1,60}?\bit was\b", re.IGNORECASE),
    re.compile(r"\bnot\b[^.!?\n]{1,40}?\bbut rather\b[^.!?\n]{1,60}", re.IGNORECASE),
)

# Exposition dialogue -> failure.
EXPO_DIALOGUE = (
    re.compile(r"\bas you know\b", re.IGNORECASE),
    re.compile(r"\bas we both know\b", re.IGNORECASE),
    re.compile(r"\bas i told you\b", re.IGNORECASE),
)

# Simile markers (density warning).
SIMILE_PATTERNS = (
    re.compile(r"\blike a\b", re.IGNORECASE),
    re.compile(r"\blike an\b", re.IGNORECASE),
    re.compile(r"\blike the\b", re.IGNORECASE),
    re.compile(r"\bas if\b", re.IGNORECASE),
    re.compile(r"\bas though\b", re.IGNORECASE),
)

EMOTION_WORDS = (
    "angry", "furious", "enraged", "sad", "sorrowful", "happy", "joyful",
    "elated", "afraid", "fearful", "terrified", "anxious", "nervous",
    "ashamed", "guilty", "jealous", "proud", "lonely", "hopeless",
    "relieved", "surprised", "shocked", "embarrassed", "frustrated",
    "desperate", "ecstatic", "miserable", "grief-stricken",
)

INNER_STATE_VERBS = (
    "knew", "felt", "thought", "realized", "realised", "wondered",
    "decided", "wanted", "feared", "hoped", "believed", "remembered",
    "recalled", "noticed", "understood", "sensed", "suspected", "intended",
)
FORESHADOW_PATTERNS = (
    re.compile(r"\bdid not yet know\b", re.IGNORECASE),
    re.compile(r"\blittle did\b", re.IGNORECASE),
    re.compile(r"\bwould (?:later|soon) (?:learn|discover|realize|realise|understand)\b",
               re.IGNORECASE),
)

PRONOUNS = {"he", "she", "they", "it", "we", "you", "i"}

ATTRIBUTION = re.compile(
    r"\b(said|asked|replied|whispered|shouted|murmured|answered|added|continued"
    r"|called|told)\b\s+([A-Za-z']+)|([A-Za-z']+)\s+"
    r"\b(said|asked|replied|whispered|shouted|murmured|answered|added|continued"
    r"|called|told)\b",
    re.IGNORECASE)


def _looks_like_speech(match: re.Match[str]) -> bool:
    """Quoted terms/excerpts ("sheet 4", "within tolerance.") are not dialogue.
    Convention: real dialogue starts capitalized."""
    inner = match.group()[1:-1]
    m = re.search(r"[A-Za-z]", inner)
    return m is not None and m.group().isupper()


def dialogue_violation(text: str) -> str | None:
    """One paragraph = one contiguous dialogue unit. Returns reason or None.

    An interrupted single speech ('"X," she said, "Y."') is one unit.
    Violations: two distinct speakers, two quoted segments with no speaker
    signal at all, or 3+ quoted segments.
    """
    pairs = [m for m in QUOTE_PAIR.finditer(text) if _looks_like_speech(m)]
    if len(pairs) < 2:
        return None
    if len(pairs) > 2:
        return f"{len(pairs)} quoted segments in one paragraph"
    unquoted = QUOTE_PAIR.sub(lambda m: " " * len(m.group()), text)
    named: set[str] = set()
    pro: set[str] = set()
    for m in ATTRIBUTION.finditer(unquoted):
        sp = (m.group(2) or m.group(3) or "").lower()
        if not sp:
            continue
        (pro if sp in PRONOUNS else named).add(sp)
    for i in range(len(pairs) - 1):
        bridge = text[pairs[i].end():pairs[i + 1].start()]
        pro.update(w.lower() for w in
                   re.findall(r"\b(he|she|they|i|we|you)\b", bridge, re.IGNORECASE))
    persons = set(named)
    if not named:
        persons = set(pro)
    elif len(named) == 1:
        pass  # pronouns absorbed by the lone named speaker
    else:
        persons = set(named) | set(pro)
    if len(persons) >= 2:
        return f"two distinct speakers ({', '.join(sorted(persons))}) in one paragraph"
    if not persons:
        return "two quoted segments with no speaker signal between them"
    return None


EM_DASH = re.compile(r"[—–]")
QUOTE_PAIR = re.compile(r'"[^"\n]*"')


@dataclass
class Paragraph:
    position: int
    text: str
    words: int
    sentences: int


@dataclass
class CheckResult:
    failures: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    words: int = 0
    paragraphs: int = 0
    em_dashes: int = 0
    pov: str | None = None


# ---------------------------------------------------------------- helpers

def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", text))


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def excerpt(value: str, width: int = 72) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= width else value[: width - 1] + "…"


def mask_non_prose(text: str) -> str:
    """Mask frontmatter, code, links, URLs, HTML tags; keep positions/newlines."""

    def mask(match: re.Match[str]) -> str:
        return "".join("\n" if c == "\n" else " " for c in match.group())

    patterns = (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),
        re.compile(r"<!--.*?-->", re.DOTALL),
        re.compile(r"```.*?```", re.DOTALL),
        re.compile(r"`[^`\n]*`"),
        re.compile(r"\]\([^)\n]*\)"),
        re.compile(r"https?://[^\s)>]+"),
        re.compile(r"<[^>\n]+>"),
    )
    masked = text
    for pattern in patterns:
        masked = pattern.sub(mask, masked)
    return masked


def split_paragraphs(text: str):
    """Scene headers, markdown, and short lines are skipped; the rest are
    prose paragraphs (one paragraph per line)."""
    paragraphs = []
    position = 0
    for line in text.splitlines():
        start = position
        position += len(line) + 1
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith(("[", "#", ">", "http", "![", "```")):
            continue
        if re.match(r"^(?:[-+*]|\d+[.、])\s", clean):
            continue
        words = word_count(clean)
        if words < 4:
            continue
        sentences = max(1, len(re.findall(r"[.!?…]+", clean)))
        paragraphs.append(Paragraph(start, clean, words, sentences))
    return paragraphs


def sentence_lengths(text: str):
    lengths = []
    for match in re.finditer(r"[^.!?\n]+[.!?]", text):
        words = word_count(match.group())
        if words >= 4:
            lengths.append(words)
    return lengths


def anaphora_runs(text: str, minimum: int = 3):
    runs = []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    run = 1
    for prev, cur in zip(sentences, sentences[1:]):
        pw = re.match(r"[A-Za-z']+", prev)
        cw = re.match(r"[A-Za-z']+", cur)
        if pw and cw and pw.group().lower() == cw.group().lower():
            run += 1
            if run >= minimum:
                runs.append((pw.group(), cur))
        else:
            run = 1
    return runs


def all_matches(text, patterns):
    matches = []
    for pattern in patterns:
        matches.extend(pattern.finditer(text))
    return sorted(matches, key=lambda m: m.start())


def non_overlapping_terms(text, terms):
    matches = []
    occupied = []
    for term in sorted(terms, key=len, reverse=True):
        for match in re.finditer(re.escape(term), text, re.IGNORECASE):
            s, e = match.span()
            if any(s < oe and e > os for os, oe in occupied):
                continue
            matches.append((s, match.group()))
            occupied.append((s, e))
    return sorted(matches)


# ---------------------------------------------------------------- core

def check_text(text: str, pov: str | None = None, min_words: int = 0) -> CheckResult:
    """Run all checks on `text`. Returns CheckResult (failures/warnings/stats).

    min_words=0 disables the word-floor check.
    """
    result = CheckResult(pov=pov)
    prose = mask_non_prose(text)
    paragraphs = split_paragraphs(prose)
    result.words = word_count(prose)
    result.paragraphs = len(paragraphs)
    if result.words == 0:
        result.failures.append("No words detected.")
        return result

    per_1k = lambda n: n * 1000 / result.words  # noqa: E731

    # ---- deterministic failures ----

    # 1. Colon in prose — forbidden (global hard rule).
    for p in paragraphs:
        for m in re.finditer(r":", p.text):
            result.failures.append(
                f"Colon in prose, line {line_number(text, p.position + m.start())}: "
                f"\"{excerpt(p.text, 60)}\"")
            break  # one report per paragraph

    # 2. Semicolon in prose — forbidden (global hard rule).
    for p in paragraphs:
        for m in re.finditer(r";", p.text):
            result.failures.append(
                f"Semicolon in prose, line {line_number(text, p.position + m.start())}: "
                f"\"{excerpt(p.text, 60)}\"")
            break

    # 3. One paragraph = one dialogue unit.
    for p in paragraphs:
        reason = dialogue_violation(p.text)
        if reason:
            result.failures.append(
                f"Two dialogues in one paragraph ({reason}), "
                f"line {line_number(text, p.position)}: \"{excerpt(p.text, 60)}\"")

    # 4. Hard AI road signs.
    for pos, phrase in non_overlapping_terms(prose, HARD_ROAD_SIGNS):
        result.failures.append(
            f"AI road sign, line {line_number(text, pos)}: \"{phrase}\"")

    # 5. Reversal sentences.
    for m in all_matches(prose, REVERSAL_PATTERNS):
        result.failures.append(
            f"Reversal sentence (not-X-but-Y), line {line_number(text, m.start())}: "
            f"\"{excerpt(m.group(), 60)}\"")

    # 6. Exposition dialogue.
    for m in all_matches(prose, EXPO_DIALOGUE):
        result.failures.append(
            f"Exposition dialogue, line {line_number(text, m.start())}: "
            f"\"{excerpt(m.group(), 50)}\"")

    # 7. Word floor (opt-in).
    if min_words and result.words < min_words:
        result.failures.append(
            f"Word count {result.words} below floor {min_words}.")

    # ---- corpus-level tendencies (warnings only) ----

    # W0. Em dash: extremely rare tendency — tracked, never a failure.
    dash_hits = list(EM_DASH.finditer(prose))
    result.em_dashes = len(dash_hits)
    if result.em_dashes > 5:
        lines = sorted({line_number(text, m.start()) for m in dash_hits})
        result.warnings.append(
            f"Em/en dash {result.em_dashes}x in one chapter (lines {lines}) — "
            "corpus tendency is ~1-5 across 5-10 chapters. Confirm each earns its place.")
    elif result.em_dashes > 2:
        lines = sorted({line_number(text, m.start()) for m in dash_hits})
        result.warnings.append(
            f"Em/en dash used {result.em_dashes}x (lines {lines}) — "
            "rare by global tendency; confirm each earns its place.")

    # W1. Sentence-length uniformity.
    lengths = sentence_lengths(prose)
    if len(lengths) >= 12:
        mean = sum(lengths) / len(lengths)
        if mean:
            import math
            cv = math.sqrt(sum((v - mean) ** 2 for v in lengths) / len(lengths)) / mean
            if cv < 0.42:
                result.warnings.append(
                    f"{len(lengths)} sentences have near-uniform length (CV {cv:.2f}).")

    # W2. Repeated paragraph openers (pronouns excluded).
    counts: collections.Counter[str] = collections.Counter()
    for p in paragraphs:
        m = re.match(r"[A-Za-z']+", p.text.lstrip("\"“‘"))
        if not m:
            continue
        opener = m.group()
        if opener.lower() in PRONOUNS:
            continue
        counts[opener] += 1
    repeated = [(o, c) for o, c in counts.items() if c >= 4]
    if repeated:
        details = ", ".join(f"{o} x{c}" for o, c in
                            sorted(repeated, key=lambda x: -x[1]))
        result.warnings.append(f"Repeated paragraph openers: {details}.")

    # W3. Anaphora runs.
    runs = anaphora_runs(prose)
    if runs:
        words = sorted({w for w, _ in runs})
        result.warnings.append(
            f"{len(runs)} anaphora run(s) (3+ sentences opening with "
            f"{', '.join(words[:5])}).")

    # W4. Simile density.
    similes = all_matches(prose, SIMILE_PATTERNS)
    if per_1k(len(similes)) > 4:
        result.warnings.append(
            f"Simile density {per_1k(len(similes)):.1f}/1k words.")

    # W5. Named-emotion density.
    emo = non_overlapping_terms(prose, EMOTION_WORDS)
    if per_1k(len(emo)) > 6:
        result.warnings.append(
            f"Named emotions {per_1k(len(emo)):.1f}/1k words.")

    # W6. AI-leaning diction.
    soft = non_overlapping_terms(prose, SOFT_AI_DICTION)
    if soft:
        kinds = ", ".join(sorted({t.lower() for _, t in soft}))
        result.warnings.append(f"AI-leaning diction: {kinds}.")

    # W7. Mechanical POV subset (opt-in).
    if pov:
        pl = pov.lower()
        name_pat = re.compile(
            r"\b([A-Z][a-z]+)\s+(" + "|".join(INNER_STATE_VERBS) + r")\b")
        for m in name_pat.finditer(prose):
            name = m.group(1)
            if name.lower() == pl or name.lower() in PRONOUNS:
                continue
            result.warnings.append(
                f"Possible head-hop (POV={pov}), line {line_number(text, m.start())}: "
                f"\"{excerpt(m.group(), 50)}\"")
        seen: list[tuple[int, int]] = []
        for m in all_matches(prose, FORESHADOW_PATTERNS):
            if any(m.start() < e and m.end() > s for s, e in seen):
                continue
            seen.append(m.span())
            result.warnings.append(
                f"Narrator foreshadowing (POV={pov}), line {line_number(text, m.start())}: "
                f"\"{excerpt(m.group(), 50)}\"")

    return result


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check English manuscript prose: global hard rules + AI-tell warnings.")
    parser.add_argument("path", help="Markdown/text manuscript path, or - for stdin")
    parser.add_argument("--pov", default=None, help="POV character name")
    parser.add_argument("--min-words", type=int, default=0,
                        help="Chapter word floor (0 = disabled)")
    args = parser.parse_args()

    try:
        text = read_text(args.path)
    except (OSError, UnicodeError) as error:
        print(f"Cannot read manuscript: {error}", file=sys.stderr)
        return 2

    result = check_text(text, pov=args.pov, min_words=args.min_words)

    print(f"Words {result.words}, paragraphs {result.paragraphs}, "
          f"em/en dashes {result.em_dashes}")
    print(f"Failures {len(result.failures)}, warnings {len(result.warnings)}"
          + (f", POV={result.pov}" if result.pov else ""))

    if result.failures:
        print("\nFAILURES (must fix)")
        for item in result.failures:
            print(f"- {item}")
    if result.warnings:
        print("\nWARNINGS (human judgment)")
        for item in result.warnings:
            print(f"- {item}")
    if not result.failures and not result.warnings:
        print("\nNo issues found by this checker.")

    return 1 if result.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
