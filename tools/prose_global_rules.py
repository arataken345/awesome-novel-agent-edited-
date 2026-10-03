#!/usr/bin/env python3
"""Deterministic global prose rules — language-neutral enforcement.

Single implementation of the hard/soft global writing rules
(knowledge/global-rules/default-rules.md §1–§4), shared by
tools/check-prose.py (Chinese) and tools/check-prose-en.py (English)
so every language enforces identical paragraph architecture.

Hard rules (deterministic failures):
- no colon in prose: ASCII ":" and full-width "：" (CJK)
- no semicolon in prose: ASCII ";" and full-width "；" (CJK)
- one contiguous dialogue unit per paragraph: ASCII "..." and CJK “...”

Soft (warning only, never a failure):
- em dash rarity: corpus-level tendency, tracked — never a hard failure

Prose-only scoping: mask_non_prose() blanks YAML frontmatter, HTML
comments, fenced code blocks, inline code, Markdown link targets, URLs
and HTML tags while preserving character positions and newlines, so
colons/semicolons in code or metadata never fail.

A colon that directly introduces quoted dialogue (他说：“……”, She said: "…")
is dialogue-unit framing (rule §4), not prose — exempt in both languages.

Usage: import prose_global_rules (library module, no CLI).
Exit codes: n/a.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ---------------------------------------------------------------- masking

_FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^)\n]*\)")
_URL = re.compile(r"https?://[^\s)>]+")
_HTML_TAG = re.compile(r"<[^>\n]+>")


def mask_non_prose(text: str) -> str:
    """Blank frontmatter, HTML comments, code, links, URLs, HTML tags.

    Replacement preserves string length and newlines, so character
    positions and line numbers stay valid for downstream checks.
    """

    def _mask(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group())

    masked = text
    for pattern in (
        _FRONTMATTER,
        _HTML_COMMENT,
        _FENCED_CODE,
        _INLINE_CODE,
        _LINK_TARGET,
        _URL,
        _HTML_TAG,
    ):
        masked = pattern.sub(_mask, masked)
    return masked


# ---------------------------------------------------------------- hard rules

# A colon that directly introduces quoted dialogue is dialogue-unit
# framing (global rule §4), not prose — exempt in both languages.
COLON_RE = re.compile(r"[:：](?!\s*[\"“])")
SEMICOLON_RE = re.compile(r"[;；]")


def find_colons(text: str) -> list[int]:
    """Start positions of prose colons (ASCII ":" + full-width "：")."""
    return [match.start() for match in COLON_RE.finditer(text)]


def find_semicolons(text: str) -> list[int]:
    """Start positions of prose semicolons (ASCII ";" + full-width "；")."""
    return [match.start() for match in SEMICOLON_RE.finditer(text)]


# ---------------------------------------------------------------- dialogue

_ASCII_QUOTE_PAIR = re.compile(r'"[^"\n]*"')
_CJK_QUOTE_PAIR = re.compile(r"“[^”\n]*”")

_EN_ATTRIBUTION = re.compile(
    r"\b(said|asked|replied|whispered|shouted|murmured|answered|added|continued"
    r"|called|told)\b\s+([A-Za-z']+)|([A-Za-z']+)\s+"
    r"\b(said|asked|replied|whispered|shouted|murmured|answered|added|continued"
    r"|called|told)\b",
    re.IGNORECASE)
_EN_PRONOUNS = {"he", "she", "they", "it", "we", "you", "i"}

_CJK_SPEECH_VERBS = (
    "低声说道", "轻声说道", "说道", "问道", "答道", "喊道", "叫道", "笑道",
    "叹道", "喝道", "吼道", "冷笑", "苦笑", "低语", "喃喃",
    "说", "道", "问", "答", "喊", "叫",
)
_CJK_ATTRIBUTION = re.compile(
    r"([\u4e00-\u9fff]{1,4})(?:"
    + "|".join(sorted(_CJK_SPEECH_VERBS, key=len, reverse=True))
    + r")(?=[，。：、”\"'\n]|$)"
)
_CJK_PRONOUNS = {"他", "她", "它", "我", "你", "他们", "她们", "它们", "我们", "你们"}
# Verb-looking matches that are really 知道/听说 (to know / to have heard).
_CJK_VERB_NOISE = ("知道", "听说")


def _looks_like_speech(match: re.Match[str]) -> bool:
    """Quoted terms/excerpts ("sheet 4", "within tolerance.") are not dialogue.
    Convention: real dialogue starts capitalized."""
    inner = match.group()[1:-1]
    found = re.search(r"[A-Za-z]", inner)
    return found is not None and found.group().isupper()


def _blank(match: re.Match[str]) -> str:
    return " " * len(match.group())


@dataclass
class DialogueViolation:
    """kind: "speakers" (detail "a, b"), "no_signal", or "too_many" (detail "3")."""

    kind: str
    detail: str = ""


def dialogue_violation(text: str) -> DialogueViolation | None:
    """One paragraph = one contiguous dialogue unit. Returns violation or None.

    Handles ASCII ("...") and CJK (“...”) quotes. An interrupted single
    speech ('"X," she said, "Y."') is one unit. Violations: two distinct
    speakers, two quoted segments with no speaker signal at all, or 3+
    quoted segments.
    """
    ascii_pairs = [
        match for match in _ASCII_QUOTE_PAIR.finditer(text)
        if _looks_like_speech(match)
    ]
    cjk_pairs = list(_CJK_QUOTE_PAIR.finditer(text))
    pairs = sorted(ascii_pairs + cjk_pairs, key=lambda match: match.start())
    if len(pairs) < 2:
        return None
    if len(pairs) > 2:
        return DialogueViolation("too_many", str(len(pairs)))
    unquoted = _CJK_QUOTE_PAIR.sub(_blank, _ASCII_QUOTE_PAIR.sub(_blank, text))
    named: set[str] = set()
    pro: set[str] = set()
    for match in _EN_ATTRIBUTION.finditer(unquoted):
        speaker = (match.group(2) or match.group(3) or "").lower()
        if not speaker:
            continue
        (pro if speaker in _EN_PRONOUNS else named).add(speaker)
    for match in _CJK_ATTRIBUTION.finditer(unquoted):
        if match.group(0).endswith(_CJK_VERB_NOISE):
            continue
        speaker = match.group(1)
        (pro if speaker in _CJK_PRONOUNS else named).add(speaker)
    bridge = text[pairs[0].end():pairs[1].start()]
    pro.update(
        word.lower()
        for word in re.findall(r"\b(he|she|they|i|we|you)\b", bridge, re.IGNORECASE)
    )
    pro.update(re.findall(r"[他她它]", bridge))
    persons = set(named)
    if not named:
        persons = set(pro)
    elif len(named) == 1:
        pass  # pronouns absorbed by the lone named speaker
    else:
        persons = set(named) | set(pro)
    if len(persons) >= 2:
        return DialogueViolation("speakers", ", ".join(sorted(persons)))
    if not persons:
        return DialogueViolation("no_signal")
    return None


# ---------------------------------------------------------------- soft

EM_DASH_RE = re.compile(r"[—–]")


def count_em_dashes(text: str) -> int:
    """Count em/en dash characters in (masked) text. Warning-only metric."""
    return sum(1 for _ in EM_DASH_RE.finditer(text))
