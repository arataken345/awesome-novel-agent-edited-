#!/usr/bin/env python3
"""Cognition-preservation tests: humanizer stage, reader stage, registry isolation.

Problems 6, 7, 16 (+ the no-humanity-score guard, Problem 12).

Scope (honest limits)
---------------------
The humanizer rewrite stage (agents/humanizer.md) and the reader review stage
(agents/reader.md) are LLM agents. They CANNOT be executed deterministically.
This file does NOT simulate a humanizer rewrite with deterministic logic and
does NOT claim to validate a rewrite. What it pins is:

(a) the deterministic machine pre-screen contract
    (tools/check-prose-en.py): cognitively-meaningful prose behaviors must
    not draw a must-fix flag demanding their removal;
(b) the guard wiring (knowledge/humanizer/hedge-protection.md exists, is merged
    into the deployed humanizer knowledge by tools/init.py, and states that
    hedged perception must never be upgraded to stated fact);
(c) documented-contract assertions (labeled SPEC-CONTRACT) over
    agents/novel-agent.md and agents/reader.md: reader review is advisory-only
    and never auto-dispatches a rewrite order;
(d) the production prompt seam (tools/build_writer_prompt.py): signature
    quarantine + registry/future isolation;
(e) a no-humanity-score guard over tools/test_*.py.

Simulated vs real (Problem 6/7 specifics)
-----------------------------------------
REAL (executed): check_text() over synthetic fixtures; file-existence and
text-presence structural pins; inspect.signature of build_writer_prompt;
normalized containment of decoy strings in a built prompt document.
SPEC-CONTRACT (documented, not executed): the novel-agent rewrite-dispatch
table and the reader advisory-only doctrine are markdown documents; these
tests assert the dispatch contracts the docs state, and say so in the check
names. The LLM reader agent itself is not executed here.
NOT PROVEN here: the actual behavior of the anti-AI rewrite pass, the reader
agent's qualitative feedback, or any end-to-end chapter run. Those remain
LLM-agent behavior.

Fixture convention (COGNITIVE_BEHAVIOR_AUTHENTICITY)
---------------------------------------------------
Every behavior fixture below is a cognitively-MEANINGFUL prose behavior
paired with the cognitive cause that justifies it (from the synthetic
fixture universe in tools/cognition_test_fixtures.py). Each check asserts
two things: (1) the intentional behavior marker IS present in the fixture
(a check that passes because the behavior is absent would be vacuous),
and (2) the machine pre-screen emits no must-fix failure for it.
All fixtures are SYNTHETIC; "Rook"/"Sable" assert no canon facts.

Usage: python3 tools/test_cognition_preservation.py
Exit code 0 = all checks pass.
"""

import inspect
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_util import check, summary, exit_code, load_module

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

CHECK_EN = load_module("check_prose_en_cp", TOOLS / "check-prose-en.py")
BWP = load_module("build_writer_prompt_cp", TOOLS / "build_writer_prompt.py")
POVF = load_module("pov_filter_cp", TOOLS / "pov_filter.py")
FIX = load_module("cognition_test_fixtures_cp",
                  TOOLS / "cognition_test_fixtures.py")


def en_failures(prose: str):
    """Deterministic pre-screen: returns the must-fix failure list."""
    return CHECK_EN.check_text(prose).failures


# ------------------------------------------------------- Problem 6 fixtures
# Each: id, cognitive cause (per COGNITIVE_BEHAVIOR_AUTHENTICITY), prose,
# and the intentional-behavior marker that must survive in the prose.

