# Narrator Voice — Knowledge Index

## Why this layer exists

Three things are routinely collapsed into one, and the collapse is what
makes POV characters narrate identically:

- **CHARACTER VOICE** — how the character speaks (dialogue: diction, rhythm,
  catchphrases).
- **CHARACTER COGNITION** — how the character processes reality (what they
  know, notice, remember, misinterpret, feel).
- **POV NARRATIVE VOICE** — how the narration presents reality *through*
  that character.

This layer owns the third. It converts the cognitive state (built by
`cognition-agent` from `knowledge/cognition/`) into a narrative filter:
what the narration notices, how it describes, what it explains, what it
leaves alone — in this character's perceptual and associative idiom.

The system must never reduce narrative voice to dialogue vocabulary. Two
characters can share a dialect and narrate nothing alike, because they
attend to different things, judge differently, and reach for different
associations.

## Files in this directory

| File | Covers |
|---|---|
| `filter-spec.md` | The POV filter contract: inputs (§44), outputs (§45), closed-POV discipline, default disciplines |
| `profile-template.md` | Narrator voice profile fields (§43) — persistent per POV character |
| `distance-modulation.md` | Narrative distance (close/moderate/distant) and emotional modulation across scenes |

## Pipeline position

```
cognition-agent  →  cognitive state (.agent/cognition/)
        ↓
narrator-voice-agent → POV narrative filter (§45, via tools/pov_filter.py)
        ↓
prompt-crafter   →  sparse injection into the writing prompt
        ↓
writer           →  prose
```

The filter is compact by design: only what the writer needs for *this*
scene. The full profile stays in the character setting; the full cognitive
state stays in the cognition file.
