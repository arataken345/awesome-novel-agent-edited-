# Default Global Rules (shipped)

These are the framework's default global rules, reflecting explicit user
style. They ship in `templates/settings/global-rules.md` and are deployed
into every new project by `init.py`. The user may edit them; edits are
`user_explicit` and outrank everything except direct commands.

## 1. Em dash — rare corpus-level tendency (soft)

The user almost never uses "—" in prose.

- Frequency must remain extremely low: roughly 1–5 occurrences across
  5–10 chapters is acceptable.
- This is NOT a ban. Do not mechanically eliminate every em dash; do not
  mechanically insert them. An em dash must earn its place.
- Enforcement: corpus-level tracking with warnings on excess — never a
  deterministic failure.

## 2. Colon — forbidden in novel prose (hard)

The user never uses ":" in novel prose.

- Deterministic validation failure. The writer must revise.
- Prose-only: does not apply to code, JSON/YAML, config, prompts, docs.

## 3. Semicolon — forbidden in novel prose (hard)

The user never uses ";" in novel prose.

- Deterministic validation failure. The writer must revise.
- Prose-only.

## 4. Dialogue paragraph architecture (hard)

One paragraph contains one contiguous dialogue unit.

- Do NOT join two structurally separate dialogue units in one paragraph:
  `"Dialogue," he said, "another dialogue."` (two separate units).
- An interrupted single speech (`"X," she said, "Y."` — one speaker,
  one continuous utterance) counts as one dialogue unit and is allowed.
- Dialogue-only paragraphs are valid:
  `"You're late."` / `"Again."`
- Deterministic validation failure on structural violation.

## Why these four

They are structural, not stylistic preferences: they define the user's
paragraph architecture and punctuation identity. Everything else about style
(voice, rhythm, diction) belongs to the style-distiller cards and the
narrator voice profiles — this layer stays structural.
