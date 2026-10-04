# Global Writing Rules — Knowledge Index

## Why this layer exists

Every novel project accumulates prose rules: the user's punctuation habits,
paragraph architecture, dialogue conventions, hard bans, style tendencies.
Without a dedicated layer, these rules scatter across agent prompts, memory
entries, and tribal knowledge — where they get duplicated, contradicted, or
silently overridden by a lower-level default. This layer makes the rules
**persistent, sourced, scoped, and precedence-ordered**.

## The hierarchy (§48)

Highest first:

1. **user_explicit** — an explicit user command (any scope). Absolute top.
2. **user_global** — the user's persistent global rules
   (`settings/global-rules.md`).
3. **project_canon** — locked canon facts that constrain expression.
4. **chapter** — chapter-level rules.
5. **scene** — scene-level rules.
6. **character** — character-level rules (including narrator voice profile).
7. **observed_style** — learned tendencies. Soft only: an observed
   statistical tendency must NEVER outrank an explicit user instruction.
8. **agent_default** — framework/agent defaults.
9. **model_default** — base model habits. Lowest; the layer exists largely
   to keep these out.

A lower level must never silently override a higher one. The deterministic
helper `tools/pov_filter.py resolve_rule` implements this; see
`rule-model.md`.

## Scoped overrides (§54)

If the user explicitly overrides a rule for a narrower scope, the narrower
explicit instruction wins. Example: global "no colons in prose", user says
"this chapter may use colons" → the chapter receives an explicit override.

**Never infer overrides.** A chapter-level mention is not an override unless
explicitly declared as one. When in doubt, the broader rule stands.

## Rule sources (§55)

Every rule records its origin: `user_explicit`, `project_canon`,
`observed_style`, `agent_default`. Priority follows the hierarchy above.
Observed style becoming stronger than an explicit instruction is a bug.

## Files in this directory

| File | Covers |
|---|---|
| `rule-model.md` | Rule schema, hierarchy, sources, scoping, override mechanics |
| `default-rules.md` | The shipped default rule set (user-explicit per the framework spec) |
| `style-learning.md` | How observed style becomes rules: explicit → hard rule, statistical → soft tendency |

## Storage

- Framework: this directory (theory + defaults).
- Project: `settings/global-rules.md` (template shipped in
  `templates/settings/`; user-editable; deployed by `init.py`).
- The `prompt-crafter` injects applicable rules into the writing prompt;
  `humanizer` enforces deterministic ones; `reader` audits style fidelity.
