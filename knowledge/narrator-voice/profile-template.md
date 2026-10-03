# Narrator Voice Profile — Template (§43)

Persistent per-POV-character profile. Lives in the character's setting file
(`settings/character-setting/{id}.md`, "Narrator Voice Profile" section).
Not every field is required for every character — fill what matters, omit
the rest. The `narrator-voice-agent` uses the filled fields;
`tools/pov_filter.py` tolerates missing ones.

```yaml
narrator_voice_profile:
  narrative_temperament: ""        # e.g. wry, liturgical, clinical, feral
  attention_priorities: []        # what this head gravitates toward
  attention_blind_spots: []       # what this head never registers
  description_preferences: []     # textures, scales, details favored
  description_avoidance: []       # what this head will not dwell on
  sensory_priorities: []          # ordered senses, e.g. [sound, touch, sight]
  metaphor_tendencies: []         # source domains, e.g. [machinery, scripture]
  association_patterns: []        # characteristic associative leaps
  judgment_tendencies: []         # how this head evaluates people/things
  emotional_vocabulary: []        # words/concepts used for feelings (may be empty!)
  emotional_self_awareness: ""    # recognize | vague | mislabel | rationalize | deny | bodily | delayed
  interpretive_habits: []         # how this head typically reads situations
  certainty_tolerance: ""         # low | medium | high
  memory_style: ""                # exact | semantic | fragmentary | ...
  social_perception: ""           # how this head reads other people
  humor_tendency: ""              # dry | teasing | absent | gallows | ...
  abstraction_level: ""           # concrete | mixed | abstract
  narrative_distance: ""          # close | moderately_close | distant
  familiarity_compression: []     # domains this head compresses (home, tools, routines)
  normalization_patterns: []     # what this head treats as normal
  strangeness_sensitivity: ""     # low | medium | high
  beauty_sensitivity: ""          # low | medium | high
  annoyance_sensitivity: ""       # low | medium | high
  threat_sensitivity: ""          # low | medium | high
  characteristic_misinterpretations: []  # what this head typically gets wrong
  characteristic_omissions: []    # what this head typically leaves out
```

## Guidance

- **Metaphors emerge from the associative world** (profession, hobbies,
  fears, education — see `knowledge/cognition/` associations), not from a
  fixed list stapled onto the character. The `metaphor_tendencies` field
  records *tendencies*, and the filter draws on scene-relevant associations.
- **Emotional vocabulary may be empty.** A character who only feels things
  in the body has no emotional words — that absence is the profile.
- **Keep voice distinct from cognition and dialogue.** If the profile reads
  like a list of catchphrases, it is a dialogue profile, not a narrator
  profile. Rewrite it.
