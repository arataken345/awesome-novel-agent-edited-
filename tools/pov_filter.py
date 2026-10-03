#!/usr/bin/env python3
"""Deterministic POV narrative filter assembly.

Implements the §45 filter contract: given a narrator profile (§43 fields)
and a cognitive state (§5 fields), assemble the 16-field POV narrative
filter as pure structure. No prose is generated here — the
narrator-voice-agent refines qualitative fields; this tool guarantees the
contract shape and the rule-precedence logic.

Also implements rule resolution per the global-rules hierarchy (§48/§54):
an explicitly declared narrower-scope rule wins; overrides are never
inferred.

Usage:
    python3 tools/pov_filter.py --profile profile.json --state state.json
    python3 tools/pov_filter.py --self-test
Exit codes: 0 = ok, 2 = read/usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- constants

# §45 filter output fields, in contract order.
FILTER_FIELDS = (
    "WHAT_TO_NOTICE",
    "WHAT_TO_PRIORITIZE",
    "WHAT_TO_IGNORE",
    "WHAT_TO_AVOID_EXPLAINING",
    "WHAT_THE_CHARACTER_THINKS_IT_MEANS",
    "WHAT_THE_CHARACTER_DOES_NOT_KNOW",
    "WHAT_MAY_BE_MISINTERPRETED",
    "WHAT_ASSOCIATIONS_ARE_NATURAL",
    "EMOTIONAL_FRAMING",
    "DESCRIPTION_DENSITY",
    "SENSORY_PRIORITY",
    "CERTAINTY_LEVEL",
    "NARRATIVE_DISTANCE",
    "FAMILIARITY_COMPRESSION",
    "SOCIAL_PERCEPTION",
    "CURRENT_COGNITIVE_DISTRACTIONS",
)

# §48 hierarchy, highest first. §55 source priority folds in: user_explicit
# outranks everything; observed_style never outranks an explicit instruction.
PRECEDENCE = (
    "user_explicit",     # explicit user command (any scope)
    "user_global",       # user global rule
    "project_canon",     # locked canon
    "chapter",           # chapter-level rule
    "scene",             # scene-level rule
    "character",         # character-level rule
    "observed_style",    # learned tendency (soft only)
    "agent_default",     # agent/framework default
    "model_default",     # base model habit (lowest)
)


def _get(mapping: dict, *keys, default=None):
    for key in keys:
        if isinstance(mapping, dict) and key in mapping:
            return mapping[key]
    return default


def build_filter(profile: dict, cognitive_state: dict) -> dict:
    """Assemble the §45 filter from profile + cognitive state.

    Both arguments are plain dicts; missing fields are tolerated (§43: do
    not require every field). Returns an ordered dict with the 16 contract
    fields. Values are data (lists/strings), never prose.
    """
    profile = profile or {}
    state = cognitive_state or {}
    attention = state.get("attention") or {}

    def att(level: str) -> list:
        items = attention.get(level) or attention.get(level.lower()) or []
        return list(items) if isinstance(items, list) else [items]

    primary = att("PRIMARY")
    secondary = att("SECONDARY")
    ignored = att("IGNORED") + att("ACTIVELY_AVOIDED")

    salience = state.get("salience_map") or []
    high_salience = [e.get("element") for e in salience
                     if isinstance(e, dict)
                     and str(e.get("character_salience", "")).upper() == "HIGH"
                     and e.get("element")]
    # Description density: familiar elements compress; primary attention expands.
    familiarity = state.get("familiarity") or []
    familiar = familiarity if isinstance(familiarity, list) else [familiarity]
    density = {
        "expand": primary,
        "compress": [f for f in familiar if f],
        "note": ("Familiar elements compress; primary-attention elements may "
                 "expand. Never expand by story importance alone."),
    }

    # Emotional framing honors the character's self-awareness level: the
    # narration presents what the character recognizes, not the raw truth.
    emo_state = state.get("emotional_state") or "unspecified"
    awareness = str(state.get("emotional_awareness") or "recognize").lower()
    emo_vocab = profile.get("emotional_vocabulary") or []
    if awareness in ("recognize", "recognised"):
        framing = f"May name the feeling directly: {emo_state}."
    elif awareness in ("vague", "vaguely_sense"):
        framing = (f"Sense without naming: something is off around "
                   f"{emo_state}; keep it unnamed.")
    elif awareness in ("mislabeled", "mislabel"):
        framing = (f"Present the mislabel, not the truth: the character "
                   f"experiences {emo_state} as "
                   f"{', '.join(emo_vocab) if emo_vocab else 'something else'}."
                   f" Never correct it in narration.")
    elif awareness in ("bodily", "bodily_only", "somatic"):
        framing = (f"Body only: render {emo_state} through physical symptoms "
                   f"(tension, breath, jaw, hands). No emotion words.")
    elif awareness in ("denied", "deny", "rationalized", "rationalize"):
        framing = (f"The character denies/rationalizes {emo_state}; narration "
                   f"may show the strain of the denial, never the named feeling.")
    else:
        framing = f"Emotional awareness level '{awareness}': render {emo_state} accordingly; do not upgrade awareness."

    return {
        "WHAT_TO_NOTICE": primary + secondary,
        "WHAT_TO_PRIORITIZE": primary + [h for h in high_salience
                                         if h not in primary],
        "WHAT_TO_IGNORE": ignored,
        "WHAT_TO_AVOID_EXPLAINING": list(state.get("blind_spots") or []) + [
            f"Causal explanation for: {u}" for u in (state.get("unknown_facts") or [])],
        "WHAT_THE_CHARACTER_THINKS_IT_MEANS": list(state.get("interpretations") or []),
        "WHAT_THE_CHARACTER_DOES_NOT_KNOW": list(state.get("unknown_facts") or []),
        "WHAT_MAY_BE_MISINTERPRETED": list(state.get("misinterpretations") or []) + list(
            profile.get("characteristic_misinterpretations") or []),
        "WHAT_ASSOCIATIONS_ARE_NATURAL": list(state.get("associations") or []) + list(
            profile.get("association_patterns") or []),
        "EMOTIONAL_FRAMING": framing,
        "DESCRIPTION_DENSITY": density,
        "SENSORY_PRIORITY": list(profile.get("sensory_priorities") or []),
        "CERTAINTY_LEVEL": profile.get("certainty_tolerance") or "mark uncertainty explicitly",
        "NARRATIVE_DISTANCE": profile.get("narrative_distance") or "moderately_close",
        "FAMILIARITY_COMPRESSION": {
            "familiar": [f for f in familiar if f],
            "patterns": list(profile.get("familiarity_compression") or []),
        },
        "SOCIAL_PERCEPTION": {
            "assumptions": list(state.get("social_assumptions") or []),
            "habits": profile.get("social_perception") or "",
        },
        "CURRENT_COGNITIVE_DISTRACTIONS": list(state.get("current_distractions") or []) + list(
            state.get("cognitive_noise") or []),
    }


# Scope specificity for explicit user overrides (§54): narrower wins.
SCOPE_SPECIFICITY = ("scene", "chapter", "character", "user_global",
                     "project_canon")


def resolve_rule(rules: list[dict], name: str):
    """Resolve which rule wins for `name` per §48/§54.

    Each rule: {name, source, value, explicit, by_user}. Resolution:
      1. an explicit direct user command (source=user_explicit) wins outright;
      2. an explicit USER override at a narrower scope wins (§54: the user
         saying "this chapter may use colons" beats the global "no colons");
      3. otherwise the §48 default source order applies.
    An override applies only when explicitly declared (explicit=True) —
    overrides are never inferred. Returns the winning rule dict, or None.
    """
    candidates = [r for r in (rules or [])
                  if isinstance(r, dict) and r.get("name") == name]
    if not candidates:
        return None

    def rank(rule: dict) -> tuple:
        source = str(rule.get("source") or rule.get("scope") or "agent_default")
        explicit = bool(rule.get("explicit"))
        by_user = bool(rule.get("by_user"))
        if source == "user_explicit" and explicit:
            return (0,)  # direct command: absolute top (§48)
        if explicit and by_user:
            try:
                spec = SCOPE_SPECIFICITY.index(source)
            except ValueError:
                spec = len(SCOPE_SPECIFICITY)
            return (1, spec)  # §54: narrower explicit user scope wins
        try:
            base = PRECEDENCE.index(source)
        except ValueError:
            base = len(PRECEDENCE)
        # Explicit system rules sort before non-explicit ones, but a
        # non-explicit rule never overrides an explicit user rule (§54).
        return (2 if explicit else 3, base)

    return sorted(candidates, key=rank)[0]


def _self_test() -> int:
    profile_a = {
        "sensory_priorities": ["sound", "touch"],
        "metaphor_tendencies": ["machinery"],
        "emotional_vocabulary": ["annoyed"],
        "narrative_distance": "close",
        "certainty_tolerance": "low",
        "characteristic_misinterpretations": ["reads concern as criticism"],
    }
    profile_b = {
        "sensory_priorities": ["sight"],
        "metaphor_tendencies": ["clothing", "fabric"],
        "emotional_vocabulary": ["irritated"],
        "narrative_distance": "distant",
        "certainty_tolerance": "high",
        "characteristic_misinterpretations": ["reads silence as agreement"],
    }
    state = {
        "attention": {"PRIMARY": ["the engine hum"],
                      "IGNORED": ["the wallpaper"]},
        "unknown_facts": ["who sent the letter"],
        "interpretations": ["the smile was mocking"],
        "misinterpretations": [],
        "blind_spots": ["own jealousy"],
        "associations": ["childhood garage"],
        "familiarity": ["the workshop"],
        "emotional_state": "jealousy",
        "emotional_awareness": "mislabeled",
        "current_distractions": ["unpaid bill"],
        "cognitive_noise": ["headache"],
        "salience_map": [{"element": "the letter", "story_importance": "HIGH",
                          "character_salience": "LOW"}],
    }
    fa = build_filter(profile_a, state)
    fb = build_filter(profile_b, state)
    assert set(fa) == set(FILTER_FIELDS), "filter contract fields"
    assert fa["WHAT_TO_NOTICE"] != fb["WHAT_TO_NOTICE"] or \
        fa["SENSORY_PRIORITY"] != fb["SENSORY_PRIORITY"], "profiles differ"
    assert "annoyed" in fa["EMOTIONAL_FRAMING"], "mislabel honored"
    assert "mocking" in str(fa["WHAT_THE_CHARACTER_THINKS_IT_MEANS"])
    # Rule precedence: explicit user chapter override beats global (§54).
    rules = [
        {"name": "colon", "source": "user_global", "value": "forbidden",
         "explicit": True, "by_user": True},
        {"name": "colon", "source": "chapter", "value": "allowed",
         "explicit": True, "by_user": True},
    ]
    assert resolve_rule(rules, "colon")["value"] == "allowed"
    # Non-explicit never overrides (never inferred).
    rules2 = [
        {"name": "colon", "source": "user_global", "value": "forbidden",
         "explicit": True, "by_user": True},
        {"name": "colon", "source": "chapter", "value": "allowed",
         "explicit": False, "by_user": True},
    ]
    assert resolve_rule(rules2, "colon")["value"] == "forbidden"
    # Explicit user command beats everything (§48 top).
    rules3 = [
        {"name": "colon", "source": "chapter", "value": "allowed",
         "explicit": True, "by_user": True},
        {"name": "colon", "source": "user_explicit", "value": "forbidden",
         "explicit": True, "by_user": True},
    ]
    assert resolve_rule(rules3, "colon")["value"] == "forbidden"
    print("pov_filter self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble a deterministic POV narrative filter (§45).")
    parser.add_argument("--profile", help="JSON narrator profile (§43 fields)")
    parser.add_argument("--state", help="JSON cognitive state (§5 fields)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return _self_test()
    if not args.profile or not args.state:
        print("need --profile and --state, or --self-test", file=sys.stderr)
        return 2
    try:
        profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"cannot read input: {error}", file=sys.stderr)
        return 2
    print(json.dumps(build_filter(profile, state), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
