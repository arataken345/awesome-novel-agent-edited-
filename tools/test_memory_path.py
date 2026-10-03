#!/usr/bin/env python3
"""Memory-path verification: state -> filter -> prompt determinism.

The production memory path is file-based: cognition-agent writes
.agent/cognition/*.md, prompt-crafter reads it and injects the memory
record into the prompt. That file -> agent handoff is LLM-agent behavior
and is OUTSIDE deterministic reach.

What these tests pin are the Python-executable links on either side:

  state["interpretations"] --build_filter--> filter field (verbatim, unnormalized)
  memory={"fidelity","recall"} --build_writer_prompt--> ## MEMORY section (verbatim)

Boundary facts documented here, not tested:
- build_filter never reads a state's "memory" key; the memory record
  travels as the explicit memory= argument to build_writer_prompt,
  mirroring prompt-crafter reading the memory section of the cognition
  .md directly (the signature is the quarantine).
- The suppression decision lives in the agent: a forgotten/suppressed
  memory is handed to build_writer_prompt as memory=None. Passing an
  explicit record would still render it -- the agent must not do that.

Usage: python tools/test_memory_path.py
Returns 0 on all pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_util import check, summary, exit_code, load_module

POV_FILTER = load_module(
    "pov_filter_mod", Path(__file__).resolve().parent / "pov_filter.py"
)
PROMPT_ASM = load_module(
    "build_writer_prompt_mod", Path(__file__).resolve().parent / "build_writer_prompt.py"
)
FIX = load_module(
    "cognition_test_fixtures_mod",
    Path(__file__).resolve().parent / "cognition_test_fixtures.py",
)

# A forgotten/suppressed memory, same (fidelity, recall, rules) shape as
# MEMORY_VARIANTS. Defined here, not in the shared fixture, so other
# suites iterating MEMORY_VARIANTS are unaffected.
SUPPRESSED_MEMORY = ("suppressed", "", {"absent": True})

EXACT_QUOTE = "I'll come tomorrow."  # MEMORY_VARIANTS "exact" recall


def _build(fidelity, recall, memory_arg):
    state = FIX.make_state(
        memory={"fidelity": fidelity, "recall": recall},
        interpretations=[recall] if recall else [],
    )
    filt = POV_FILTER.build_filter(FIX.make_profile(), state)
    result = PROMPT_ASM.build_writer_prompt(
        FIX.SCENE_CANON, filt, memory=memory_arg
    )
    return filt, result


def _memory_block(document: str) -> str:
    """The ## MEMORY section of the prompt document, or '' if absent."""
    if "## MEMORY" not in document:
        return ""
    return document.split("## MEMORY", 1)[1]


# --------------------------------------------- link 1: state -> filter

def test_recall_survives_filter_verbatim():
    for fidelity, recall, _rules in FIX.MEMORY_VARIANTS:
        filt, _ = _build(fidelity, recall,
                         {"fidelity": fidelity, "recall": recall})
        got = filt["WHAT_THE_CHARACTER_THINKS_IT_MEANS"]
        check(f"[{fidelity}] recall in filter byte-identical (not normalized)",
              got == [recall],
              f"got={got!r} want={[recall]!r}")


# --------------------------------------------- link 2: filter -> prompt

def test_memory_section_per_fidelity():
    for fidelity, recall, rules in FIX.MEMORY_VARIANTS:
        _, result = _build(fidelity, recall,
                           {"fidelity": fidelity, "recall": recall})
        doc = result["document"]
        block = _memory_block(doc)
        check(f"[{fidelity}] MEMORY section present", bool(block))
        check(f"[{fidelity}] fidelity label preserved",
              f"- fidelity: {fidelity}" in block)
        check(f"[{fidelity}] recall byte-identical in prompt",
              f"- recall: {recall}" in block)

        if fidelity == "exact":
            check("[exact] byte-identical to canon quote",
                  recall == EXACT_QUOTE and EXACT_QUOTE in block)
        else:
            check(f"[{fidelity}] never restored to canon wording",
                  EXACT_QUOTE not in block)

        hedge = rules.get("keeps_hedge")
        if hedge:
            check(f"[{fidelity}] hedge word '{hedge}' preserved (not upgraded)",
                  hedge in block)
        for forbidden in rules.get("forbids", []):
            check(f"[{fidelity}] forbidden canon wording '{forbidden}' absent",
                  forbidden not in block)
        marker = rules.get("keeps")
        if marker:
            check(f"[{fidelity}] distortion marker present", marker in block)


# --------------------------------------------- absence paths

def test_no_memory_no_section():
    # memory=None must not inject a phantom memory section.
    _, result = _build("exact", EXACT_QUOTE, None)
    doc = result["document"]
    check("memory=None -> no MEMORY section", "## MEMORY" not in doc)
    check("memory=None -> MEMORY absent from section list",
          "MEMORY" not in result["sections"])
    check("memory=None -> no '- recall:' memory record line",
          "- recall:" not in doc)
    # The recall still reaches the filter via interpretations (link 1, pinned
    # above); only the MEMORY section must be absent, never the filter entry.
    check("memory=None -> filter link intact (recall via interpretations)",
          EXACT_QUOTE in doc)


def test_suppressed_memory_produces_no_content():
    # The agent's suppression decision: a forgotten memory is handed over
    # as memory=None -- there is no record to inject, so the prompt must
    # carry neither the section nor the suppression label.
    fidelity, recall, _rules = SUPPRESSED_MEMORY
    filt, result = _build(fidelity, recall, None)
    doc = result["document"]
    check("suppressed -> no MEMORY section", "## MEMORY" not in doc)
    check("suppressed -> no suppression label leaks",
          "suppressed" not in doc.lower())
    check("suppressed -> filter interpretations empty",
          filt["WHAT_THE_CHARACTER_THINKS_IT_MEANS"] == [])


# --------------------------------------------- determinism of the seam

def test_prompt_assembly_deterministic():
    fidelity, recall, _rules = FIX.MEMORY_VARIANTS[4]  # uncertain
    arg = {"fidelity": fidelity, "recall": recall}
    _, r1 = _build(fidelity, recall, arg)
    _, r2 = _build(fidelity, recall, dict(arg))
    check("same memory inputs -> byte-identical prompt",
          r1["document"] == r2["document"])


if __name__ == "__main__":
    test_recall_survives_filter_verbatim()
    test_memory_section_per_fidelity()
    test_no_memory_no_section()
    test_suppressed_memory_produces_no_content()
    test_prompt_assembly_deterministic()
    print(f"\n{summary()}")
    sys.exit(exit_code())
