# Attention Model

## Why

A language model distributes descriptive attention the way a story optimizer
would: important plot objects get loving detail, trivial objects get a
passing mention, every character in a room gets a reaction shot. Human
attention does not work like that. A person in a crisis may stare at a stain
on the floor while the plot-critical phone rings unanswered. Attention follows
goals, emotion, habit, and threat — not narrative importance.

## Attention levels

| Level | Meaning |
|---|---|
| PRIMARY | The character's focus is here; rendered in full sensory detail |
| SECONDARY | Registered, available for recall, lightly rendered |
| PERIPHERAL | Vaguely sensed; may surface later as "something felt off" |
| IGNORED | Present but unregistered (familiarity, irrelevance) |
| ACTIVELY_AVOIDED | Deliberately not looked at (fear, shame, social cost) |

## What moves attention

Drives, emotion, personality, profession, current concern, environment,
familiarity, threat, social context, fatigue/stress. The cognitive state must
record *why* attention sits where it does — attention without a cause is just
as artificial as uniform attention.

## Attention blindness

Characters must be capable of failing to notice: obvious objects,
environmental changes, subtle social cues, physical details, implications,
patterns, emotional signals. **Blindness must arise from cognition** — from
the attention model, from emotional avoidance, from familiarity, from
competing concerns. Never insert random obliviousness as a stylistic trick.
Before accepting a blindness, ask: *why would this character not notice this?*

## Uneven salience: two separate values

Maintain explicitly, per notable scene element:

- `story_importance`: HIGH / MEDIUM / LOW (what it means for the plot)
- `character_salience`: HIGH / MEDIUM / LOW (how much the character cares)

A plot-critical object with LOW character salience stays understated — the
character does not recognize its significance, and the narration must not
compensate by emphasizing it "for the reader". A trivial object with HIGH
character salience may receive disproportionate description. **Do not optimize
descriptive space by plot importance alone.**

## Related behaviors (all causally motivated)

- **Wrong focus**: the character notices the stain, the shoes, the broken
  object — while the reader expects attention on the major event. Valid when
  the attention model justifies it.
- **Disproportionate attention**: a trivial object described at length because
  it matters to *this* character.
- **Incomplete perception**: partial senses, blocked vision, missed sounds,
  uncertain recognition, peripheral perception, delayed recognition,
  mishearing. Characters do not perceive like cameras.
- **Familiarity compression**: familiar rooms, people, tools, routines are
  NOT re-described from scratch. Newness increases attention; familiarity
  compresses it. (Test: a character entering a familiar room gets no automatic
  full re-description.)
- **Presence ≠ participation**: characters may be present and silent. Never
  force every visible character to speak, react, or contribute.
