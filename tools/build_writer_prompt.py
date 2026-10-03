#!/usr/bin/env python3
"""Production seam: deterministic Writer-prompt cognition assembly.

This module is the SINGLE SOURCE OF TRUTH for the mechanical,
deterministic core of Writer prompt construction (prompt-crafter
Step 1.6: sparse injection of the scene's POV cognitive state and
POV narrative filter into the Writer-facing prompt document).

Contract
--------
``build_writer_prompt(scene_canon, pov_filter, memory=None)`` assembles
the Writer prompt's cognition/filter portion from ONLY:

- ``scene_canon``: current-scene canon, scene-necessary items only.
  Format: iterable of ``(key, text)`` pairs; the Writer sees the text.
- ``pov_filter``: the current scene's 16-field POV filter, as produced
  by ``tools/pov_filter.py::build_filter``.
- ``memory``: optional ``{"fidelity": ..., "recall": ...}`` carried from
  the cognitive state's memory entry.

There is deliberately NO parameter for hidden story truth, other POVs'
cognition, unresolved-registry / delayed-meaning entries, future
payoffs, or other scenes' material. The signature itself is the
quarantine: anything not passed in cannot leak into the prompt.

Sparse injection: at most ``SPARSE_CEILING`` (5) load-bearing filter
constraints are selected, in ``SPARSE_PRIORITY`` order, among fields
with substantive content. Fewer than 5 is normal; 0 is legal. The
ceiling is never padded to a quota.

What this seam does NOT do
--------------------------
The full production prompt (``prompts/vol-{N}-ch-{M}-prompt.md``) is a
6-element document assembled by the prompt-crafter agent
(``skills/prompt-crafting.md`` Step 2): role, task instruction, background,
cases, input scene material, output constraints. The LLM-side work --
style rendering, scene-method transformation, case authoring, conflict
adjudication -- stays in the agent. THIS seam covers the deterministic
cognition/filter assembly that must be byte-identical whether it runs in
production or under test. ``skills/prompt-crafting.md`` Step 1.6
designates this module as authoritative for that portion; the agent MUST
NOT reimplement the selection/serialization logic, and neither may any
benchmark.

Global hard rules (no-colon / no-semicolon / one-dialogue-per-paragraph)
are injected by the prompt-crafter agent into the prompt's
"output - non-violable rules" section (Step 1.6.5), not by this seam.

Returns
-------
``{"document": <markdown the Writer reads>,
  "constraints": [field names injected, in priority order],
  "sections": [...]}``
"""

from __future__ import annotations

import json

# Fixed priority order for sparse-constraint selection (prompt-crafter
# Step 1.6: inject only load-bearing constraints).
SPARSE_PRIORITY = [
    "WHAT_TO_NOTICE",
    "WHAT_TO_IGNORE",
    "EMOTIONAL_FRAMING",
    "WHAT_THE_CHARACTER_THINKS_IT_MEANS",
    "WHAT_MAY_BE_MISINTERPRETED",
    "SOCIAL_PERCEPTION",
    "FAMILIARITY_COMPRESSION",
    "WHAT_ASSOCIATIONS_ARE_NATURAL",
    "CURRENT_COGNITIVE_DISTRACTIONS",
    "SENSORY_PRIORITY",
]

# 5 is a ceiling, never a quota. 0-5 load-bearing constraints allowed.
SPARSE_CEILING = 5


def _canon(value) -> str:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return json.dumps(list(value), ensure_ascii=False)
    return str(value)


def _field_has_load(field: str, value) -> bool:
    """A filter field carries load iff it has substantive content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple)):
        return len(value) > 0
    if isinstance(value, dict):
        return any(_field_has_load(k, v) for k, v in value.items())
    return True


def build_writer_prompt(scene_canon, pov_filter, memory=None) -> dict:
    """Assemble the Writer prompt's cognition/filter portion (production).

    Deterministic: same inputs always yield the same document. Reads
    nothing from disk, imports no agent state, and accepts no hidden
    channels -- the quarantine is structural, in the signature.
    """
    lines = ["# WRITER PROMPT -- Step 1.6 cognition/filter assembly",
             "## SCENE CANON"]
    lines += [f"- {text}" for _, text in scene_canon]
    lines += ["## POV FILTER"]
    for field, value in pov_filter.items():
        lines.append(f"- {field}: {_canon(value)}")
    constraints = []
    for field in SPARSE_PRIORITY:
        if len(constraints) >= SPARSE_CEILING:
            break
        value = pov_filter.get(field)
        if _field_has_load(field, value):
            constraints.append((field, value))
    lines += ["## SPARSE CONSTRAINTS"]
    for i, (field, value) in enumerate(constraints, 1):
        lines.append(f"- [C{i}] {field}: {_canon(value)}")
    if not constraints:
        lines.append("- (none: no load-bearing cognitive constraints this scene)")
    sections = ["SCENE CANON", "POV FILTER", "SPARSE CONSTRAINTS"]
    if memory is not None:
        lines += ["## MEMORY",
                  f"- fidelity: {memory.get('fidelity', 'unspecified')}",
                  f"- recall: {memory.get('recall', '')}"]
        sections.append("MEMORY")
    document = "\n".join(lines)
    return {"document": document,
            "constraints": [f for f, _ in constraints],
            "sections": sections}


def self_test() -> int:
    """Minimal structural self-test: determinism + quarantine shape."""
    filt = {"WHAT_TO_NOTICE": ["the door"],
            "WHAT_TO_IGNORE": [],
            "EMOTIONAL_FRAMING": "calm",
            "UNRELATED_FIELD": "present but not prioritized"}
    canon = [("door", "The door stands open.")]
    a = build_writer_prompt(canon, filt)
    b = build_writer_prompt(canon, filt)
    assert a["document"] == b["document"], "not deterministic"
    assert a["constraints"] == ["WHAT_TO_NOTICE", "EMOTIONAL_FRAMING"], \
        f"sparse selection wrong: {a['constraints']}"
    assert len(a["constraints"]) <= SPARSE_CEILING
    # Empty filter is legal.
    empty = build_writer_prompt(canon, {})
    assert empty["constraints"] == []
    assert "(none" in empty["document"]
    # Memory section appears only when provided.
    assert "MEMORY" not in a["sections"]
    mem = build_writer_prompt(
        canon, filt, memory={"fidelity": "fuzzy", "recall": "something"})
    assert "MEMORY" in mem["sections"]
    print("build_writer_prompt self-test: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(self_test())
