# Narrative Distance & Emotional Modulation

## Narrative distance

The filter supports variable distance without breaking closed POV:

- **close** — bodily sensation, fragmented cognition, immediate association,
  uncertainty on the surface. Thought rendered near-verbatim.
- **moderately_close** — the default. Interiority summarized but still
  character-colored; perception leads.
- **distant** — compressed thought, wider framing, cooler diction. Still
  inside the POV's cognition — distance is not omniscience.

Distance is set per scene (or per beat) by the narrator-voice-agent from the
cognitive state: urgency and emotional flooding pull close; calm procedure
allows distance.

## CLOSED_POV_EPISTEMIC_INVARIANT

Narrative distance controls presentation distance (descriptive density,
abstraction level, emotional rendering distance, sentence presentation) —
NEVER epistemic permissions (what the POV knows/observes/infers, which
secrets are accessible, what future information is possessed).

Even at `narrative_distance=distant`, the narration may not:

- state another character's hidden thoughts or motives as fact;
- state unrevealed story truth as if the POV knew it;
- state future significance ("this would matter later") as possessed knowledge;
- state hidden causes the POV has not observed, learned, or inferred;
- state any fact unknown to the POV at this moment.

A distant-voiced sentence may compress, cool, and abstract — but everything
it asserts must remain traceable to the POV's OBSERVATION / MEMORY /
BELIEF / GUESS / INTERPRETATION layers (see
`knowledge/cognition/epistemic-layers.md`). Anything the story establishes
only the author, the reader, or another character knows is epistemically
forbidden regardless of distance. When in doubt, the per-scene knowledge
lattice (READER KNOWS / POV KNOWS / OTHERS KNOW / HIDDEN FORCES / WITHHELD)
decides — never the distance setting.

## Emotional modulation

The same character does not narrate every scene identically. Perceptual
emphasis shifts with fear, excitement, anger, exhaustion, grief, calm,
embarrassment, obsession, urgency — while identity stays stable. The filter
records the current modulation so the writer can shift emphasis without
shifting character:

- What gets noticed more / less under this emotion.
- Whether description expands (flooding) or compresses (shutdown).
- Whether certainty rises (anger, obsession) or collapses (fear, grief).
- Whether associations darken, sharpen, or go quiet.

Modulation is derived from `emotional_state` in the cognitive state, never
imposed by the writer's convenience.