FIXTURES = [
    {
        "id": "hedged-perception",
        "cause": ("epistemic layer UNCERTAINTY: the sound's source is "
                  "underdetermined by the POV's hearing; perception must "
                  "stay hedged"),
        "marker": "might have been",
        "prose": (
            "The duct clank came again, fainter this time. It might have been "
            "the ventilation settling after the temperature drop. Or perhaps "
            "water moving through the building's old pipes. The sound reached "
            "him as if from far above the strategy room, bent and thinned by "
            "the shafts it had traveled. Rook could not tell whether it was "
            "closer than before or only louder against the quiet. He waited "
            "through two full breaths. Nothing followed."
        ),
    },
    {
        "id": "wrong-belief-as-belief",
        "cause": ("POV A's social model ('people communicate strategically') "
                  "plus familiarity compression: sincere but wrong "
                  "interpretation of the key"),
        "marker": "was certain the brass key was ceremonial",
        "story_truth_outside_prose": FIX.HIDDEN_TRUTH,
        "prose": (
            "Rook was certain the brass key was ceremonial. Sable kept it on "
            "the table the way a chairperson keeps a gavel, visible but never "
            "used, a prop that lent weight to the room. It caught the light "
            "from the display and threw small gold flecks across the telemetry. "
            "He had seen keys like that in old headquarters, souvenirs of "
            "mergers no one remembered. Whatever its history, its function "
            "here was display, nothing more."
        ),
    },
    {
        "id": "non-closure",
        "cause": ("unknown_facts quarantine: the POV must not know what it "
                  "cannot know; closure is epistemically withheld, not "
                  "forgotten"),
        "marker": "unexplained",
        "prose": (
            "The sealed envelope leaned against the display stand, cream paper "
            "gone yellow at the edges. No name, no seal. Rook noticed his gaze "
            "returning to it between Sable's sentences, the way a tooth finds "
            "a sore spot. Sable said nothing about it. The display cycled to a "
            "new telemetry page, and the meeting moved on, and the envelope "
            "stayed exactly where it was, unexplained."
        ),
    },
    {
        "id": "meaningful-repetition",
        "cause": ("rising stress drives a self-reassurance ritual: attention "
                  "fixation on Sable's tapping fingers, repeated with cause, "
                  "not filler"),
        "marker": "two fingers",
        "prose": (
            "Sable tapped two fingers against the table edge. A pause in the "
            "briefing, and the tapping resumed, two fingers, steady, louder "
            "than the ductwork. Rook realized he had been counting the taps "
            "without deciding to count them. Two fingers. Again. Whatever "
            "Sable was holding back, it was pressing hard enough to leak "
            "through her hands."
        ),
    },
    {
        "id": "dead-end-attention",
        "cause": ("current_distractions: the duct clank captures attention but "
                  "resolves into nothing; unmanaged attention is realistic"),
        "marker": "the duct made no further sound",
        "prose": (
            "A clank came from the ventilation duct somewhere above the table. "
            "Rook's eyes went up before he could stop them, tracking the shaft "
            "across the ceiling. The display flickered, and Sable's voice "
            "continued over the numbers, and the duct made no further sound. "
            "It was nothing. Rook pulled his attention back to the telemetry "
            "he was supposed to be watching."
        ),
    },
    {
        "id": "self-blindness",
        "cause": ("emotional_awareness below recognition for a social emotion: "
                  "the POV registers the body, never the label"),
        "marker": "jaw had gone tight",
        "forbidden_labels": ["jealous", "jealousy", "envious", "envy"],
        "prose": (
            "Rook's jaw had gone tight again. He unclenched it and found his "
            "thumb pressing a hard line into the table edge. Sable laughed at "
            "something the aide said, quick and easy, and the sound landed "
            "like a grain of sand in his eye. He flipped to the next telemetry "
            "page before she could see his face. The numbers swam. He read the "
            "same line three times and retained nothing."
        ),
    },
    {
        "id": "social-misinterpretation",
        "cause": ("POV C's social model ('people seek emotional reassurance'): "
                  "a flat tone is misread as a plea, marked as interpretation, "
                  "not fact"),
        "marker": "took the flatness as exhaustion",
        "prose": (
            '"The schedule moved," Sable said, flat and fast, already turning '
            "back to the display.\n\n"
            "Rook took the flatness as exhaustion wearing a uniform. She was "
            "asking, in the only way the room allowed, for someone to notice "
            "how thin she was stretched. He softened his voice when he "
            "answered, offering her an opening to admit it. She did not take it."
        ),
    },
    {
        "id": "memory-uncertainty",
        "cause": ("fuzzy memory fidelity: the recall path degrades the name; "
                  "uncertainty is marked, not resolved"),
        "marker": "Or maybe Elian",
        "prose": (
            "The aide's name surfaced wrong twice. Elias, he thought, then "
            "corrected himself. Or maybe Elian. The badge had been turned "
            "inward all morning, and Rook had met the man once, briefly, in a "
            "corridor with bad lighting. He decided to avoid the name entirely "
            "and address the room instead. Names were the first things to go "
            "when he was tired, and he was tired."
        ),
    },
    {
        "id": "selective-omission",
        "cause": ("attention.IGNORED: the vaulted ceiling is "
                  "familiarity-compressed out of perception; absence is valid "
                  "cognition, not a defect"),
        "marker": "brass key",
        "must_omit": ["vaulted", "ceiling", "acoustic"],
        "prose": (
            "The display cycled through telemetry pages Rook had already "
            "memorized. Sable's hands rested flat on the table now, still at "
            "last. The brass key sat between them, catching light. Rook "
            "watched her shoulders drop a fraction and decided the worst of "
            "the briefing was over."
        ),
    },
    {
        "id": "cognitive-distraction",
        "cause": ("current_distractions plus attention load: the duct clank "
                  "steals bandwidth; the display compresses to a glance"),
        "marker": "waiting for a second clank that never came",
        "prose": (
            "The clank from the duct pulled half his attention up into the "
            "ceiling shafts and would not give it back. Sable kept talking. "
            "Rook caught fragments, telemetry, a number that might have "
            "mattered, and let the display blur into a sheet of blue light. He "
            "was listening to the duct, waiting for a second clank that never "
            "came, while the meeting went on without him."
        ),
    },
]


