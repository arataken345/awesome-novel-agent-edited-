# Global Rule Model

## Rule schema

```yaml
rules:
  - name: "no-colon-in-prose"        # machine-readable id
    statement: "No colons in novel prose."   # human-readable
    scope: user_global              # user_global | project_canon | chapter | scene | character
    source: user_explicit           # user_explicit | project_canon | observed_style | agent_default
    strength: hard                  # hard (deterministic fail) | soft (tendency)
    explicit: true                  # was this explicitly declared?
    by_user: true                   # was this declared by the user?
    applies_to: prose               # prose only — never code/config/prompts/docs
    rationale: "The user never uses colons in prose."
```

## Strength

- **hard**: deterministic validation failure. The writer must revise.
  Example: no colons, no semicolons in prose.
- **soft**: corpus-level tendency. Tracked, warned on excess, never a
  hard fail. Example: em-dash rarity.

Do not promote a soft tendency to hard without an explicit user statement.
Do not demote a hard rule without an explicit user statement.

## Overrides

```yaml
overrides:
  - rule: "no-colon-in-prose"
    scope: chapter
    chapter: "vol-1-ch-12"
    value: "allowed"
    explicit: true
    by_user: true
    reason: "User explicitly permitted colons for this chapter."
```

Resolution: `tools/pov_filter.py resolve_rule`. Direct user commands win;
then explicit narrower-scope user overrides (§54); then the §48 order.
Non-explicit entries never override.

## Prose-only scoping

Global prose rules apply ONLY to novel prose. They never apply to: source
code, JSON, YAML, configuration, metadata, agent prompts, documentation,
Git files. Validators must mask non-prose content before checking
(see `tools/check-prose-en.py mask_non_prose`).
