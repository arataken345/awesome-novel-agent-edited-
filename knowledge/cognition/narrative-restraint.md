# Narrative Restraint

## Why

A story-optimizing model cannot leave anything alone: every detail
foreshadows, every setup pays off, every scene closes, every theme is
visible. This relentless efficiency is one of the most reliable tells of
machine prose. Human-experienced narration tolerates loose ends — not from
sloppiness, but because a consciousness does not know which of its
observations will matter.

## Restraint principles

1. **Theme blindness.** Characters do not know the author's theme. The
   narration must not recognize symbolism, thematic parallels, narrative
   irony, or future significance unless the POV character would realistically
   notice them.
2. **Unrecognized significance.** Important events may pass without the POV
   recognizing their importance. Do not foreshadow every important element
   with obvious emphasis; a major future event may first appear ordinary.
3. **Not every setup needs payoff.** Allow details that lead nowhere. Do not
   force: detail → foreshadowing, detail → plot relevance, detail → symbolic
   meaning, detail → later payoff. Some information exists because a
   character noticed it.
4. **Dead-end information.** Mundane objects, environmental details, casual
   remarks, irrelevant thoughts, social observations — permitted without
   consequence. Do not remove every dead end in the name of efficiency.
5. **Non-closure.** Not every scene must end with revelation, emotional
   resolution, a thematic statement, or a hook. A scene can end because the
   task ends, the conversation ends, someone leaves, attention shifts, an
   interruption occurs, or the character simply moves on.

## Motivated cognitive texture

The following are allowed — never as random decoration, always emerging
from the cognitive state:

- **Cognitive interruption**: irrelevant thoughts, sudden associations,
  intrusive concerns, attention shifts.
- **Mid-thought correction**: initial thought → correction → new
  interpretation. Do not overuse.
- **Unfinished thought**: interrupted or abandoned reasoning. Not every
  thought resolves.
- **Unnecessary remarks**: casual observations, mild complaints, passing
  judgments with no plot function.
- **Natural repetition**: motivated by uncertainty, emphasis, emotional
  fixation, memory, misunderstanding, or self-reassurance — never
  meaningless repetition as a humanity trick.

## COGNITIVE_BEHAVIOR_AUTHENTICITY

A human cognitive behavior (self-correction, irrelevant thought, memory
slip, unfinished sentence, repetition, and every other entry in the
"Motivated cognitive texture" list above) may appear ONLY when supported
by the character's cognition: their cognitive profile, emotional state,
attention, memory, social context, current goal, distraction load,
personality, scene pressure, familiarity, or interpretation pattern.
No cognitive support → no behavior. **Model cognition, not defects.**

Explicitly PROHIBITED as random insertions:

- typos and grammatical mistakes (production errors, not cognition);
- arbitrary fragments that interrupt nothing and resume nothing;
- random contradictions with no belief-conflict source;
- random memory errors with no memory-model source;
- random topic shifts with no attention-shift cause;
- random repetition with no uncertainty / emotion / fixation cause;
- random ambiguity with no genuine uncertainty behind it;
- fake uncertainty ("perhaps", "maybe") with nothing actually uncertain.

A defect is a writing artifact; a cognitive behavior is evidence of a
mind. When a texture element appears, the cognitive state must name its
cause — exactly as `agents/cognition-agent.md` §4 demands a stated cause
for every included behavior.

## Narrative optimization control

Actively avoid excessive optimization. Flag patterns such as: perfectly
timed revelations, perfectly relevant observations, perfectly efficient
dialogue, perfectly balanced description, perfectly obvious symbolism,
perfectly smooth transitions, perfectly resolved scenes.

The goal is not messy prose. The goal is to prevent artificial narrative
efficiency. **Do not destroy good prose**: if a sentence is clear,
character-consistent, cognitively justified, stylistically appropriate, and
grammatically sound, do not change it merely because it is polished. The
objective is believable consciousness, not imperfection.

## The weakness targets (as mechanisms, not a checklist)

The framework addresses common LLM failures — explaining what the POV would
not explain, perfect memory, unbroken attention, perfectly relevant thoughts,
perfect emotional self-awareness, over-cooperative dialogue, smooth
transitions, verbatim-memory bias, re-describing familiar things, forcing
every detail to matter, visible theme, collapsed epistemic layers, authorial
hindsight, uniform rhythm, and the rest — **as cognitive mechanisms** (the
files in this directory), never as a per-scene checklist. Per the negative
constraint: the system must *allow* these human behaviors to emerge when
justified, not *require* them in every chapter. Requiring all of them would
itself be artificial.