def test_preservation_pre_screen():
    for fx in FIXTURES:
        prose = fx["prose"]
        # (1) the intentional behavior is actually present (no vacuous pass)
        check(
            f"preservation/{fx['id']}: behavior marker present "
            f"('{fx['marker']}')",
            fx["marker"] in prose,
            f"marker missing from fixture [{fx['cause']}]",
        )
        # (2) the pre-screen emits no must-fix flag for the fixture
        failures = en_failures(prose)
        check(
            f"preservation/{fx['id']}: no must-fix flag from check-prose-en "
            f"(failures=0)",
            failures == [],
            f"must-fix failures: {failures[:3]} [{fx['cause']}]",
        )
        # behavior-specific integrity pins
        if "story_truth_outside_prose" in fx:
            truth = fx["story_truth_outside_prose"]
            check(
                f"preservation/{fx['id']}: story truth stays OUTSIDE the prose",
                truth not in prose,
                "story truth leaked into prose",
            )
        for label in fx.get("forbidden_labels", []):
            check(
                f"preservation/{fx['id']}: no diagnostic label "
                f"('{label}') in prose",
                label.lower() not in prose.lower(),
                f"label '{label}' found in prose",
            )
        for term in fx.get("must_omit", []):
            check(
                f"preservation/{fx['id']}: ignored element absent "
                f"('{term}')",
                term.lower() not in prose.lower(),
                f"ignored element '{term}' present in prose",
            )


