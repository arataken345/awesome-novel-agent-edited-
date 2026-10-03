# Narrator-Voice Filter SOP

Standard operating procedure for `narrator-voice-agent`. Read with
`knowledge/narrator-voice/` — this SOP is the procedure; those files are
the theory.

## Step 1 — Gather inputs

- Read the chapter's cognitive state:
  `.agent/cognition/vol-{N}-ch-{M}.md`.
- Read the POV character's narrator voice profile from
  `settings/character-setting/{pov}.md` ("Narrator Voice Profile"). If the
  section is missing, derive a minimal profile from the character setting
  (temperament, sensory habits, metaphor sources evident in the setting
  text) and mark every derived field `[provisional]`.
- Read `settings/global-rules.md` for style constraints (they shape the
  filter's expression guidance, never its cognition).

## Step 2 — Deterministic assembly

Extract the profile (§43 fields) and the scene's cognitive state (§5
fields) into two JSON files, then run:

```
python3 <tools>/pov_filter.py --profile /tmp/profile.json --state /tmp/state.json
```

This produces the 16-field filter skeleton per the §45 contract. The tool
tolerates missing fields — do not pad the JSON to fill them.

## Step 3 — Qualitative refinement

Adjust, without breaking the contract fields:

1. **Emotional modulation**: from the scene's `emotional_state`, shift
   emphasis per `distance-modulation.md` (what gets noticed more/less,
   expand vs compress, certainty shift).
2. **Scene-relevant associations**: replace generic association patterns
   with the associations actually live in this scene.
3. **Theme blindness**: add to WHAT_TO_AVOID_EXPLAINING anything the scene
   tempts the narrator to explain (symbolism, irony, future significance)
   that the POV would not notice.
4. **Salience check**: where `story_importance` and `character_salience`
   diverge, make sure the filter follows character salience.

## Step 4 — Closed-POV verification

For each field, ask: *could the POV character know/notice/feel this at this
moment?* Any field that requires narrator-privilege knowledge is rewritten
or cut. One consciousness per scene; handoffs only at scene breaks.

## Step 5 — Write the filter

Append `## POV NARRATIVE FILTER` to the scene's section in the cognition
file, with the 16 fields. Keep each field to a few lines — the
prompt-crafter will sparsely inject this into the writing prompt.
