# Epistemic Layers & Information Asymmetry

## Why

The single most common omniscient-model failure is **epistemic collapse**:
the narration silently treats everything the model knows as something the
narrator may say. A character's guess gets written as fact. A suspicion gets
written as certainty. An interpretation gets written as observation. The
reader can no longer tell what is true, what is seen, and what is merely
believed — because the narration itself no longer distinguishes them.

This file defines the layers. They must remain distinct in the cognitive
state, in the POV filter, and in the prose.

## The 11 layers

| Layer | Meaning | Example (same situation) |
|---|---|---|
| FACT | Story truth (what actually is) | She is holding a phone. |
| OBSERVATION | What the POV character's senses register | A rectangle of light in her hand. |
| MEMORY | What the POV recalls (see `memory-model.md`) | She always checks it at dinner. |
| BELIEF | What the POV holds true (may be wrong) | She probably knows something. |
| GUESS | Conscious low-confidence hypothesis | Maybe she received bad news. |
| SUSPICION | Guess with emotional charge / distrust | She is hiding something from me. |
| RUMOR | Second-hand information, source uncertain | Mara said she was seen crying. |
| INTERPRETATION | Meaning the POV assigns to an observation | She looks nervous. |
| MISINTERPRETATION | Interpretation that is wrong (story truth differs) | He smiled → "He is mocking me." (truth: he is nervous) |
| UNCERTAINTY | Explicitly unresolved | He could not tell whether she had heard. |
| UNKNOWN | Not present in the POV's cognition at all | (absent — must never appear in narration) |

## Rules

1. **Never silently convert.** An INTERPRETATION must not be written as an
   OBSERVATION ("She looks nervous" must not become "She was nervous").
   A BELIEF must not be written as FACT. Marking is the mechanism:
   hedged perception ("seemed", "looked like", "he took it as", "she wondered
   whether") is **mandatory** for anything above OBSERVATION/MEMORY — and
   must never be stripped by editing passes.
2. **Observation is thin.** Senses register surfaces, not meanings. If the
   narration states a meaning, it must be traceable to an INTERPRETATION or
   BELIEF in the cognitive state — or it is an epistemic violation.
3. **Beliefs can be wrong** (`story_truth != character_belief`). The system
   must allow and preserve wrong beliefs; correcting them automatically is
   an authorial intrusion.
4. **Causal claims need a cause-source.** Known cause / suspected cause /
   multiple possible causes / unknown cause / incorrectly assumed cause —
   the narration must not upgrade "suspected" to "known".

## Information asymmetry

Five knowledge positions must be tracked separately per scene:

- **STORY TRUTH** — what actually is (canon; the archive system owns this).
- **POV KNOWLEDGE** — what the POV character knows right now.
- **OTHER CHARACTER KNOWLEDGE** — what others know (the POV may not know it).
- **READER KNOWLEDGE** — what the reader has been shown so far.
- **POV BELIEF** — what the POV holds true, rightly or wrongly.

The writer may only reveal what the narrative mode and current POV permit.
For strict closed POV: **the narrator must not know something merely because
the author/model knows it.**

## The per-scene knowledge lattice

Every scene's cognitive state must contain a lattice:

```
READER KNOWS:     ...
POV KNOWS:        ...
OTHERS KNOW:      ... (each relevant character, separately)
HIDDEN FORCES:    ... (active but unrevealed, or "none")
WITHHELD:         ... (fact / withholder / why withheld / intended payoff)
```

A fact may appear in STORY TRUTH but in none of the character positions —
that is legitimate dramatic irony, not a gap to close. The lattice exists so
the pipeline *knows* the gap is intentional.

## Reader-character gap (intentional)

Allow READER UNDERSTANDS while CHARACTER DOES NOT — without forcing the
narrator to explain the difference. This is the engine of dramatic irony,
hidden motives, emotional subtext, and character self-deception. The
narration must not collapse the gap by over-explaining it.