def test_hedge_protection_wiring():
    guard = REPO / "knowledge/humanizer/hedge-protection.md"
    check("humanizer-preservation/guard: hedge-protection.md exists",
          guard.exists(), str(guard))
    guard_text = guard.read_text(encoding="utf-8") if guard.exists() else ""
    init_text = (TOOLS / "init.py").read_text(encoding="utf-8")
    check(
        "humanizer-preservation/wiring: init.py merges hedge-protection.md "
        "into the deployed humanizer knowledge",
        '"hedge-protection.md"' in init_text,
        "filename not found in tools/init.py",
    )
    check(
        "humanizer-preservation/guard: hedged perception must never be "
        "upgraded to stated fact",
        "升级为事实" in guard_text and "事实升级" in guard_text,
        "guard text missing the no-fact-upgrade rule",
    )
    checker_src = (TOOLS / "check-prose-en.py").read_text(encoding="utf-8")
    check(
        "humanizer-preservation/checker-contract: hedged perception is "
        "deliberately NEVER flagged by check-prose-en",
        "deliberately NEVER" in checker_src and "flagged" in checker_src,
        "contract statement not found in check-prose-en.py",
    )


# ------------------------------------------------------- Problem 7: reader


def test_reader_advisory_only():
    reader_md = (REPO / "agents/reader.md").read_text(encoding="utf-8")
    review_md = (REPO / "skills/reader-review.md").read_text(encoding="utf-8")
    check(
        "reader-preservation/advisory: agents/reader.md states the reader "
        "never has pass/fail power",
        "读者永无通过/不通过权力" in reader_md,
        "advisory-only phrase missing from agents/reader.md",
    )
    check(
        "reader-preservation/advisory: reader.md keeps decision rights at "
        "feedback only",
        "仅做反馈，不做通过/不通过的判决" in reader_md,
        "decision-rights line missing from agents/reader.md",
    )
    check(
        "reader-preservation/advisory: skills/reader-review.md repeats the "
        "advisory-only doctrine (H1-H15 flags are feedback, not verdict)",
        "读者永远无通过/不通过权力" in review_md
        and "只反馈，不下判决" in review_md,
        "advisory-only phrase missing from skills/reader-review.md",
    )


def test_rewrite_dispatch_contract():
    # SPEC-CONTRACT: the dispatch table is a markdown document. These tests
    # assert the contract the document states; they do not execute dispatch.
    novel = (REPO / "agents/novel-agent.md").read_text(encoding="utf-8")
    check(
        "reader-preservation/SPEC-CONTRACT: rewrite dispatch is documented "
        "from humanizer FAIL (round<3)",
        "FAIL 且 round < 3" in novel and "rewrite-order" in novel,
        "humanizer FAIL -> rewrite-order dispatch missing",
    )
    review_idx = novel.find("step=reviewing")
    archive_idx = novel.find("step=archiving", review_idx)
    review_section = (
        novel[review_idx:archive_idx] if review_idx >= 0 and archive_idx > 0
        else ""
    )
    check(
        "reader-preservation/SPEC-CONTRACT: no path dispatches a rewrite "
        "order from reader review alone",
        review_idx >= 0 and archive_idx > 0
        and "rewrite-order" not in review_section,
        "rewrite-order found inside the review step section",
    )
    check(
        "reader-preservation/SPEC-CONTRACT: the only other documented "
        "rewrite path is the explicit author decision (rollback)",
        "作者要重写某章" in novel and "rollback-order.md" in novel,
        "author-decision rollback path missing",
    )


