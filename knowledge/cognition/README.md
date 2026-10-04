# Cognitive Humanization — Knowledge Index

## Why this layer exists

The framework's writer is a language model. Left to itself, a language model
writes from the position of *everything it knows about the story*: it perceives
like a camera, remembers perfectly, interprets correctly, explains causally,
and distributes attention according to plot importance. The result reads as
*optimized* — every sentence earning its place, every detail paying off, every
character understanding exactly as much as the scene needs.

Real human consciousness does none of that. A person perceives selectively,
remembers semantically, misinterprets constantly, feels without understanding,
notices the wrong things, and forgets what the plot needs them to remember.
The purpose of this knowledge layer is to give the pipeline a **causally
motivated model of a specific character's cognition** — so that narration
emerges from what the POV character can experience, not from what the model
knows about the story.

This is not a license to write badly. Every file below repeats the same
discipline: **a cognitive behavior is only used when the character, the scene,
and the cognitive state justify it.** Random mistakes, random distractions,
and random forgetfulness are forbidden — they are just as artificial as
perfect optimization.

## The five responsibilities (never collapse these)

1. **Cognitive humanization** (this directory) — how a character experiences
   information: knowledge limits, attention, memory, interpretation, emotion,
   social perception.
2. **POV narrative filter** (`knowledge/narrator-voice/`) — what the narration
   is capable of presenting, given the cognitive state.
3. **Narrator voice** (`knowledge/narrator-voice/`) — how the narration sounds
   through this specific character (distinct from what the character knows and
   from how the character speaks).
4. **Global writing rules** (`knowledge/global-rules/`) — the user's persistent
   prose style: punctuation, paragraph architecture, rule hierarchy.
5. **Humanizer / humanity audit** (`knowledge/humanizer/` + reader) — evaluates
   whether the output still feels mechanically optimized. Auditing is
   downstream of creation; it never generates cognition.

## Files in this directory

| File | Covers |
|---|---|
| `epistemic-layers.md` | The 11 epistemic layers (FACT → UNKNOWN); information asymmetry: STORY TRUTH vs POV KNOWLEDGE vs READER KNOWLEDGE; the per-scene knowledge lattice |
| `attention-model.md` | PRIMARY/SECONDARY/PERIPHERAL/IGNORED/ACTIVELY_AVOIDED attention; attention blindness; uneven salience (`story_importance` vs `character_salience`); wrong focus; incomplete perception |
| `memory-model.md` | Imperfect memory types; semantic-over-verbatim default; motivated misremembering; STORY MEMORY ≠ CHARACTER MEMORY |
| `interpretation-model.md` | Interpretation error; narrative self-blindness; emotional self-awareness levels; per-character emotional vocabulary; wrong beliefs; causal uncertainty |
| `social-cognition.md` | Social misalignment; non-cooperative dialogue; different models of the same character; inferred (never factual) social states |
| `narrative-restraint.md` | Theme blindness; unrecognized significance; dead-end detail; non-closure; motivated interruption/correction/unfinished thought; narrative optimization control |
| `registries.md` | Unresolved-detail registry and delayed-meaning registry: track without forcing payoff or closure |

## How it is used

1. `cognition-agent` (new) reads the chapter outline, character settings, and
   canon, then writes a per-scene **cognitive state** to
   `.agent/cognition/vol-{N}-ch-{M}.md`.
2. `narrator-voice-agent` (new) converts the cognitive state into a compact
   **POV narrative filter**.
3. `prompt-crafter` injects the filter into the writing prompt using **sparse
   injection**: only the active POV, relevant memories/beliefs, current
   attention/emotion/concerns, relevant blind spots and associations, and the
   applicable global rules. Never the whole profile.
4. `writer` writes from the prompt. `humanizer` cleans expression. `reader`
   (extended with the humanity flag taxonomy) audits situatedness.

## Language note

The framework's historical knowledge files are written in Chinese. This
directory is written in English: it serves English-language prose generation,
and its primary specification (the implementation command) is English. The
concepts are language-independent; the examples are English.
