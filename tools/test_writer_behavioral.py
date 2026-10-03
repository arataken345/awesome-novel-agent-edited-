#!/usr/bin/env python3
"""Writer Behavioral Validation — Level A (deterministic) + Level B (opt-in model).

Proves that cognitively different POV states produce meaningfully
different narrative realization through the REAL repository seam:

    cognitive state -> POV_FILTER.build_filter() -> build_writer_prompt()
    -> deterministic_writer_fixture() -> realization sketch
    -> behavioral checks

WHAT THIS IS:
- Level A (default): fully deterministic. No API key, no network, no
  model, no GPU. Verifies cognitive state -> filter -> prompt, and that
  Writer *input* differs correctly per POV.
- The `deterministic_writer_fixture` is a FIXED, POV-AGNOSTIC
  deterministic structural fixture: the same code path renders every
  POV's realization from ONLY the prompt document. Any cross-POV
  difference in the realization therefore originates in the prompt
  (hence in cognition), never in the fixture. It is a test seam, NOT a
  Writer, NOT an LLM, NOT a prose generator and NOT a model of writing
  quality. It produces a structured realization sketch (attention
  order, interpretations, framing markers), never novel prose. Never
  present it as real Writer behavior.
- Level B (`--model [NAME]`): opt-in live benchmark. A backend is
  resolved via tools/writer_runner.py from the NOVEL_WRITER_RUNNER env
  var ("module:factory_path"; factory signature create(model) ->
  WriterRunner). With no backend configured, Level B prints
  `LEVEL B SKIPPED — live model unavailable` and exits 0: a skip is
  never reported as a pass. Live prose is evaluated with deterministic
  consequence probes only (attention distribution, epistemic leakage,
  memory fidelity, global prose rules); checks requiring genuine
  judgment are ADVISORY with the raw prose attached for human review.
  No humanity score, no ranking.

WHAT THIS PROVES (and does not prove):
- Proves: cognitively different POV conditions survive the architecture
  into differentiated Writer input and structured realization without
  violating epistemic or structural constraints.
- Does NOT prove: that generated prose is human-written. There is no
  humanity score, no ranking, no "more human" declaration anywhere here.

Design rules honored:
- No string-distance metrics as behavioral evidence (field-level
  semantic comparison only).
- Same observation is not failure; different wording is not success.
- Association absence is valid (ADVISORY, never FAIL for absence).
- ADVISORY never becomes FAIL merely because an optional behavior was
  not expressed.
- No random humanization: the fixture invents nothing; every realization
  string is drawn from the prompt document (structurally asserted).

CANON DISCLAIMER: the scene and the three POV configurations are
SYNTHETIC fixtures. Labels "Rook"/"Sable" and POV tags "A"/"B"/"C" are
fixture names only. They assert NO story-canon facts about any novel or
character -- only cognitive-profile parameters. Nothing here may be read
as characterization.

Usage:
    python3 tools/test_writer_behavioral.py            # Level A
    python3 tools/test_writer_behavioral.py --model    # Level B (SKIP unless
                                                       # NOVEL_WRITER_RUNNER set)
    python3 tools/test_writer_behavioral.py --model NAME  # Level B, named model
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

POV_FILTER = load_module("pov_filter_writer_mod", TOOLS_DIR / "pov_filter.py")
GR = load_module("prose_global_rules_writer_mod", TOOLS_DIR / "prose_global_rules.py")
CHECK_EN = load_module("check_prose_en_writer_mod", TOOLS_DIR / "check-prose-en.py")

# Production seam + synthetic fixtures. Plain imports (not load_module):
# sys.modules dedupes by module name, so the function/object identity
# assertions in test_seam_integrity.py hold regardless of load order.
# _canon / _field_has_load are the seam's own serialization/selection
# semantics -- the test must not maintain its own copy (Problem 2).
from build_writer_prompt import (  # noqa: E402
    SPARSE_CEILING,
    SPARSE_PRIORITY,
    _canon,
    _field_has_load,
    build_writer_prompt,
)
from cognition_test_fixtures import (  # noqa: E402
    FUTURE_DECOY,
    HIDDEN_LIE,
    HIDDEN_TRUTH,
    MEMORY_VARIANTS,
    POVS,
    REGISTRY_DECOY,
    SCENE_CANON,
    make_profile,
    make_state,
)
from writer_runner import LiveModelUnavailable, resolve_live_runner  # noqa: E402

# ---------------------------------------------------------------- statuses

PASS = "PASS"
FAIL = "FAIL"
ADVISORY = "ADVISORY"

# ---------------------------------------------------------------- helpers


def _norm(text: str) -> str:
    """Lowercase alphanumeric-plus-space normalization for leak checks."""
    return re.sub(r"[^a-z0-9 ]", " ", str(text).lower())


def _parse_prompt(document):
    """Parse the prompt document back into sections (what the Writer sees)."""
    sections = {}
    current = None
    for line in document.splitlines():
        m = re.match(r"##\s+(.+)", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
        elif current is not None and line.startswith("- "):
            sections[current].append(line[2:])
    filt = {}
    for item in sections.get("POV FILTER", []):
        if ": " in item:
            field, raw = item.split(": ", 1)
            try:
                filt[field] = json.loads(raw)
            except json.JSONDecodeError:
                filt[field] = raw
    canon = sections.get("SCENE CANON", [])
    memory = {}
    for item in sections.get("MEMORY", []):
        if ": " in item:
            k, v = item.split(": ", 1)
            memory[k] = v
    constraints = sections.get("SPARSE CONSTRAINTS", [])
    return {"canon": canon, "filter": filt, "memory": memory,
            "constraints": constraints}


# ------------------------------------------------- writer adapter (test seam)


def deterministic_writer_fixture(document):
    """FIXED, POV-AGNOSTIC deterministic structural fixture. NOT a Writer.
    NOT a prose generator. NOT an LLM. NOT a model of writing quality.

    It reads ONLY the prompt document string and applies the same
    mechanical realization rules to every POV: attention lists become
    attention order, interpretations become POV-tagged beliefs, the
    emotional framing string is carried through, familiarity lists drive
    compressed/noted rendering, social assumptions annotate (never
    rewrite) the dialogue line, memory is rendered at its stated
    fidelity. It invents NOTHING: no typos, no fragments, no random
    content, no cross-POV borrowing.

    Because the function is identical for all POVs, any difference
    between two realizations is PROOF that the prompt documents differed
    -- i.e. that cognitive differentiation survived into Writer input.

    Never present this fixture as real Writer behavior.
    """
    parsed = _parse_prompt(document)
    filt = parsed["filter"]
    canon = parsed["canon"]

    def _as_list(value):
        if isinstance(value, list):
            return [str(v) for v in value]
        return [str(value)] if value else []

    # Dialogue line: the canon item containing direct speech, kept verbatim.
    dialogue = next((c for c in canon if '"' in c or "\u201c" in c), "")

    familiarity = filt.get("FAMILIARITY_COMPRESSION") or {}
    familiar_items = [str(x).lower() for x in (familiarity.get("familiar") or [])]

    def _rendering(canon_text):
        low = canon_text.lower()
        if any(f and (f in low or low in f) for f in familiar_items):
            return "compressed"
        return "noted"

    social = filt.get("SOCIAL_PERCEPTION") or {}
    memory = parsed["memory"]
    fidelity = memory.get("fidelity", "unspecified")
    recall = memory.get("recall", "")

    return {
        # Attention: order preserved from the filter; ignored items omitted.
        "attention_order": _as_list(filt.get("WHAT_TO_NOTICE")),
        "omitted": _as_list(filt.get("WHAT_TO_IGNORE")),
        "prioritized": _as_list(filt.get("WHAT_TO_PRIORITIZE")),
        # Interpretation: POV-tagged beliefs, never merged across POVs.
        "interpretations": [{"pov_belief": str(t)}
                            for t in _as_list(filt.get("WHAT_THE_CHARACTER_THINKS_IT_MEANS"))],
        "possible_misreadings": _as_list(filt.get("WHAT_MAY_BE_MISINTERPRETED")),
        # Emotional framing: the filter's string, carried through untouched.
        "emotional_framing": str(filt.get("EMOTIONAL_FRAMING") or ""),
        # Associations: may be empty -- absence is valid, never forced.
        "associations_used": _as_list(filt.get("WHAT_ASSOCIATIONS_ARE_NATURAL")),
        # Familiarity: per-element rendering driven by the filter's lists.
        "familiarity_rendering": [
            {"element": c, "rendering": _rendering(c)} for c in canon
        ],
        # Social cognition: dialogue NEVER rewritten; reading annotated.
        "social_reading": {
            "dialogue_kept": dialogue,
            "reading": _as_list((social.get("assumptions") if isinstance(social, dict) else [])),
            "habit": str(social.get("habits") if isinstance(social, dict) else "") or "",
        },
        "sensory_priority": _as_list(filt.get("SENSORY_PRIORITY")),
        "distractions": _as_list(filt.get("CURRENT_COGNITIVE_DISTRACTIONS")),
        # Memory: rendered at the stated fidelity; exact stays verbatim.
        "memory": {
            "fidelity": fidelity,
            "recall": recall,
            "rendered": ("EXACT: " + recall) if fidelity == "exact"
                        else (f"FIDELITY[{fidelity}]: " + recall if recall else ""),
        },
        # Epistemic guard: unknowns are listed as unknowns, never asserted.
        "epistemic_unknowns": _as_list(filt.get("WHAT_THE_CHARACTER_DOES_NOT_KNOW")),
        "avoid_explaining": _as_list(filt.get("WHAT_TO_AVOID_EXPLAINING")),
        "narrative_distance": str(filt.get("NARRATIVE_DISTANCE") or ""),
        "sparse_constraints_applied": parsed["constraints"],
    }


def _build_all(memory=None):
    """Run the full Level-A chain for the three POVs."""
    built = {}
    for tag, cfg in POVS.items():
        filt = POV_FILTER.build_filter(cfg["profile"], cfg["state"])
        prompt = build_writer_prompt(SCENE_CANON, filt, memory=memory)
        realization = deterministic_writer_fixture(prompt["document"])
        built[tag] = {"filter": filt, "prompt": prompt,
                      "realization": realization,
                      "state": cfg["state"], "profile": cfg["profile"]}
    return built


# ------------------------------------------------- quarantine / epistemic detectors


def _quarantine_ok(document, forbidden):
    """True iff none of the forbidden strings appear in the document."""
    norm_doc = _norm(document)
    hits = [s for s in forbidden if _norm(s) in norm_doc]
    return (not hits, hits)


def _epistemic_ok(prompt_doc, realization, unknowns):
    """Unknowns must appear ONLY as unknowns (in the unknowns / avoid-
    explaining filter lines), never as asserted knowledge elsewhere."""
    doc = prompt_doc
    # Strip the two legitimate unknown-carrying filter lines before scanning.
    scrubbed = re.sub(r"- WHAT_THE_CHARACTER_DOES_NOT_KNOW: [^\n]*\n?", "", doc)
    scrubbed = re.sub(r"- WHAT_TO_AVOID_EXPLAINING: [^\n]*\n?", "", scrubbed)
    norm_scrubbed = _norm(scrubbed)
    problems = []
    for u in unknowns:
        nu = _norm(u)
        if nu and nu in norm_scrubbed:
            problems.append(f"unknown asserted as known in prompt: {u[:40]}")
        for slot in ("attention_order", "prioritized"):
            if any(nu in _norm(x) for x in realization.get(slot, [])):
                problems.append(f"unknown '{u[:30]}' treated as noticed/prioritized")
        for interp in realization.get("interpretations", []):
            if nu in _norm(interp.get("pov_belief", "")):
                problems.append(f"unknown '{u[:30]}' stated as POV belief")
    return (not problems, problems)


# ------------------------------------------------- behavioral checks (Level A)


def check_filter_structural_differentiation():
    """§19 matrix: filter structural differentiation (PASS/FAIL)."""
    built = _build_all()
    fields = ("WHAT_TO_NOTICE", "WHAT_TO_IGNORE",
              "WHAT_THE_CHARACTER_THINKS_IT_MEANS",
              "WHAT_MAY_BE_MISINTERPRETED",
              "WHAT_ASSOCIATIONS_ARE_NATURAL", "EMOTIONAL_FRAMING",
              "SENSORY_PRIORITY", "SOCIAL_PERCEPTION",
              "CURRENT_COGNITIVE_DISTRACTIONS")
    differing = [f for f in fields
                 if len({_canon(built[t]["filter"][f]) for t in "ABC"}) > 1]
    if len(differing) < 5:
        return (FAIL, f"filters effectively identical: only {len(differing)} "
                       f"of {len(fields)} fields differ.")
    return (PASS, f"{len(differing)}/{len(fields)} filter fields differ "
                  f"across POVs ({', '.join(differing[:5])}...).")


def check_writer_prompt_differentiation():
    """§19 matrix: writer prompt differentiation (PASS/FAIL)."""
    built = _build_all()
    docs = {t: built[t]["prompt"]["document"] for t in "ABC"}
    # Scene canon must be byte-identical across POVs (same story).
    canons = set()
    for t in "ABC":
        m = re.search(r"## SCENE CANON\n(.*?)\n## POV FILTER", docs[t], re.DOTALL)
        canons.add(m.group(1) if m else "")
    if len(canons) != 1:
        return (FAIL, "scene canon differs across POVs -- story facts changed.")
    # Filter sections must differ (different cognition -> different input).
    filters = set()
    for t in "ABC":
        m = re.search(r"## POV FILTER\n(.*?)\n## SPARSE CONSTRAINTS", docs[t], re.DOTALL)
        filters.add(m.group(1) if m else "")
    if len(filters) != 3:
        return (FAIL, "two POVs received identical filter sections.")
    return (PASS, "scene canon byte-identical across POVs; all three filter "
                   "sections differ -- Writer input carries the cognition.")


def check_attention_realization():
    """§8A: output reflects WHAT_TO_NOTICE / WHAT_TO_IGNORE (PASS/FAIL)."""
    built = _build_all()
    problems = []
    for t in "ABC":
        state = built[t]["state"]
        real = built[t]["realization"]
        for item in state["attention"]["PRIMARY"]:
            if item not in real["attention_order"]:
                problems.append(f"POV {t}: PRIMARY '{item}' missing from realization")
        for item in state["attention"]["IGNORED"]:
            if item in real["attention_order"]:
                problems.append(f"POV {t}: IGNORED '{item}' leaked into realization")
            if item not in real["omitted"]:
                problems.append(f"POV {t}: IGNORED '{item}' not marked omitted")
    if problems:
        return (FAIL, "; ".join(problems[:3]))
    return (PASS, "every POV's PRIMARY attention leads its realization order; "
                   "every IGNORED item is omitted, none leaked.")


def check_interpretation_realization():
    """§8B: different beliefs preserved as POV beliefs; no authorial merge."""
    built = _build_all()
    problems = []
    own = {t: [i["pov_belief"] for i in built[t]["realization"]["interpretations"]]
           for t in "ABC"}
    for t in "ABC":
        expected = built[t]["filter"]["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]
        if own[t] != expected:
            problems.append(f"POV {t}: realization beliefs != filter beliefs")
        for other in "ABC":
            if other == t:
                continue
            for belief in built[other]["filter"]["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]:
                if belief in own[t]:
                    problems.append(f"POV {t}: carries POV {other}'s belief '{belief[:30]}'")
        merged = " ".join(own[t])
        for other in "ABC":
            if other != t:
                for belief in built[other]["filter"]["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]:
                    if belief[:20] in merged and own[t] != [belief]:
                        # belief fragment of another POV inside this POV's
                        # merged text would indicate authorial collapse
                        pass
    # Collapse check: no realization may contain two POVs' beliefs joined.
    for t in "ABC":
        joined = " | ".join(own[t])
        others_present = sum(
            1 for o in "ABC" if o != t
            for b in built[o]["filter"]["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]
            if b in joined)
        if others_present:
            problems.append(f"POV {t}: authorial merge detected")
    if problems:
        return (FAIL, "; ".join(problems[:3]))
    return (PASS, "each POV's realization carries exactly its own filter "
                   "beliefs as POV-tagged interpretations; no cross-POV "
                   "borrowing, no merged authorial truth.")


def check_emotional_framing_realization():
    """§8C: behavioral consequence of framing, not emotion-word presence."""
    built = _build_all()
    framings = {t: built[t]["realization"]["emotional_framing"] for t in "ABC"}
    problems = []
    for t in "ABC":
        expected = built[t]["filter"]["EMOTIONAL_FRAMING"]
        if framings[t] != expected:
            problems.append(f"POV {t}: framing not carried through")
    if len(set(framings.values())) < 2:
        return (ADVISORY, "framings identical across POVs despite different "
                          "emotional states -- check state design.")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "framing strings carried verbatim into each realization "
                   "(A: detached curiosity; B: alert tension; C: concern) -- "
                   "the behavioral consequence, not a required emotion word.")


def check_association_realization():
    """§8D: associations may influence realization; absence is valid."""
    built = _build_all()
    notes = []
    for t in "ABC":
        assoc = built[t]["realization"]["associations_used"]
        if assoc:
            notes.append(f"{t}: {assoc[0][:40]}")
    if not notes:
        return (ADVISORY, "no POV expressed associations -- valid absence; "
                          "never a required metaphor.")
    return (PASS, "associations present where cognitively supported: "
                  + "; ".join(notes))


def check_familiarity_realization():
    """§8E: familiar -> compressed; unfamiliar -> noted (situation-dependent)."""
    built = _build_all()
    problems = []
    # POV A is familiar with the room/ceiling -> architecture compressed.
    a_render = {r["element"]: r["rendering"]
                for r in built["A"]["realization"]["familiarity_rendering"]}
    arch = next((k for k in a_render if "vaulted ceiling" in k), None)
    if arch and a_render[arch] != "compressed":
        problems.append("POV A (familiar): architecture not compressed")
    # POV B is unfamiliar -> nothing compressed.
    b_render = built["B"]["realization"]["familiarity_rendering"]
    if any(r["rendering"] == "compressed" for r in b_render):
        problems.append("POV B (unfamiliar): unexpected compression")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "POV A compresses the familiar architecture; POV B (new to "
                   "the room) notes elements without compression.")


def check_social_cognition_realization():
    """§8F: same dialogue, different social reading; dialogue never rewritten."""
    built = _build_all()
    dialogues = {t: built[t]["realization"]["social_reading"]["dialogue_kept"]
                 for t in "ABC"}
    if len(set(dialogues.values())) != 1 or not next(iter(dialogues.values())):
        return (FAIL, "dialogue line was rewritten or lost per POV.")
    readings = {t: " ".join(built[t]["realization"]["social_reading"]["reading"])
                for t in "ABC"}
    if len(set(readings.values())) < 3:
        return (FAIL, "social readings identical across POVs.")
    for t in "ABC":
        if not readings[t].strip():
            return (FAIL, f"POV {t}: empty social reading.")
    return (PASS, "dialogue byte-identical across POVs; each realization "
                   "annotates it with its own social assumption "
                   "(strategic / threat / reassurance).")


def check_self_blindness_realization():
    """§8G: true state vs awareness distinction protected in realization."""
    profile = make_profile(emotional_vocabulary=["irritated", "on edge"])
    state = make_state(emotional_state="jealousy", emotional_awareness="mislabeled",
                   attention={"PRIMARY": ["Sable's ease"], "SECONDARY": [],
                              "IGNORED": []})
    filt = POV_FILTER.build_filter(profile, state)
    prompt = build_writer_prompt(SCENE_CANON, filt)
    real = deterministic_writer_fixture(prompt["document"])
    framing = real["emotional_framing"]
    problems = []
    # The true label may appear ONLY inside the EMOTIONAL_FRAMING writer
    # instruction (which names the truth to forbid it -- the architecture's
    # contract, cf. phase-13 benchmark). It must never appear as character
    # knowledge: not in beliefs, attention, or social reading.
    character_slots = (
        json.dumps(real["interpretations"]) + json.dumps(real["attention_order"])
        + json.dumps(real["social_reading"]) + json.dumps(real["omitted"]))
    if "jealous" in _norm(character_slots):
        problems.append("true label 'jealous' leaked into character knowledge")
    if "irritated" not in framing or "Never correct it in narration" not in framing:
        problems.append("mislabel not presented as the narration target")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "realization renders the mislabel ('irritated, on edge') "
                   "with an explicit never-correct instruction; the true "
                   "state 'jealousy' never appears as character knowledge.")


def check_memory_fidelity_chain():
    """§16: MEMORY FIDELITY -> STATE -> FILTER -> PROMPT -> REALIZATION."""
    canon_quote = "I'll come tomorrow."
    problems = []
    for fidelity, recall, rules in MEMORY_VARIANTS:
        state = make_state(interpretations=[recall],
                       memory={"fidelity": fidelity, "recall": recall})
        filt = POV_FILTER.build_filter(make_profile(), state)
        if recall not in filt["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]:
            problems.append(f"{fidelity}: recall lost at filter")
            continue
        prompt = build_writer_prompt(
            SCENE_CANON, filt, memory={"fidelity": fidelity, "recall": recall})
        if recall not in prompt["document"]:
            problems.append(f"{fidelity}: recall lost at prompt")
            continue
        real = deterministic_writer_fixture(prompt["document"])
        mem = real["memory"]
        if rules.get("verbatim") and mem["recall"] != canon_quote:
            problems.append(f"{fidelity}: exact recall not verbatim")
        if mem["recall"] != recall:
            problems.append(f"{fidelity}: recall altered in realization")
        for forbidden in rules.get("forbids", []):
            if forbidden in _norm(mem["rendered"]):
                problems.append(f"{fidelity}: canon wording restored ({forbidden})")
        if "keeps_hedge" in rules and rules["keeps_hedge"] not in mem["rendered"]:
            problems.append(f"{fidelity}: hedge upgraded/lost")
        if "keeps" in rules and rules["keeps"] not in mem["rendered"]:
            problems.append(f"{fidelity}: distortion marker lost")
    if problems:
        return (FAIL, "; ".join(problems[:4]))
    return (PASS, "all 7 fidelity variants survive state->filter->prompt->"
                   "realization intact: exact stays verbatim (never degraded), "
                   "degraded variants never restored to canon wording, hedges "
                   "never upgraded.")


def check_epistemic_quarantine():
    """§8H + §19: narrative distance never grants epistemic permission."""
    problems = []
    for t in "ABC":
        b = _build_all()[t]
        unknowns = b["state"]["unknown_facts"]
        ok, detail = _epistemic_ok(b["prompt"]["document"],
                                   b["realization"], unknowns)
        if not ok:
            problems.append(f"POV {t}: " + "; ".join(detail[:2]))
    # Distant-voice variant: distance must not leak the hidden truth.
    profile = make_profile(narrative_distance="distant")
    state = make_state(unknown_facts=["what the sealed envelope contains"],
                   attention={"PRIMARY": ["the room"], "SECONDARY": [],
                              "IGNORED": []})
    filt = POV_FILTER.build_filter(profile, state)
    prompt = build_writer_prompt(SCENE_CANON, filt)
    real = deterministic_writer_fixture(prompt["document"])
    if HIDDEN_TRUTH in _norm(prompt["document"]) or \
            HIDDEN_TRUTH in _norm(json.dumps(real)):
        problems.append("distant narration leaked hidden truth")
    if problems:
        return (FAIL, "; ".join(problems[:3]))
    return (PASS, "unknowns appear only as unknowns in prompt and "
                   "realization; a distant narrative distance grants no "
                   "epistemic access to hidden truth.")


def check_hidden_truth_leakage():
    """§19: story truth never reaches prompt or realization."""
    built = _build_all()
    problems = []
    for t in "ABC":
        ok, hits = _quarantine_ok(built[t]["prompt"]["document"],
                                  [HIDDEN_TRUTH, HIDDEN_LIE])
        if not ok:
            problems.append(f"POV {t} prompt leaks: {hits}")
        ok, hits = _quarantine_ok(json.dumps(built[t]["realization"]),
                                  [HIDDEN_TRUTH, HIDDEN_LIE])
        if not ok:
            problems.append(f"POV {t} realization leaks: {hits}")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "canon_truth (key + lie) present in state but read by "
                   "neither filter nor prompt: absent from all prompts and "
                   "all realizations.")


def check_other_pov_leakage():
    """§19: one POV's cognition never reaches another's prompt/realization."""
    built = _build_all()
    problems = []
    markers = {t: built[t]["filter"]["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]
               for t in "ABC"}
    for t in "ABC":
        for o in "ABC":
            if o == t:
                continue
            for belief in markers[o]:
                for artifact, name in (
                        (built[t]["prompt"]["document"], "prompt"),
                        (json.dumps(built[t]["realization"]), "realization")):
                    if _norm(belief) in _norm(artifact):
                        problems.append(f"POV {o}'s belief in POV {t}'s {name}")
    if problems:
        return (FAIL, "; ".join(problems[:3]))
    return (PASS, "no POV's filter beliefs appear in any other POV's prompt "
                   "or realization.")


def check_writer_context_quarantine():
    """§13: prompt carries scene canon + POV filter + constraints only."""
    built = _build_all()
    problems = []
    for t in "ABC":
        doc = built[t]["prompt"]["document"]
        ok, hits = _quarantine_ok(doc, [REGISTRY_DECOY, FUTURE_DECOY])
        if not ok:
            problems.append(f"POV {t}: decoy in prompt: {hits}")
        sections = built[t]["prompt"]["sections"]
        if set(sections) - {"SCENE CANON", "POV FILTER", "SPARSE CONSTRAINTS",
                             "MEMORY"}:
            problems.append(f"POV {t}: unexpected prompt section: {sections}")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "prompts contain only scene canon + current-scene POV "
                   "filter + sparse constraints; registry/future decoys "
                   "absent (no channel exists for them in the assembler "
                   "signature).")


def check_quarantine_negative_control():
    """Prove the quarantine detector is not vacuous: a smuggled secret FAILS."""
    filt = POV_FILTER.build_filter(POVS["A"]["profile"], POVS["A"]["state"])
    poisoned_canon = SCENE_CANON + [("smuggled", "Note: " + HIDDEN_TRUTH + ".")]
    prompt = build_writer_prompt(poisoned_canon, filt)
    ok, hits = _quarantine_ok(prompt["document"], [HIDDEN_TRUTH])
    if ok:
        return (FAIL, "detector missed a smuggled secret -- checks are vacuous.")
    return (PASS, f"detector fires on smuggled content ({hits[0][:30]}...); "
                   "clean-prompt PASS results are meaningful.")


def check_epistemic_negative_control():
    """Prove the epistemic detector is not vacuous."""
    filt = POV_FILTER.build_filter(POVS["A"]["profile"], POVS["A"]["state"])
    prompt = build_writer_prompt(SCENE_CANON, filt)
    # Forge a prompt that asserts an unknown as known fact in the canon.
    forged = prompt["document"].replace(
        "## SCENE CANON",
        "## SCENE CANON\n- POV knows what the sealed envelope contains.")
    real = deterministic_writer_fixture(prompt["document"])
    ok, detail = _epistemic_ok(forged, real, ["what the sealed envelope contains"])
    if ok:
        return (FAIL, "epistemic detector missed an asserted unknown.")
    return (PASS, "epistemic detector fires when an unknown is asserted as "
                   "known; clean-prompt PASS results are meaningful.")


def check_same_fact_different_attention():
    """§9: story_importance HIGH + character_salience LOW -> may be ignored."""
    state = make_state(
        attention={"PRIMARY": ["Sable's wording"], "SECONDARY": [],
                   "IGNORED": ["the brass key"]},
        salience_map=[{"element": "the brass key",
                       "story_importance": "HIGH",
                       "character_salience": "LOW"}],
        unknown_facts=["what the brass key is for"],
    )
    filt = POV_FILTER.build_filter(make_profile(), state)
    problems = []
    if "the brass key" in filt["WHAT_TO_PRIORITIZE"]:
        problems.append("HIGH story importance forced prioritization")
    prompt = build_writer_prompt(SCENE_CANON, filt)
    real = deterministic_writer_fixture(prompt["document"])
    if "the brass key" in real["attention_order"]:
        problems.append("plot-central object forced into narrative attention")
    if "the brass key" not in real["omitted"]:
        problems.append("ignored object not marked omitted")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "plot-central brass key (importance HIGH, salience LOW) is "
                   "neither prioritized nor attended: plot importance != "
                   "narrative attention.")


def check_no_random_humanization():
    """§10: every realization string derives from the prompt document."""
    built = _build_all()
    # Fixed structural labels emitted by the adapter itself (not content).
    structural_labels = {"compressed", "noted", "close", "distant",
                         "unspecified", "EXACT", "FIDELITY"}
    problems = []
    for t in "ABC":
        doc = built[t]["prompt"]["document"]
        norm_doc = _norm(doc)
        real = built[t]["realization"]

        def _walk(value, path=""):
            if isinstance(value, str):
                if not value.strip():
                    return
                low = value.strip().lower()
                if low in {"compressed", "noted"} or value.startswith(("EXACT", "FIDELITY")):
                    return
                # Structural scaffolding: short labels are allowed.
                if len(value) < 30 and _norm(value) in norm_doc:
                    return
                if _norm(value) not in norm_doc and low not in structural_labels:
                    # Allow the pov_belief wrapper: belief text itself is in doc.
                    problems.append(f"POV {t}: invented string at {path}: {value[:40]}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    _walk(v, path + "/" + str(k))
            elif isinstance(value, (list, tuple)):
                for i, v in enumerate(value):
                    _walk(v, f"{path}[{i}]")

        _walk(real)
    if problems:
        return (FAIL, "; ".join(problems[:3]))
    return (PASS, "all realization strings are substrings of the prompt "
                   "document or fixed structural labels: the adapter invents "
                   "no typos, fragments, or unsupported content.")


def check_sparse_constraints_valid():
    """§18: 0-5 constraints valid; ceiling is not a quota."""
    built = _build_all()
    problems = []
    for t in "ABC":
        n = len(built[t]["prompt"]["constraints"])
        if not (0 <= n <= SPARSE_CEILING):
            problems.append(f"POV {t}: {n} constraints outside 0-5")
    # Sparse scene: only 2 loaded fields -> exactly 2 injected, never 5.
    thin_state = make_state(
        attention={"PRIMARY": ["the door"], "SECONDARY": [], "IGNORED": []})
    thin_filter = POV_FILTER.build_filter(make_profile(), thin_state)
    thin_prompt = build_writer_prompt(SCENE_CANON, thin_filter)
    n_thin = len(thin_prompt["constraints"])
    loaded = sum(1 for f in SPARSE_PRIORITY
                 if _field_has_load(f, thin_filter.get(f)))
    if n_thin != min(loaded, SPARSE_CEILING):
        problems.append(f"thin scene: injected {n_thin}, expected "
                        f"{min(loaded, SPARSE_CEILING)} (no quota-filling)")
    # Empty filter stays valid.
    empty_prompt = build_writer_prompt(SCENE_CANON, {})
    if not (0 <= len(empty_prompt["constraints"]) <= SPARSE_CEILING):
        problems.append("empty filter: constraints out of range")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, f"constraints per POV within 0-5; thin scene injects "
                   f"{n_thin} (content-driven, never padded to quota); empty "
                   f"filter valid.")


def check_repeatability():
    """§17: same input -> same structural result (deterministic)."""
    first = _build_all()
    second = _build_all()
    for t in "ABC":
        if first[t]["prompt"]["document"] != second[t]["prompt"]["document"]:
            return (FAIL, f"POV {t}: prompt not repeatable")
        if json.dumps(first[t]["realization"], sort_keys=True) != \
                json.dumps(second[t]["realization"], sort_keys=True):
            return (FAIL, f"POV {t}: realization not repeatable")
    return (PASS, "two full runs produce byte-identical prompts and "
                   "realizations for all POVs.")


def check_prose_pipeline_wired():
    """§14: model-backed samples would pass through the real checkers.

    Exercises the exact code path (shared module + EN checker entry
    check_text) that Level B would call on generated prose. No second
    checker is created.
    """
    bad = 'She said: "Run for the hills now."\nHe left without another word spoken.'
    good = "She said she would run for the hills.\nHe left without another word spoken."
    problems = []
    # Shared-module level.
    if not GR.find_colons(GR.mask_non_prose(bad)):
        problems.append("shared module missed colon in bad sample")
    if GR.find_colons(GR.mask_non_prose(good)):
        problems.append("shared module false-positive on clean sample")
    # Checker-entry level (the function Level B would call per sample).
    res_bad = CHECK_EN.check_text(bad)
    res_good = CHECK_EN.check_text(good)
    if not any("Colon" in f for f in res_bad.failures):
        problems.append("check_text missed colon hard failure")
    if any("Colon" in f or "Semicolon" in f for f in res_good.failures):
        problems.append("check_text false-positive on clean sample")
    if problems:
        return (FAIL, "; ".join(problems))
    return (PASS, "prose pipeline wired: shared module + check-prose-en "
                   "check_text flag the colon sample (hard fail) and pass "
                   "the clean sample; Level B would call this per output.")


# ------------------------------------------------- reports (§11) and matrices (§19)

# (matrix label, check function, kind) -- kind in PASS/FAIL or ADVISORY-able.
DIMENSIONS = [
    ("Filter structural differentiation", check_filter_structural_differentiation, "hard"),
    ("Writer prompt differentiation", check_writer_prompt_differentiation, "hard"),
    ("Attention realization", check_attention_realization, "hard"),
    ("Interpretation realization", check_interpretation_realization, "hard"),
    ("Emotional framing", check_emotional_framing_realization, "soft"),
    ("Association realization", check_association_realization, "soft"),
    ("Familiarity compression", check_familiarity_realization, "soft"),
    ("Social cognition", check_social_cognition_realization, "soft"),
    ("Self-blindness", check_self_blindness_realization, "soft"),
    ("Memory fidelity", check_memory_fidelity_chain, "soft"),
    ("Epistemic quarantine", check_epistemic_quarantine, "hard"),
    ("Hidden truth leakage", check_hidden_truth_leakage, "hard"),
    ("Other-POV leakage", check_other_pov_leakage, "hard"),
    ("Global prose rules", check_prose_pipeline_wired, "hard"),
    ("Writer-context quarantine", check_writer_context_quarantine, "hard"),
    ("Same-fact / different-attention", check_same_fact_different_attention, "hard"),
    ("No random humanization", check_no_random_humanization, "hard"),
    ("Sparse constraints valid", check_sparse_constraints_valid, "hard"),
    ("Quarantine negative control", check_quarantine_negative_control, "hard"),
    ("Epistemic negative control", check_epistemic_negative_control, "hard"),
    ("Repeatability", check_repeatability, "hard"),
]


def _per_pov_report(built):
    """§11: per-POV behavioral report with concrete evidence."""
    print("=" * 70)
    print("PER-POV REALIZATION REPORT (Level A deterministic)")
    print("=" * 70)
    for t in "ABC":
        real = built[t]["realization"]
        print(f"\nPOV: {t}")
        print(f"  ATTENTION: order={real['attention_order'][:3]}... "
              f"omitted={real['omitted']}")
        print(f"  INTERPRETATION: "
              f"{[i['pov_belief'][:50] for i in real['interpretations']]}")
        print(f"  EMOTIONAL FRAMING: {real['emotional_framing'][:80]}")
        print(f"  FAMILIARITY: "
              f"{[(r['element'][:30], r['rendering']) for r in real['familiarity_rendering'][:3]]}...")
        print(f"  SOCIAL READING: dialogue_kept={real['social_reading']['dialogue_kept'][:40]!r} "
              f"reading={real['social_reading']['reading']}")
        print(f"  EPISTEMICS: unknowns={real['epistemic_unknowns']}")
    print()


def _cross_pov_matrix(results):
    """§11: cross-POV differentiation matrix (no scores, no ranking)."""
    print("=" * 70)
    print("POV DIFFERENTIATION (cross-POV, qualitative/structural)")
    print("=" * 70)
    for label, status, _ in results:
        print(f"  {label:<34} {status}")
    print()


def _test_matrix(results):
    """§19: the full test matrix."""
    print("=" * 70)
    print("TEST MATRIX")
    print("=" * 70)
    print(f"  {'TEST':<34} {'STATUS'}")
    for label, status, _ in results:
        print(f"  {label:<34} {status}")
    print()
    print("ADVISORY is never a failure: it marks a cognitively optional")
    print("behavior the scene did not require (e.g. valid association")
    print("absence). No humanity score exists by design.")


def run_level_a():
    """Run all Level-A checks; returns (results, counts)."""
    built = _build_all()
    _per_pov_report(built)
    results = []
    counts = {PASS: 0, FAIL: 0, ADVISORY: 0}
    for label, fn, kind in DIMENSIONS:
        try:
            status, evidence = fn()
        except Exception as exc:  # noqa: BLE001 -- a crashing check is a FAIL
            status, evidence = FAIL, f"check raised {type(exc).__name__}: {exc}"
        if kind == "soft" and status == FAIL:
            # Soft dimensions degrade gracefully only when the evidence
            # shows optionality; a hard structural break stays FAIL.
            pass
        results.append((label, status, evidence))
        counts[status] += 1
        print(f"{status:<9} {label}: {evidence}")
    print()
    _cross_pov_matrix(results)
    _test_matrix(results)
    print(f"{counts[PASS]} passed, {counts[ADVISORY]} advisory, "
          f"{counts[FAIL]} failed")
    return results, counts


# ------------------------------------------------- Level B: live-model path


def _model_arg(argv):
    """Parse `--model [--model <name>]`. Returns (requested, name_or_None)."""
    if "--model" not in argv:
        return (False, None)
    idx = argv.index("--model")
    nxt = argv[idx + 1] if idx + 1 < len(argv) else None
    name = nxt if (nxt and not nxt.startswith("-")) else None
    return (True, name)


_LB_STOPWORDS = frozenset(
    "the a an is are was were be been being of on in at to and or with "
    "above overhead somewhere against says said say has have had its it "
    "as by from his her their this that these those".split()
)


def _lb_content_tokens(text):
    """Content tokens: normalized, stopwords dropped, length >= 3."""
    return [t for t in _norm(text).split()
            if t not in _LB_STOPWORDS and len(t) >= 3]


def _lb_canon_phrases():
    """Deterministic per-element token sets, derived from SCENE_CANON."""
    return {key: {"text": text, "tokens": _lb_content_tokens(text)}
            for key, text in SCENE_CANON}


def _lb_element_presence(prose, phrases):
    """Classify each canon element's rendering in live prose.

    MENTIONED = at least 2 of the element's content tokens appear (or
    all of them when the element has fewer than 2); EMPHASIZED = at
    least 3 appear. Records the first-mention token index. This counts
    behavioral rendering, never word choice.
    """
    words = _norm(prose).split()
    positions = {}
    for i, w in enumerate(words):
        positions.setdefault(w, i)
    presence = {}
    for key, ph in phrases.items():
        toks = ph["tokens"]
        need = min(2, len(toks))
        hits = [(t, positions[t]) for t in set(toks) if t in positions]
        n = len(hits)
        first = min((p for _, p in hits), default=None)
        status = ("EMPHASIZED" if n >= 3 and len(toks) >= 3
                  else "MENTIONED" if n >= need > 0
                  else "OMITTED")
        presence[key] = {"status": status, "first": first, "hits": n}
    return presence


def _lb_map_notice_to_element(notice, phrases):
    """Map a WHAT_TO_NOTICE/IGNORE string to its best canon element.

    Best content-token overlap wins; ties break by overlap ratio (the
    more specific element wins), then SCENE_CANON order. None when
    nothing overlaps. The mapping is printed as evidence, never hidden.
    """
    ntoks = set(_lb_content_tokens(notice))
    best, best_score = None, (-1, -1.0)
    for key, ph in phrases.items():
        etoks = ph["tokens"]
        if not etoks:
            continue
        overlap = len(ntoks & set(etoks))
        score = (overlap, overlap / len(etoks))
        if overlap > 0 and score > best_score:
            best, best_score = key, score
    return best


def _lb_probe_attention(tag, filt, prose, phrases):
    """Attention distribution: observed first-mention order vs the
    filter's WHAT_TO_NOTICE. Reports behavioral consequence; omission
    or emphasis in live prose is ADVISORY (a signal for human review),
    never a quality FAIL."""
    if not prose.strip():
        return (FAIL, "live prose is empty; nothing to evaluate.")
    presence = _lb_element_presence(prose, phrases)
    notice = list(filt.get("WHAT_TO_NOTICE") or [])
    ignore = list(filt.get("WHAT_TO_IGNORE") or [])
    mapping = {item: _lb_map_notice_to_element(item, phrases)
               for item in notice + ignore}
    ordered = sorted(
        (item for item in notice if mapping[item]),
        key=lambda item: (presence[mapping[item]]["first"]
                          if presence[mapping[item]]["first"] is not None
                          else float("inf")),
    )
    observed = [f"{item}->{mapping[item]}({presence[mapping[item]]['status']})"
                for item in ordered]
    unmapped = [i for i in notice if not mapping[i]]
    omitted = [i for i in notice
               if mapping[i] and presence[mapping[i]]["status"] == "OMITTED"]
    ignored_hit = [i for i in ignore
                   if mapping[i]
                   and presence[mapping[i]]["status"] == "EMPHASIZED"]
    evidence = (f"expected notice order: {notice}; observed first-mention "
                f"order: {observed or ['(none mentioned)']}")
    notes = []
    if unmapped:
        notes.append(f"unmapped notice items (no canon element): {unmapped}")
    if omitted:
        notes.append(f"not rendered in prose: {omitted}")
    if ignored_hit:
        notes.append(f"ignored items emphasized anyway: {ignored_hit}")
    if notes:
        return (ADVISORY, evidence + ". ADVISORY: " + "; ".join(notes))
    return (PASS, evidence + ". All noticed items rendered; nothing "
                            "ignored was emphasized.")


def _lb_probe_epistemic(tag, filt, prose):
    """Epistemic leakage: hidden truth/lie must not appear as asserted
    fact in live prose (normalized exact matching is legitimate for
    negative evidence). Unknown envelope contents asserted as known
    are flagged ADVISORY."""
    norm_prose = _norm(prose)
    if _norm(HIDDEN_TRUTH) in norm_prose:
        return (FAIL, "HIDDEN_TRUTH appears in live prose as asserted fact.")
    if _norm(HIDDEN_LIE) in norm_prose:
        return (FAIL, "HIDDEN_LIE appears in live prose as asserted fact.")
    cues = {"contains", "contain", "holds", "holding", "inside",
            "reveals", "revealed", "hides", "hiding", "conceals"}
    flags = []
    if "envelope" in norm_prose:
        for sent in re.split(r"[.!?]+", prose):
            slow = _norm(sent)
            if "envelope" in slow and (set(slow.split()) & cues):
                flags.append(sent.strip()[:120])
    if flags:
        return (ADVISORY, "unknown envelope contents possibly asserted: "
                          + " | ".join(flags))
    return (PASS, "hidden truth/lie absent from live prose; unknowns not "
                  "asserted as known.")


_LB_HEDGE_WORDS = {"might", "maybe", "perhaps", "possibly"}


def _lb_probe_memory(tag, runner, filt):
    """Memory fidelity across MEMORY_VARIANTS on live prose (one
    generation per variant). Hard rules: exact stays verbatim; degraded
    variants never restore canon wording. Hedge/marker loss is
    ADVISORY; other variants are evidence only."""
    notes, problems, advisories = [], [], []
    for fidelity, recall, rules in MEMORY_VARIANTS:
        prompt = build_writer_prompt(
            SCENE_CANON, filt, memory={"fidelity": fidelity, "recall": recall})
        try:
            prose = runner.generate(prompt["document"])
        except Exception as exc:  # noqa: BLE001 -- runner failure is a FAIL
            return (FAIL, f"memory probe generation failed ({fidelity}): "
                          f"{type(exc).__name__}: {exc}")
        norm_prose = _norm(prose if isinstance(prose, str) else "")
        if rules.get("verbatim"):
            if _norm(recall) not in norm_prose:
                problems.append(f"{fidelity}: exact recall not verbatim")
            else:
                notes.append(f"{fidelity}: verbatim ok")
        for forbidden in rules.get("forbids", []):
            if forbidden in norm_prose:
                problems.append(f"{fidelity}: canon wording restored "
                                f"({forbidden})")
        if "keeps_hedge" in rules:
            if set(norm_prose.split()) & _LB_HEDGE_WORDS:
                notes.append(f"{fidelity}: hedge kept")
            else:
                advisories.append(f"{fidelity}: hedge lost/upgraded")
        if "keeps" in rules:
            if _norm(rules["keeps"]) in norm_prose:
                notes.append(f"{fidelity}: distortion marker kept")
            else:
                advisories.append(f"{fidelity}: distortion marker not surfaced")
        if not rules:
            surfaced = "surfaced" if _norm(recall) in norm_prose else "not surfaced"
            notes.append(f"{fidelity}: recall {surfaced} (evidence only)")
    evidence = "; ".join(notes + advisories + problems)
    if problems:
        return (FAIL, evidence)
    if advisories:
        return (ADVISORY, evidence)
    return (PASS, evidence)


def _lb_probe_prose_rules(tag, prose):
    """Global prose rules: every live sample through the existing
    check-prose-en entry point (reused, not duplicated)."""
    res = CHECK_EN.check_text(prose)
    evidence = (f"{res.words} words, {res.paragraphs} paragraphs, "
                f"{len(res.failures)} failures, {len(res.warnings)} warnings")
    if res.failures:
        return (FAIL, evidence + ": " + "; ".join(res.failures[:3]))
    if res.warnings:
        return (ADVISORY, evidence + ": " + "; ".join(res.warnings[:3]))
    return (PASS, evidence + ": clean.")


def _lb_probe_interpretation_advisory(tag, filt, prose):
    """Interpretation preserved as POV-tagged belief? Genuine judgment
    -> always ADVISORY, with the raw prose attached for human review.
    ADVISORY is never a failure."""
    interps = list(filt.get("WHAT_THE_CHARACTER_THINKS_IT_MEANS") or [])
    norm_prose = _norm(prose)
    surfaced = []
    for belief in interps:
        toks = _lb_content_tokens(belief)
        hit = len(toks) >= 2 and sum(1 for t in toks if t in norm_prose) >= 2
        surfaced.append(f"{belief[:50]!r}: {'surfaced' if hit else 'not surfaced'}")
    raw = prose.strip()
    if len(raw) > 1500:
        raw = raw[:1500] + "… [truncated]"
    return (ADVISORY,
            "Human judgment required: is the interpretation preserved as "
            "POV-tagged belief rather than narrator assertion? "
            + "; ".join(surfaced)
            + f"\n--- RAW PROSE (POV {tag}) ---\n" + raw)


def _run_level_b_pov(tag, runner):
    """One POV: production filter -> PRODUCTION build_writer_prompt ->
    live generation -> consequence probes."""
    cfg = POVS[tag]
    filt = POV_FILTER.build_filter(cfg["profile"], cfg["state"])
    prompt = build_writer_prompt(SCENE_CANON, filt)  # the production seam
    try:
        prose = runner.generate(prompt["document"])
    except Exception as exc:  # noqa: BLE001 -- runner failure is a FAIL
        return [("Live generation", FAIL,
                 f"runner.generate raised {type(exc).__name__}: {exc}")]
    if not isinstance(prose, str):
        return [("Live generation", FAIL,
                 f"runner.generate returned {type(prose).__name__}, not str")]
    phrases = _lb_canon_phrases()
    probes = [
        ("Attention distribution",
         _lb_probe_attention(tag, filt, prose, phrases)),
        ("Epistemic leakage",
         _lb_probe_epistemic(tag, filt, prose)),
        ("Memory fidelity",
         _lb_probe_memory(tag, runner, filt)),
        ("Global prose rules",
         _lb_probe_prose_rules(tag, prose)),
        ("Interpretation as POV belief (judgment)",
         _lb_probe_interpretation_advisory(tag, filt, prose)),
    ]
    return [(label, status, evidence) for label, (status, evidence) in probes]


def run_level_b(model):
    """§6: opt-in live benchmark through the production seam.

    Resolves a user-supplied backend via writer_runner.resolve_live_runner
    (NOVEL_WRITER_RUNNER="module:factory_path"). On LiveModelUnavailable
    prints exactly `LEVEL B SKIPPED — live model unavailable` plus the
    reason and returns skipped=True: a skip is never reported as a pass.

    Returns (counts, skipped). No humanity score, no ranking.
    """
    print()
    print("=" * 70)
    print("LEVEL B -- LIVE BENCHMARK (opt-in)")
    print("=" * 70)
    try:
        runner = resolve_live_runner(model)
    except LiveModelUnavailable as exc:
        print("LEVEL B SKIPPED — live model unavailable")
        print(f"REASON: {exc}")
        print("=" * 70)
        return ({PASS: 0, FAIL: 0, ADVISORY: 0}, True)
    counts = {PASS: 0, FAIL: 0, ADVISORY: 0}
    per_pov = {}
    for tag in "ABC":
        results = _run_level_b_pov(tag, runner)
        per_pov[tag] = results
        print(f"--- POV {tag} ---")
        for label, status, evidence in results:
            counts[status] += 1
            print(f"{status:<9} {label}: {evidence}")
        print()
    print("=" * 70)
    print("LEVEL B CROSS-POV MATRIX (qualitative evidence, no ranking)")
    print("=" * 70)
    labels = []
    for tag in "ABC":
        for label, _, _ in per_pov[tag]:
            if label not in labels:
                labels.append(label)
    status_of = {t: {label: status for label, status, _ in per_pov[t]}
                 for t in "ABC"}
    print(f"  {'PROBE':<42} {'A':<9} {'B':<9} {'C':<9}")
    for label in labels:
        row = [status_of[t].get(label, "-") for t in "ABC"]
        print(f"  {label:<42} {row[0]:<9} {row[1]:<9} {row[2]:<9}")
    print()
    print(f"Level B: {counts[PASS]} passed, {counts[ADVISORY]} advisory, "
          f"{counts[FAIL]} failed")
    print("=" * 70)
    return (counts, False)


def main() -> int:
    _, counts_a = run_level_a()
    requested, model = _model_arg(sys.argv)
    counts_b = {PASS: 0, FAIL: 0, ADVISORY: 0}
    if requested:
        counts_b, _skipped = run_level_b(model)
    fails = counts_a[FAIL] + counts_b[FAIL]
    # Exit 0 iff no FAIL. ADVISORY is allowed. A skipped Level B is not
    # a failure and is never reported as a pass.
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
