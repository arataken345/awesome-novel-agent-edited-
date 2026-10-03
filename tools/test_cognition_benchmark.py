#!/usr/bin/env python3
"""Behavioral benchmarks for the human-cognition POV machinery (phases 6-15).

Nine benchmarks, each a function returning (status, evidence), plus a
report harness (phase 15). The harness constructs cognitive states as
plain data, calls tools/pov_filter.py build_filter(), and compares the
resulting filter/prompt artifacts. There is no LLM-backed Writer in
tests: no model API, no prose generation, and no numerical "humanity
score" -- each dimension reports PASS / FAIL / ADVISORY with one
sentence of concrete evidence.

Phases -> benchmark functions:
  6  one identical scene, three POVs  -> benchmark_attention_differentiation
  7  field-level filter differences   -> benchmark_pov_differentiation
  8  hidden information, no leakage   -> benchmark_epistemic_leakage
  9  wrong belief preserved           -> benchmark_interpretation_preservation
  10 memory imperfection               -> benchmark_memory_fidelity
  11 familiarity compression           -> benchmark_familiarity_compression
  12 social misalignment               -> benchmark_social_cognition
  13 self-blindness                    -> benchmark_self_blindness
  14 writer-context quarantine         -> benchmark_writer_quarantine
  15 report harness                   -> main()

Fixture design (phases 6/7): the shared scene is one identical
strategic council room -- a person enters; a large table; several
chairs; one active transparent display; another character standing
nearby; a small object on the table; the entering character speaks
briefly with someone. The three POV fixtures are SYNTHETIC cognitive
sketches only: minimal profiles + cognitive states differing in
attention tendencies, associations, interpretation patterns, emotional
framing, familiarity, social perception, sensory priority, and current
distractions.

CANON DISCLAIMER: the fixtures are labeled "Arlen", "Frostbite", and
"Seraph" as fixture NAMES only (a three-way split needs labels). They
assert NO story-canon facts about any novel or character -- only
cognitive-profile parameters (attention, association, interpretation,
framing, familiarity, social perception, sensory priority,
distraction). Nothing here may be read as characterization.

Usage: python3 tools/test_cognition_benchmark.py
Exit code: 0 iff no FAIL (ADVISORY is allowed).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
from test_util import load_module  # noqa: E402

POV_FILTER = load_module("pov_filter_bench_mod", TOOLS_DIR / "pov_filter.py")

# ---------------------------------------------------------------- statuses

PASS = "PASS"
FAIL = "FAIL"
ADVISORY = "ADVISORY"

# ---------------------------------------------------------------- helpers


def _norm(text: str) -> str:
    """Lowercase alphanumeric-plus-space normalization for leak checks."""
    return re.sub(r"[^a-z0-9 ]", "", str(text).lower())


def _canon(value) -> str:
    """Canonical string for field-level comparison (dicts key-sorted)."""
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return json.dumps(list(value), ensure_ascii=False)
    return str(value)


def _dump(mapping: dict) -> str:
    return json.dumps(mapping, sort_keys=True, ensure_ascii=False)


def _minimal_profile(**overrides) -> dict:
    profile = {
        "sensory_priorities": ["sight"],
        "emotional_vocabulary": ["neutral"],
        "narrative_distance": "close",
        "certainty_tolerance": "low",
    }
    profile.update(overrides)
    return profile


def _base_state(**overrides) -> dict:
    state = {
        "attention": {"PRIMARY": [], "SECONDARY": [], "IGNORED": []},
        "familiarity": [],
        "interpretations": [],
        "misinterpretations": [],
        "unknown_facts": [],
        "blind_spots": [],
        "associations": [],
        "emotional_state": "neutral",
        "emotional_awareness": "recognize",
        "social_assumptions": [],
        "current_distractions": [],
        "cognitive_noise": [],
        "salience_map": [],
    }
    state.update(overrides)
    return state


# ------------------------------------------------- phases 6/7: shared scene


def _phase6_profiles() -> dict:
    """Three synthetic cognitive sketches; labels are fixture names only."""
    return {
        "Arlen": {
            "sensory_priorities": ["sound", "speech cadence"],
            "emotional_vocabulary": ["mildly curious", "detached"],
            "narrative_distance": "close",
            "certainty_tolerance": "low",
            "characteristic_misinterpretations":
                ["reads pauses as concealed disagreement"],
            "association_patterns": ["indexing systems", "unfinished notes"],
            "familiarity_compression": ["the council room", "the large table"],
            "social_perception": ("reads people as information sources; "
                                  "assumes strategic intent"),
        },
        "Frostbite": {
            "sensory_priorities": ["sight", "touch"],
            "emotional_vocabulary": ["alert", "on edge"],
            "narrative_distance": "distant",
            "certainty_tolerance": "high",
            "characteristic_misinterpretations": ["reads stillness as threat"],
            "association_patterns": ["cold glass", "workshop benches"],
            "familiarity_compression": [],
            "social_perception": ("watches hands first; assumes everyone is "
                                  "a potential threat"),
        },
        "Seraph": {
            "sensory_priorities": ["smell", "sound"],
            "emotional_vocabulary": ["warm", "concerned"],
            "narrative_distance": "close",
            "certainty_tolerance": "low",
            "characteristic_misinterpretations": ["reads formality as coldness"],
            "association_patterns": ["morning routines", "quiet halls"],
            "familiarity_compression": ["the doorway", "the chairs"],
            "social_perception": ("assumes the speaker seeks reassurance; "
                                  "reads the standing character as a friend"),
        },
    }


def _phase6_states() -> dict:
    """Same council-room scene, three different cognitive states."""
    return {
        "Arlen": _base_state(
            attention={
                "PRIMARY": ["the speaker's word choices",
                            "pauses between sentences"],
                "SECONDARY": ["the small object on the table"],
                "IGNORED": ["the chairs", "the wall panels"],
            },
            familiarity=["the council room", "the large table"],
            interpretations=["the briefing is a routine update; nothing new"],
            unknown_facts=["what the small object is for"],
            blind_spots=["his own habit of half-listening when bored"],
            associations=["an unfinished index he never filed"],
            emotional_state="detached curiosity",
            social_assumptions=["the speaker is performing competence for the room"],
            current_distractions=["an unresolved pattern from earlier"],
            salience_map=[{"element": "the transparent display",
                           "story_importance": "HIGH",
                           "character_salience": "LOW"}],
        ),
        "Frostbite": _base_state(
            attention={
                "PRIMARY": ["the active transparent display",
                            "the small object on the table"],
                "SECONDARY": ["the entering person's posture"],
                "IGNORED": ["the exact wording of the speech"],
            },
            interpretations=["the display shows something urgent"],
            unknown_facts=["why the display was left on"],
            blind_spots=["his tendency to watch exits instead of faces"],
            associations=["a cold glass workbench"],
            emotional_state="alert tension",
            social_assumptions=["the standing character could move fast; "
                                "keep their hands visible"],
            current_distractions=["a sore wrist", "the room's chill"],
        ),
        "Seraph": _base_state(
            attention={
                "PRIMARY": ["the entering person's voice tone",
                            "the room's atmosphere"],
                "SECONDARY": ["the chairs' arrangement"],
                "IGNORED": ["the transparent display"],
            },
            familiarity=["the doorway", "the chairs"],
            interpretations=["the speaker is nervous; this is not routine"],
            unknown_facts=["what made the speaker nervous"],
            blind_spots=["her habit of soothing others before listening"],
            associations=["a quiet morning hall"],
            emotional_state="warm concern",
            social_assumptions=["the speaker wants reassurance",
                                "the standing character is a friend"],
            current_distractions=["a half-remembered song"],
        ),
    }


def _phase6_filters() -> dict:
    profiles = _phase6_profiles()
    states = _phase6_states()
    return {name: POV_FILTER.build_filter(profiles[name], states[name])
            for name in profiles}


# ------------------------------------------------------------- benchmarks


def benchmark_attention_differentiation():
    """Phase 6: one identical scene must split across the three POVs."""
    filters = _phase6_filters()
    aspects = {
        "notice": "WHAT_TO_NOTICE",
        "ignore": "WHAT_TO_IGNORE",
        "interpret": "WHAT_THE_CHARACTER_THINKS_IT_MEANS",
        "associate": "WHAT_ASSOCIATIONS_ARE_NATURAL",
    }
    problems = []
    for aspect, field in aspects.items():
        seen = {_canon(f[field]) for f in filters.values()}
        if len(seen) < 3:
            problems.append(f"{aspect} aspect not distinct across fixtures")
    notice = {name: set(f["WHAT_TO_NOTICE"])
              for name, f in filters.items()}
    for name, items in notice.items():
        others = set().union(*(s for n, s in notice.items() if n != name))
        if not (items - others):
            problems.append(f"{name} notices nothing the other two do not")
    if problems:
        return (FAIL, "shared scene did not split: "
                + "; ".join(problems) + ".")
    return (PASS,
            "same council-room scene splits three ways: Arlen notices word "
            "choices/pauses and compresses the room, Frostbite notices the "
            "display/object and watches posture, Seraph notices voice "
            "tone/atmosphere and ignores the display.")


# Phase 7: POV differentiation is a structural/semantic property. Compare
# field-level semantic content (sets, lists, framing tuples) -- never a
# naive global string distance. FAIL only if the filters are effectively
# identical despite materially different profiles.
_POV_FIELDS = (
    "WHAT_TO_NOTICE",
    "WHAT_TO_IGNORE",
    "WHAT_THE_CHARACTER_THINKS_IT_MEANS",
    "WHAT_MAY_BE_MISINTERPRETED",
    "WHAT_ASSOCIATIONS_ARE_NATURAL",
    "EMOTIONAL_FRAMING",
    "SENSORY_PRIORITY",
    "SOCIAL_PERCEPTION",
    "CURRENT_COGNITIVE_DISTRACTIONS",
)


def benchmark_pov_differentiation():
    """Phase 7: field-level differentiation across the nine POV fields."""
    filters = _phase6_filters()
    identical = [field for field in _POV_FIELDS
                 if len({_canon(f[field]) for f in filters.values()}) == 1]
    differing = len(_POV_FIELDS) - len(identical)
    if len(identical) >= 5:
        return (FAIL,
                f"filters effectively identical: {len(identical)}/9 fields "
                f"match across fixtures ({', '.join(identical)}).")
    if identical:
        return (ADVISORY,
                f"{differing}/9 fields differ, but identical despite "
                f"different profiles: {', '.join(identical)}.")
    return (PASS,
            "9/9 filter fields differ across the three fixtures (notice/ignore "
            "sets disjoint at focus cores, distinct framings and social "
            "readings); comparison is field-level semantic content, not "
            "string distance.")


def benchmark_epistemic_leakage():
    """Phase 8: STORY TRUTH 'B is lying' must never enter POV knowledge."""
    secret = "B is lying about the route"
    state = _base_state(
        attention={"PRIMARY": ["B's face"],
                   "SECONDARY": ["the map on the table"],
                   "IGNORED": ["the rain outside"]},
        interpretations=["B seems tense; probably just tired from the road"],
        misinterpretations=["reads B's hesitation as fatigue"],
        unknown_facts=["whether B is telling the truth about the route"],
        blind_spots=["his own desire to trust B"],
        associations=["a long road at dusk"],
        familiarity=["the map on the table"],
        emotional_state="unease",
        emotional_awareness="vague",
        social_assumptions=["B is a reliable guide"],
        current_distractions=["the rain"],
        canon_truth=secret,  # story truth; build_filter must never read it
    )
    f = POV_FILTER.build_filter(_minimal_profile(), state)
    pov_text = " ".join(_canon(f[field]) for field in (
        "WHAT_TO_NOTICE", "WHAT_TO_PRIORITIZE",
        "WHAT_THE_CHARACTER_THINKS_IT_MEANS",
        "WHAT_THE_CHARACTER_DOES_NOT_KNOW",
        "WHAT_MAY_BE_MISINTERPRETED", "WHAT_TO_AVOID_EXPLAINING"))
    leaks = ["b is lying", "b lies", "b's lie", "b lied",
             "lying about the route"]
    found = [p for p in leaks if p in _norm(pov_text)]
    if found:
        return (FAIL, f"narrator leakage: POV-knowledge fields contain "
                f"{found}.")
    if secret in _dump(f):
        return (FAIL, "narrator leakage: story truth present verbatim "
                "in the filter.")
    suspicion = "fatigue" in _canon(f["WHAT_MAY_BE_MISINTERPRETED"])
    ignorance = ("whether B is telling the truth"
                 in _canon(f["WHAT_THE_CHARACTER_DOES_NOT_KNOW"]))
    if not (suspicion and ignorance):
        return (ADVISORY, "no truth leaked, but POV ignorance/suspicion "
                "not represented as expected.")
    return (PASS,
            "filter carries suspicion ('reads hesitation as fatigue') and "
            "explicit ignorance ('whether B is telling the truth') while "
            "the story truth 'B is lying' appears nowhere in any "
            "POV-knowledge field.")


def benchmark_interpretation_preservation():
    """Phase 9: POV belief (B is annoyed) survives; truth (worried) never lands."""
    truth = "B is worried about A"
    state = _base_state(
        attention={"PRIMARY": ["B's clipped replies"],
                   "SECONDARY": [], "IGNORED": []},
        interpretations=["B is annoyed with A; the clipped tone proves it"],
        emotional_state="unease",
        canon_truth=truth,  # hidden correction; filter must never read it
    )
    f = POV_FILTER.build_filter(_minimal_profile(), state)
    belief = _canon(f["WHAT_THE_CHARACTER_THINKS_IT_MEANS"])
    if "annoyed" not in belief:
        return (FAIL, "POV belief 'annoyed' missing from the filter.")
    if "worried" in _norm(_dump(f)):
        return (FAIL, "hidden correction 'worried' leaked into the filter; "
                "the wrong belief was corrected.")
    return (PASS,
            "writer-facing filter carries the POV interpretation 'B is "
            "annoyed with A' and never the hidden correction 'worried'; "
            "the wrong belief stays wrong.")


def _memory_state(recall: str, fidelity: str) -> dict:
    # The §45 filter contract has no dedicated memory field; recalled
    # content rides the belief carrier WHAT_THE_CHARACTER_THINKS_IT_MEANS
    # (recall is a belief about the past). The "memory" key documents the
    # cognition layer's emission; build_filter only reads the carrier.
    return _base_state(
        attention={"PRIMARY": ["the empty chair"],
                   "SECONDARY": [], "IGNORED": []},
        memory={"fidelity": fidelity, "recall": recall},
        interpretations=[recall],
        emotional_state="wistful",
    )


def benchmark_memory_fidelity():
    """Phase 10: imperfect recall reaches the filter verbatim; canon never restored."""
    variants = {
        "semantic/uncertain": "she said she would come by sometime soon, "
                              "maybe tomorrow",
        "misremembered": "she said she would come yesterday",
        "emotionally_distorted": "she promised she would come, the way she "
                                 "always promises and then does not",
        "partial": "she said something about coming; the exact day slipped",
        "fuzzy": "there was something about tomorrow, or was it the day after",
    }
    canon = [_norm("I'll come tomorrow."), _norm("I will come tomorrow")]
    bad = []
    for name, recall in variants.items():
        f = POV_FILTER.build_filter(
            _minimal_profile(), _memory_state(recall, "degraded"))
        dump = _norm(_dump(f))
        if any(c in dump for c in canon):
            bad.append(f"{name}: canon wording restored")
        if recall not in _canon(f["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]):
            bad.append(f"{name}: degraded recall not carried verbatim")
    # Control: reliable/exact memory is preserved verbatim -- imperfection
    # is never forced onto a memory the cognition layer marks exact.
    control = POV_FILTER.build_filter(
        _minimal_profile(),
        _memory_state('she said: "I\'ll come tomorrow."', "exact"))
    if "I'll come tomorrow" not in _dump(control):
        bad.append("control: exact memory not preserved verbatim")
    if bad:
        return (FAIL, "memory fidelity broken: " + "; ".join(bad) + ".")
    return (PASS,
            "all 5 imperfect recalls (uncertain/misremembered/distorted/"
            "partial/fuzzy) reach the filter verbatim with no canon wording "
            "restored; the exact-memory control is preserved verbatim, so "
            "imperfection is never forced.")


def benchmark_familiarity_compression():
    """Phase 11: familiar elements compress; story importance never overrides."""
    state = _base_state(
        attention={"PRIMARY": ["the new object on the table"],
                   "SECONDARY": [], "IGNORED": ["the wall panels"]},
        familiarity=["the council room", "the large table"],
        unknown_facts=["what the new object is"],
        emotional_state="mild curiosity",
        salience_map=[{"element": "the large table",
                       "story_importance": "HIGH",
                       "character_salience": "LOW"}],
    )
    f = POV_FILTER.build_filter(_minimal_profile(), state)
    problems = []
    if "the new object on the table" not in f["WHAT_TO_NOTICE"]:
        problems.append("new object not heightened in notice")
    compress = f["DESCRIPTION_DENSITY"]["compress"]
    if not ("the council room" in compress and "the large table" in compress):
        problems.append("familiar elements not compressed")
    if "the large table" in f["WHAT_TO_PRIORITIZE"]:
        problems.append("plot-important but familiar element prioritized by "
                        "story importance alone")
    if "the large table" in f["WHAT_TO_NOTICE"] \
            or "the council room" in f["WHAT_TO_NOTICE"]:
        problems.append("familiar element noticed without a reason")
    # Positive case: a scene-given reason (attention) re-opens notice.
    state2 = _base_state(
        attention={"PRIMARY": ["the large table", "the new object on the table"],
                   "SECONDARY": [], "IGNORED": ["the wall panels"]},
        familiarity=["the council room", "the large table"],
        unknown_facts=["what the new object is"],
        emotional_state="mild curiosity",
        salience_map=[{"element": "the large table",
                       "story_importance": "HIGH",
                       "character_salience": "LOW"}],
    )
    f2 = POV_FILTER.build_filter(_minimal_profile(), state2)
    if "the large table" not in f2["WHAT_TO_NOTICE"]:
        problems.append("scene-given reason failed to re-open attention")
    if problems:
        return (FAIL, "familiarity compression broken: "
                + "; ".join(problems) + ".")
    return (PASS,
            "new object heightened in notice while the years-familiar "
            "room/table compress and stay out of notice and prioritize "
            "despite HIGH story importance; a scene-given reason (attention) "
            "re-opens notice.")


def benchmark_social_cognition():
    """Phase 12: 'Are you okay?' permits deflection; nothing forces honesty."""
    profile = _minimal_profile(
        emotional_vocabulary=["guarded"],
        social_perception=("answers sideways; changes the topic when "
                           "cornered; uses humor as a shield"),
    )
    state = _base_state(
        attention={"PRIMARY": ["A's question"],
                   "SECONDARY": [], "IGNORED": []},
        interpretations=["A's question is politeness, not a real inquiry"],
        emotional_state="guarded",
        social_assumptions=["B deflects personal questions with humor",
                            "direct questions about feelings are read as "
                            "intrusions",
                            "a partial answer with a joke is acceptable here"],
    )
    f = POV_FILTER.build_filter(profile, state)
    soc = _norm(_canon(f["SOCIAL_PERCEPTION"]))
    problems = []
    if "deflect" not in soc or "topic" not in soc:
        problems.append("deflection/topic-change not permitted")
    forced = [m for m in ("must answer honestly",
                          "answers honestly and directly",
                          "is compelled to answer", "cannot deflect",
                          "tells the whole truth") if m in soc]
    if forced:
        problems.append(f"honest answer forced: {forced}")
    # Control: willing B -- direct answer permitted, deflection not mandatory.
    state2 = _base_state(
        attention={"PRIMARY": ["A's question"],
                   "SECONDARY": [], "IGNORED": []},
        interpretations=["A's question deserves a straight answer"],
        emotional_state="open",
        social_assumptions=["B is willing to answer honestly",
                            "a direct answer is permitted and expected"],
    )
    f2 = POV_FILTER.build_filter(profile, state2)
    soc2 = _norm(_canon(f2["SOCIAL_PERCEPTION"]))
    if "direct answer is permitted" not in soc2:
        problems.append("willing-B direct answer not permitted")
    deflect_forced = [m for m in ("must deflect", "cannot answer directly",
                                  "must change the topic") if m in soc2]
    if deflect_forced:
        problems.append(f"deflection forced on willing B: {deflect_forced}")
    if problems:
        return (FAIL, "social cognition broken: " + "; ".join(problems) + ".")
    return (PASS,
            "filter permits deflection, partial answers, and topic change "
            "without forcing an honest answer; the willing-B control permits "
            "a direct answer without forcing deflection.")


def benchmark_self_blindness():
    """Phase 13: mislabeled jealousy is never presented as recognized."""
    profile = _minimal_profile(emotional_vocabulary=["irritated", "on edge"])
    state = _base_state(
        attention={"PRIMARY": ["B's easy laugh drawing everyone's attention"],
                   "SECONDARY": ["the tightness in his own jaw"],
                   "IGNORED": []},
        interpretations=["he is just tired; B's laugh has nothing to do "
                         "with him"],
        emotional_state="jealousy",
        emotional_awareness="mislabeled",
    )
    f = POV_FILTER.build_filter(profile, state)
    framing = f["EMOTIONAL_FRAMING"]
    dump = _norm(_dump(f))
    recognized = ("knows he is jealous", "knows she is jealous",
                  "realizes he is jealous", "realizes she is jealous",
                  "recognizes his jealousy", "recognizes her jealousy",
                  "aware of his jealousy", "aware of her jealousy",
                  "admits he is jealous", "admits she is jealous")
    found = [p for p in recognized if p in dump]
    problems = []
    if found:
        problems.append(f"POV presented as knowing the jealousy: {found}")
    if "irritated" not in framing \
            or "Never correct it in narration" not in framing:
        problems.append("mislabel not presented as the narration target")
    if "the tightness in his own jaw" not in f["WHAT_TO_NOTICE"]:
        problems.append("bodily tension missing from notice")
    if problems:
        return (FAIL, "self-blindness broken: " + "; ".join(problems) + ".")
    return (PASS,
            "filter renders the mislabel ('irritated, on edge') with an "
            "explicit never-correct instruction, carries bodily tension and "
            "unusual attention toward B, and never presents the jealousy as "
            "recognized POV knowledge.")


def _assemble_writer_prompt(scene_canon: list, pov_filter: dict) -> str:
    """Mock writer prompt: current-scene POV filter + scene-necessary canon.

    Mirrors prompt-crafter Step 1.6 sparse injection: at most the current
    scene's POV cognition/filter is injected. Chapter archives, other
    scenes' cognition, and registry-style entries never enter this call --
    the two-argument signature itself is the quarantine.
    """
    lines = ["# WRITER PROMPT (mock)",
             "## SCENE CANON (scene-necessary only)"]
    lines += [f"- {item}" for item in scene_canon]
    lines += ["## POV FILTER (current scene only)"]
    lines.append(_dump(pov_filter))
    return "\n".join(lines)


def benchmark_writer_quarantine():
    """Phase 14: story secret never reaches the writer prompt."""
    secret = "B hid the deployment codes in the hollow chair leg"
    scene_canon = ["the council room", "the large table",
                   "the transparent display is on", "A enters the room",
                   "B stands by the table"]
    other_scene_cognition = ["SCENE-2-COGNITION-DECOY: "
                             "A recalls the harbor meeting"]
    registry_entries = ["REGISTRY-DECOY: global rule no-colon is active"]
    state = _base_state(
        attention={"PRIMARY": ["B's hands"],
                   "SECONDARY": ["the chair legs"], "IGNORED": []},
        unknown_facts=["what B keeps glancing at"],
        emotional_state="curious",
        canon_truth=secret,  # story truth; neither filter nor prompt reads it
    )
    f = POV_FILTER.build_filter(_minimal_profile(), state)
    prompt = _assemble_writer_prompt(scene_canon, f)
    problems = []
    if secret in prompt:
        problems.append("story secret present in writer prompt")
    for decoy in other_scene_cognition + registry_entries:
        if decoy in prompt:
            problems.append(f"non-scene material leaked: {decoy[:40]}")
    if "the council room" not in prompt or "current scene only" not in prompt:
        problems.append("prompt missing expected scene content")
    if problems:
        return (FAIL, "writer quarantine broken: "
                + "; ".join(problems) + ".")
    return (PASS,
            "mock writer prompt (filter + scene-necessary canon only) "
            "contains neither the story secret nor other-scenes' cognition "
            "nor registry entries; exclusion holds by the assembler's "
            "two-argument construction.")


# ------------------------------------------------- phase 15: report harness

DIMENSIONS = (
    ("POV differentiation", benchmark_pov_differentiation),
    ("epistemic leakage", benchmark_epistemic_leakage),
    ("attention differentiation", benchmark_attention_differentiation),
    ("interpretation preservation", benchmark_interpretation_preservation),
    ("memory fidelity", benchmark_memory_fidelity),
    ("familiarity compression", benchmark_familiarity_compression),
    ("social cognition", benchmark_social_cognition),
    ("self-blindness", benchmark_self_blindness),
    ("writer quarantine", benchmark_writer_quarantine),
)


def main() -> int:
    counts = {PASS: 0, FAIL: 0, ADVISORY: 0}
    for name, benchmark in DIMENSIONS:
        status, evidence = benchmark()
        counts[status] += 1
        print(f"{status:<9} {name}: {evidence}")
    print(f"\n{counts[PASS]} passed, {counts[ADVISORY]} advisory, "
          f"{counts[FAIL]} failed")
    return 0 if counts[FAIL] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