def test_envelope_regression():
    # Sealed envelope: the POV does not know the contents. Synthetic reader
    # feedback says "I want to know what is inside". The feedback has no
    # channel into the production prompt seam: the signature admits only
    # scene_canon, pov_filter, memory.
    profile = FIX.POVS["A"]["profile"]
    state = FIX.POVS["A"]["state"]
    filt = POVF.build_filter(profile, state)
    built = BWP.build_writer_prompt(FIX.SCENE_CANON, filt)
    document = built["document"]

    envelope_contents = (
        "SYNTHETIC-SECRET-D47: the envelope holds a recall order"
    )  # lives in the test's "universe" only; never passed in
    reader_feedback = "I want to know what is inside the sealed envelope."

    check(
        "reader-preservation/envelope: contents never reach the prompt "
        "document",
        envelope_contents not in document,
        "envelope contents leaked into the Writer prompt",
    )
    check(
        "reader-preservation/envelope: the epistemic boundary is recorded, "
        "not crossed ('what the sealed envelope contains' listed as "
        "unknown, contents unstated)",
        "what the sealed envelope contains" in document
        and envelope_contents not in document,
        "unknown-fact boundary not represented in the prompt",
    )
    check(
        "reader-preservation/envelope: reader feedback cannot inject a "
        "new prompt section (signature quarantine)",
        reader_feedback not in document
        and built["sections"] == ["SCENE CANON", "POV FILTER",
                                  "SPARSE CONSTRAINTS"],
        f"sections: {built['sections']}",
    )


# ------------------------------------------------------- Problem 16: registry


def test_registry_isolation():
    params = list(inspect.signature(BWP.build_writer_prompt).parameters)
    check(
        "registry-isolation/signature: build_writer_prompt takes exactly "
        "(scene_canon, pov_filter, memory)",
        params == ["scene_canon", "pov_filter", "memory"],
        f"params: {params}",
    )
    check(
        "registry-isolation/signature: no registry/future parameter exists",
        not any("registry" in p or "future" in p for p in params),
        f"params: {params}",
    )
    filt = POVF.build_filter(FIX.POVS["B"]["profile"], FIX.POVS["B"]["state"])
    document = BWP.build_writer_prompt(FIX.SCENE_CANON, filt)["document"]
    for decoy in (FIX.REGISTRY_DECOY, FIX.FUTURE_DECOY):
        check(
            f"registry-isolation/containment: decoy absent from prompt "
            f"('{decoy[:34]}...')",
            decoy.lower().strip() not in document.lower(),
            "decoy string found in the Writer prompt",
        )
    craft = (REPO / "skills/prompt-crafting.md").read_text(encoding="utf-8")
    check(
        "registry-isolation/skill: prompt-crafting.md Step 1.6 documents "
        "that registry entries are never injected",
        "Registry 隔离" in craft and "永远不注入" in craft,
        "registry-isolation rule missing from skills/prompt-crafting.md",
    )
    check(
        "registry-isolation/skill: direction documented as writing -> "
        "registry, never back into the prompt",
        "writing → registry" in craft,
        "writing-to-registry direction missing from the skill",
    )


# ------------------------------------------------------- Problem 12: no score


def test_no_humanity_score():
    # Guard: no numerical humanity score may be computed in any behavioral
    # test. The forbidden-name regex is built by concatenation so the guard's
    # own source never contains the literal under test.
    rx_name = re.compile(r"\b" + "humanity" + "_" + "score" + r"\b")
    rx_num = re.compile(r"\bscore\s*=\s*\d+\s*/\s*100\b")
    files = sorted(TOOLS.glob("test_*.py"))
    check("no-score-guard: tools/test_*.py files exist to scan",
          len(files) > 0, "no test files found")
    for path in files:
        text = path.read_text(encoding="utf-8")
        name_hits = [ln for ln in text.splitlines() if rx_name.search(ln)]
        num_hits = [ln for ln in text.splitlines() if rx_num.search(ln)]
        check(
            f"no-score-guard/{path.name}: no " + "humanity" + "_" + "score"
            + " computation",
            not name_hits,
            f"matches: {name_hits[:2]}",
        )
        check(
            f"no-score-guard/{path.name}: no score=N/100 computation",
            not num_hits,
            f"matches: {num_hits[:2]}",
        )


if __name__ == "__main__":
    test_preservation_pre_screen()
    test_hedge_protection_wiring()
    test_reader_advisory_only()
    test_rewrite_dispatch_contract()
    test_envelope_regression()
    test_registry_isolation()
    test_no_humanity_score()
    print(f"\n{summary()}")
    sys.exit(exit_code())
