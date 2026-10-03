# Unresolved-Detail Registry & Delayed-Meaning Registry

## Why

Two opposite failure modes haunt story pipelines. The first is **automatic
closure**: every observation gets explained, every question answered, every
ambiguity resolved — usually immediately, usually by the narrator. The
second is **lost threads**: a detail is planted and the system forgets it
was ever open. This file defines two registries that solve both without
falling into a third trap: forcing every registered detail to pay off.

## Unresolved-detail registry

Tracks, per project (maintained by `updater` at archive time):

- `unresolved_observation` — something a POV noticed but nobody explained
- `unanswered_question` — a question raised in dialogue or thought, unanswered
- `ambiguous_event` — something happened; its meaning is genuinely unclear
- `delayed_significance` — may matter later; currently dormant
- `misinterpreted_event` — the POV assigned a wrong meaning (story truth kept
  separately in canon)
- `unknown_cause` — something happened; the cause is unknown

**Rules:**

1. The registry **prevents automatic closure**. A registered item must not be
   silently explained away by a later narration pass.
2. The registry **does not force payoff**. Registration is not a promise.
   An item may stay unresolved forever. Never let the registry become a
   checklist that the plot must discharge.
3. Entries record: what / where it appeared / whose cognition holds it /
   current status. Nothing more.

## Delayed-meaning registry

For details that *may* later become meaningful — tracked without telling
the writer "this MUST become important" (which would warp the prose toward
telegraphing). Four significance states, kept separate:

- `potential_significance` — could matter; nobody knows yet
- `confirmed_significance` — the story plan confirms it matters (planner-level
  knowledge, never shown to the writer as an instruction to emphasize)
- `character_recognized_significance` — a character has noticed it matters
- `reader_recognized_significance` — the reader has been given enough to
  notice

These must remain separate. In particular, `confirmed_significance` must
never leak into the writing prompt as emphasis guidance — that is exactly
how automatic foreshadowing is born.

## Storage

Project-level file: `settings/unresolved-registry.md` (template shipped in
`templates/settings/`). The `updater` appends entries at archive time from
the chapter's cognitive state and review notes. Entries are never deleted by
agents; the author may retire them explicitly.
