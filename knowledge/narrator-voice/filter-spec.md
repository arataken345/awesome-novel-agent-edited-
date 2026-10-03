# POV Narrative Filter — Contract

## Inputs (§44)

Before writing a scene, the filter consumes as much of the following as is
available: POV CHARACTER, CURRENT EMOTIONAL STATE, CURRENT GOAL, CURRENT
CONCERN, KNOWN FACTS, UNKNOWN FACTS, BELIEFS, SUSPICIONS, MEMORY STATE,
ATTENTION STATE, INTERPRETATION, BLIND SPOTS, FAMILIARITY, SOCIAL CONTEXT,
CHARACTER ASSOCIATIONS, NARRATIVE DISTANCE, SCENE CONTEXT.

In practice these arrive as the cognitive state file
(`.agent/cognition/vol-{N}-ch-{M}.md`) plus the character's narrator profile.

## Outputs (§45)

A compact filter with exactly these fields (see `tools/pov_filter.py`
`build_filter` for the deterministic assembly):

- WHAT_TO_NOTICE / WHAT_TO_PRIORITIZE / WHAT_TO_IGNORE
- WHAT_TO_AVOID_EXPLAINING
- WHAT_THE_CHARACTER_THINKS_IT_MEANS
- WHAT_THE_CHARACTER_DOES_NOT_KNOW
- WHAT_MAY_BE_MISINTERPRETED
- WHAT_ASSOCIATIONS_ARE_NATURAL
- EMOTIONAL_FRAMING
- DESCRIPTION_DENSITY / SENSORY_PRIORITY
- CERTAINTY_LEVEL / NARRATIVE_DISTANCE
- FAMILIARITY_COMPRESSION / SOCIAL_PERCEPTION
- CURRENT_COGNITIVE_DISTRACTIONS

## Closed-POV discipline (defaults)

For scenes marked closed POV, the filter enforces:

- **One scene → one active consciousness.** No paragraph-level switching.
  Handoffs happen only at scene breaks, never mid-scene.
- **No other-character interiority.** Others' inner states appear only as
  observed behavior, never as asserted fact.
- **No narrator foreshadowing.** Nothing the POV cannot know at this moment:
  no "little did they know", no hindsight, no future-tense knowledge.
- **No unmarked narrator-privilege exposition.** The narrator does not
  explain what an event objectively means, only what the POV makes of it.
- **No manufactured dramatic irony via cutaways.** Irony comes from scene
  structure (the reader holding the POV's misreading against shown
  evidence), not from villain-POV inserts.

## Narrator voice is not authorial voice

Avoid any statement that requires knowledge the POV does not possess.
"He did not know that this would be the last time he saw her" is forbidden
in closed POV unless the narrative mode explicitly permits authorial
foresight (it does not, by default).
