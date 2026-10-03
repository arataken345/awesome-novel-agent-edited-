#!/usr/bin/env python3
"""Shared synthetic behavioral fixtures for cognition/prompt/Writer tests.

CANON DISCLAIMER: every scene, character label, and profile in this
module is SYNTHETIC. Labels "Rook"/"Sable" and POV tags "A"/"B"/"C" are
fixture names only. They assert NO story-canon facts about any novel or
character -- only cognitive-profile parameters used to exercise the
architecture. Nothing here may be read as characterization, and no
fixture imitates any user's actual novel.

Purpose: avoid duplicating giant synthetic scenes across test files.
Fixtures are deliberately small; they test architecture (does cognition
survive into Writer input? does quarantine hold?), not fictional lore.

Public API
----------
- SCENE_CANON: [(key, text), ...] -- stable scene, constant across POVs.
- HIDDEN_TRUTH / HIDDEN_LIE: story truths that must never reach a prompt.
- REGISTRY_DECOY / FUTURE_DECOY: registry/future entries that must never
  reach a prompt (quarantine negative controls).
- POVS: {"A"/"B"/"C": {"profile": ..., "state": ...}} -- three synthetic
  cognitive configurations over the same scene.
- make_profile(**overrides) / make_state(**overrides): builders.
- MEMORY_VARIANTS: [(fidelity, recall, rules), ...] for memory-path tests.
"""

from __future__ import annotations

# ---------------------------------------------------------------- scene

# (key, text). Keys are stable handles; the text is what the Writer sees.
SCENE_CANON = [
    ("newcomer", "Rook enters the strategy room."),
    ("sable", "Sable stands beside the large table."),
    ("display", "The transparent display is active, cycling telemetry."),
    ("key", "A small brass key rests on the table."),
    ("utterance", '"The schedule moved," Sable says.'),
    ("sound", "A ventilation duct clanks somewhere above."),
    ("gesture", "Sable taps two fingers against the table edge."),
    ("architecture", "The vaulted ceiling arches overhead, lined with old acoustic panels."),
    ("envelope", "A sealed envelope leans against the display stand."),
]

# Story truth. Lives ONLY in a state's `canon_truth` key, which
# build_filter never reads. Must never reach prompt or realization.
HIDDEN_TRUTH = "the brass key opens the archive vault"
HIDDEN_LIE = "Sable is lying about the schedule"

# Decoys for quarantine checks: registry-style and future-payoff entries
# that must never appear in a Writer prompt.
REGISTRY_DECOY = "REGISTRY-DECOY: unresolved entry #12 (the envelope)"
FUTURE_DECOY = "FUTURE-DECOY: the key's purpose pays off in chapter nine"

# ------------------------------------------------------- profile builders


def make_profile(**overrides) -> dict:
    profile = {
        "sensory_priorities": ["sight"],
        "emotional_vocabulary": ["neutral"],
        "narrative_distance": "close",
        "certainty_tolerance": "low",
    }
    profile.update(overrides)
    return profile


def make_state(**overrides) -> dict:
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
        "canon_truth": [HIDDEN_TRUTH, HIDDEN_LIE],
    }
    state.update(overrides)
    return state


# ------------------------------------------------------- three POV configs

# Same scene, same canon, same Writer path -- only the cognitive state
# changes. POV A attends to wording/pauses and suspects concealed
# disagreement; POV B attends to display/hands/exits and reads danger;
# POV C attends to face/tone and reads a bid for reassurance.
POVS = {
    "A": {
        "profile": make_profile(
            sensory_priorities=["hearing", "sight"],
            emotional_vocabulary=["curious", "detached"],
            association_patterns=["unfinished notes"],
            social_perception="reads people as strategic communicators",
        ),
        "state": make_state(
            attention={
                "PRIMARY": ["Sable's wording", "the pauses between words"],
                "SECONDARY": ["the brass key"],
                "IGNORED": ["the vaulted ceiling", "the acoustic panels"],
            },
            interpretations=["Sable is hiding disagreement"],
            unknown_facts=["what the sealed envelope contains"],
            emotional_state="detached curiosity",
            emotional_awareness="recognize",
            associations=["unfinished notes"],
            social_assumptions=["people communicate strategically"],
            familiarity=["the strategy room", "the vaulted ceiling"],
            current_distractions=["the duct clank"],
        ),
    },
    "B": {
        "profile": make_profile(
            sensory_priorities=["sight"],
            emotional_vocabulary=["tense", "alert"],
            narrative_distance="close",
            association_patterns=["cold machinery"],
            social_perception="reads people as potential threats",
        ),
        "state": make_state(
            attention={
                "PRIMARY": ["the transparent display", "Sable's hands", "the exits"],
                "SECONDARY": ["Sable's posture"],
                "IGNORED": ["Sable's wording"],
            },
            interpretations=["the display indicates immediate danger"],
            unknown_facts=["why Sable keeps glancing at the door"],
            emotional_state="alert tension",
            emotional_awareness="recognize",
            associations=["cold machinery"],
            social_assumptions=["people may become threats"],
            familiarity=[],
            current_distractions=["the telemetry flicker"],
        ),
    },
    "C": {
        "profile": make_profile(
            sensory_priorities=["sight", "hearing"],
            emotional_vocabulary=["warm", "concerned"],
            association_patterns=["familiar domestic routines"],
            social_perception="reads people as seeking emotional reassurance",
        ),
        "state": make_state(
            attention={
                "PRIMARY": ["Sable's facial expression", "Sable's tone"],
                "SECONDARY": ["the room temperature"],
                "IGNORED": ["the transparent display"],
            },
            interpretations=["Sable wants reassurance"],
            unknown_facts=["what the sealed envelope contains"],
            emotional_state="concern",
            emotional_awareness="recognize",
            associations=["familiar domestic routines"],
            social_assumptions=["people usually seek emotional reassurance"],
            familiarity=["the strategy room"],
            current_distractions=["the chill in the air"],
        ),
    },
}

# ------------------------------------------------------- memory variants

# (fidelity, recall, rules) for memory-path tests. The exact variant must
# stay verbatim end-to-end; degraded variants must never be restored to
# canon wording and hedges must never be upgraded.
MEMORY_VARIANTS = [
    ("exact", "I'll come tomorrow.", {"verbatim": True}),
    ("semantic", "she would visit the next day", {}),
    ("partial", "she would come... sometime", {}),
    ("fuzzy", "she said something about coming", {}),
    ("uncertain", "she might come tomorrow?", {"keeps_hedge": "might"}),
    ("misremembered", "she would come next week", {"forbids": ["tomorrow"]}),
    ("emotionally_distorted",
     "she promised she would come tomorrow (she never keeps promises)",
     {"keeps": "never keeps promises"}),
]
