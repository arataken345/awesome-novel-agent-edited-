#!/usr/bin/env python3
"""Doctrine-hardening regression tests: closed-POV epistemic invariant,
salience/importance separation, sparse-injection ceiling,
cognitive-behavior authenticity, Gate B7 hedge protection, and
prompt-level knowledge-quarantine guards.

Phase coverage: Phase 2 (closed POV) / Phase 3 (filter safety) /
Phase 4 (sparse injection) / Phase 5 (behavior authenticity) /
Gate B7 fix / prompt-crafting leak guards / docs extension.
Read-only w.r.t. tools/pov_filter.py — the filter is exercised,
never modified.

Usage: python tools/test_cognition_hardening.py
Returns 0 on all pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_util import check, summary, exit_code, load_module

CHECK_EN = load_module(
    "check_prose_en_mod", Path(__file__).resolve().parent / "check-prose-en.py"
)
POV_FILTER = load_module(
    "pov_filter_mod", Path(__file__).resolve().parent / "pov_filter.py"
)

ROOT = Path(__file__).resolve().parent.parent


def read_repo(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def epistemic_warnings(result) -> list:
    return [w for w in result.warnings
            if "head-hop" in w or "foreshadowing" in w]


# ------------------------------------------------- Phase 2: closed POV

def test_invariant_text_exists():
    text = read_repo("knowledge/narrator-voice/distance-modulation.md")
    check("CLOSED_POV_EPISTEMIC_INVARIANT section present",
          "CLOSED_POV_EPISTEMIC_INVARIANT" in text)
    check("invariant: distance NEVER controls epistemic permissions",
          "NEVER epistemic permissions" in text)
    check("invariant names the forbidden assertions",
          "hidden thoughts" in text and "future significance" in text
          and "hidden causes" in text)


def test_distant_voice_inside_pov_knowledge_no_epistemic_warning():
    # Distant voice (compressed, cool), but everything asserted is
    # POV-observable or hedged — inside the POV's epistemic permissions.
    text = ("Arlen surveyed the courtyard from the balcony, with the patience "
            "of a man who had nothing better to do. The fountain stood dry. "
            "A servant crossed the square with his head down. It seemed to "
            "Arlen that the man was in a hurry, though he could not have said why.")
    result = CHECK_EN.check_text(text, pov="Arlen")
    check("distant voice inside POV knowledge: no failures", not result.failures)
    check("distant voice inside POV knowledge: no epistemic warnings",
          not epistemic_warnings(result), "; ".join(result.warnings))


def test_distant_voice_mind_reading_warns():
    # Same distant voice, but asserts another character's hidden interiority:
    # an epistemic-permission violation at any distance.
    text = ("Arlen surveyed the courtyard from the balcony. Mara knew he was "
            "lying about the letter. The fountain stood dry.")
    result = CHECK_EN.check_text(text, pov="Arlen")
    check("distant voice + other-character interiority warns",
          any("head-hop" in w for w in result.warnings),
          "; ".join(result.warnings))
    check("mind-reading warns, never hard-fails", not result.failures)


# ------------------------------------------------- Phase 3: filter safety

def _salience_state():
    return {
        "attention": {"PRIMARY": ["the stain"], "SECONDARY": []},
        "salience_map": [
            {"element": "the vault code",
             "story_importance": "HIGH", "character_salience": "LOW"},
            {"element": "the stain",
             "story_importance": "LOW", "character_salience": "HIGH"},
        ],
        "familiarity": [],
    }


def test_prioritize_follows_character_salience_not_story_importance():
    f = POV_FILTER.build_filter({}, _salience_state())
    check("HIGH character_salience element is prioritized",
          "the stain" in f["WHAT_TO_PRIORITIZE"])
    check("HIGH story_importance / LOW salience element is NOT prioritized",
          "the vault code" not in f["WHAT_TO_PRIORITIZE"],
          str(f["WHAT_TO_PRIORITIZE"]))


def test_description_density_never_expands_by_story_importance():
    f = POV_FILTER.build_filter({}, _salience_state())
    density = f["DESCRIPTION_DENSITY"]
    check("story-important but unattended element never expanded",
          "the vault code" not in density["expand"], str(density["expand"]))
    check("density contract states the invariant",
          "Never expand by story importance alone" in density["note"])


# ------------------------------------------------- Phase 4: sparse injection

def test_sparse_filter_rule_formalized():
    text = read_repo("skills/prompt-crafting.md")
    check("SPARSE_FILTER_RULE formalized", "SPARSE_FILTER_RULE" in text)
    check("5 is a ceiling, never a quota",
          "ceiling" in text and "quota" in text)
    check("inject-only-what-matters example present",
          "WHAT_TO_NOTICE" in text and "凑满" in text)


def check_sparse_ceiling(constraints) -> bool:
    """Ceiling validator for sparse injection: 0..5 constraints allowed.

    5 is a ceiling, never a quota — fewer is always legal.
    """
    return 0 <= len(constraints) <= 5


def test_sparse_ceiling_validator():
    check("6 constraints fail the ceiling",
          not check_sparse_ceiling([f"c{i}" for i in range(6)]))
    check("5 constraints pass", check_sparse_ceiling([f"c{i}" for i in range(5)]))
    check("3 constraints pass without requiring 5",
          check_sparse_ceiling(["notice", "ignore", "framing"]))
    check("0 constraints pass (nothing load-bearing)", check_sparse_ceiling([]))


# ------------------------------------------------- Phase 5: behavior authenticity

PROHIBIT_LIST = (
    "typos",
    "grammatical mistakes",
    "arbitrary fragments",
    "random contradictions",
    "random memory errors",
    "random topic shifts",
    "random repetition",
    "random ambiguity",
    "fake uncertainty",
)


def test_authenticity_rule_formalized():
    text = read_repo("knowledge/cognition/narrative-restraint.md")
    check("COGNITIVE_BEHAVIOR_AUTHENTICITY formalized",
          "COGNITIVE_BEHAVIOR_AUTHENTICITY" in text)
    check("model cognition, not defects", "Model cognition, not defects" in text)
    check("behaviors require cognitive support",
          "No cognitive support" in text)


def test_prohibit_list_present():
    text = read_repo("knowledge/cognition/narrative-restraint.md")
    for item in PROHIBIT_LIST:
        check(f"prohibit list contains: {item}", item in text)


def test_cognition_agent_no_random_humanization_strengthened():
    text = read_repo("agents/cognition-agent.md")
    check("cognition-agent §4 names typos", "typos" in text)
    check("cognition-agent §4 names unresolved uncertainty",
          "genuinely unresolved" in text)


def test_build_filter_never_invents_behavior_fields():
    # Deterministic, read-only: absent state fields must not materialize
    # as filter content.
    f = POV_FILTER.build_filter({}, {"attention": {}})
    check("no invented distractions",
          f["CURRENT_COGNITIVE_DISTRACTIONS"] == [])
    check("no invented associations",
          f["WHAT_ASSOCIATIONS_ARE_NATURAL"] == [])
    check("no invented misinterpretations",
          f["WHAT_MAY_BE_MISINTERPRETED"] == [])
    check("no invented unknown facts",
          f["WHAT_THE_CHARACTER_DOES_NOT_KNOW"] == [])
    check("no invented avoid-explaining entries",
          f["WHAT_TO_AVOID_EXPLAINING"] == [])


# ------------------------------------------------- Gate B7: hedge protection

def test_hedge_protection_entry_exists():
    text = read_repo("knowledge/anti-ai/hedge-protection.md")
    check("hedge-protection guard entry exists", "误杀防护" in text)
    check("hedging is epistemic-layer mandated", "epistemic-layers" in text)
    check("never upgrade hedged perception to fact",
          "升级" in text and "事实" in text)
    check("protected pattern classes listed (CN + EN)",
          "似乎" in text and "seemed" in text)


# ------------------------------------------------- Prompt leak guards

def test_information_asymmetry_pov_guard():
    text = read_repo("skills/prompt-crafting.md")
    check("信息差 POV-side guard present",
          "POV 侧过滤" in text and "lattice" in text)
    check("hidden side redacted, never named",
          "涂黑" in text and "永不具名" in text)


def test_registry_never_injected():
    text = read_repo("skills/prompt-crafting.md")
    check("registry entries never enter writer prompts",
          "unresolved-registry" in text and "永远不注入" in text)


def test_prompt_audit_knowledge_quarantine_dimension():
    text = read_repo("skills/prompt-audit.md")
    check("knowledge-quarantine dimension J present",
          "维度 J" in text and "知识隔离" in text)
    check("hidden story truth quarantined", "HIDDEN FORCES" in text)
    check("registry entries quarantined", "registry" in text.lower())
    check("dimension J is a FAIL trigger",
          "B/E/F/G/J" in text)


# ------------------------------------------------- Docs extension

def test_docs_extended():
    text = read_repo("docs/human-cognition-architecture.md")
    check("docs A: distance = presentation, not epistemic access",
          "## 23." in text and "presentation, not epistemic access" in text)
    check("docs B: sparse 0-5, ceiling not quota",
          "## 24." in text and "ceiling, not a quota" in text)
    check("docs C: behaviors only when cognitively motivated",
          "## 25." in text and "Model cognition, not defects" in text)
    check("docs E: benchmark = behavioral differentiation",
          "## 26." in text and "behavioral" in text.lower())
    check("existing sections untouched (1-22 intact)",
          "## 1." in text and "## 22." in text)


TESTS = [v for k, v in sorted(globals().items())
         if k.startswith("test_") and callable(v)]

if __name__ == "__main__":
    print("test_cognition_hardening.py")
    for test in TESTS:
        test()
    print(f"\n{summary()}")
    sys.exit(exit_code())
