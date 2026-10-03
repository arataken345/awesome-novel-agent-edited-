# Global Writing Rules

Persistent prose rules for this project. Shipped with framework defaults
(reflecting explicit user style); edit freely — your edits are
`user_explicit` and outrank everything except your direct commands.

Precedence (highest first): your explicit command > rules below >
project canon > chapter/scene/character rules > agent defaults > model
habits. A narrower-scope override you declare explicitly wins over a
broader rule; overrides are never inferred.

```yaml
rules:
  - name: no-colon-in-prose
    statement: "No colons (:) in novel prose."
    scope: user_global
    source: user_explicit
    strength: hard
    explicit: true
    by_user: true
    applies_to: prose

  - name: no-semicolon-in-prose
    statement: "No semicolons (;) in novel prose."
    scope: user_global
    source: user_explicit
    strength: hard
    explicit: true
    by_user: true
    applies_to: prose

  - name: em-dash-rarity
    statement: "Em dashes (—) extremely rare: roughly 1-5 across 5-10 chapters."
    scope: user_global
    source: user_explicit
    strength: soft
    explicit: true
    by_user: true
    applies_to: prose

  - name: one-dialogue-per-paragraph
    statement: "One paragraph contains one contiguous dialogue unit."
    scope: user_global
    source: user_explicit
    strength: hard
    explicit: true
    by_user: true
    applies_to: prose
```

## Overrides (explicit only)

```yaml
overrides: []
# Example:
# - rule: no-colon-in-prose
#   scope: chapter
#   chapter: "vol-1-ch-12"
#   value: allowed
#   explicit: true
#   by_user: true
#   reason: "Author explicitly permitted colons for this chapter."
```

Add entries here only for rules you explicitly choose to override at a
narrower scope. Never add an override on an agent's behalf.
