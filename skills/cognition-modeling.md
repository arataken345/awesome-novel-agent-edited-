# Cognition Modeling SOP

Standard operating procedure for `cognition-agent`. Read with the knowledge
files in `knowledge/cognition/` — this SOP is the procedure; those files are
the theory.

## Step 1 — Establish story truth

Read the canon files (`settings/world-setting.md`, `settings/timeline.md`)
and the chapter outline. Write down, privately, what is actually true in
each scene. This is STORY TRUTH. It never appears in the cognitive state as
character knowledge unless the character holds it. Keep it separate from
everything that follows.

## Step 2 — Build the knowledge lattice (per scene)

For each scene, fill:

- **READER KNOWS**: what previous chapters + this chapter so far have shown.
- **POV KNOWS**: facts the POV character holds at this moment. Sources:
  direct perception in-scene, memory, or previously established knowledge.
- **OTHERS KNOW**: per relevant character, what they know (the POV may not).
- **HIDDEN FORCES**: active but unrevealed elements, or "none".
- **WITHHELD**: fact / withholder / why withheld / intended payoff.

Cross-check: nothing in POV KNOWS may contradict canon or require
information the character never received.

## Step 3 — Fill the cognitive state (per scene)

Use all applicable fields. Omit the rest — never pad.

- `known_facts` / `unknown_facts`: crisp lists.
- `beliefs`: what the character holds true (flag any that are wrong).
- `suspicions`, `guesses`: marked as such, with confidence.
- `memories`: each with a fidelity tag
  (exact/semantic/partial/fuzzy/uncertain/misremembered/
  emotionally_distorted/forgotten/suppressed) and, for anything below
  `semantic`, a cause.
- `memory_uncertainty`: what the character is unsure they remember.
- `attention`: map salient elements to
  PRIMARY/SECONDARY/PERIPHERAL/IGNORED/ACTIVELY_AVOIDED, each with a cause
  (goal, emotion, habit, threat, familiarity, fatigue...).
- `current_goal`, `current_concern`: what the character wants right now and
  what weighs on them.
- `emotional_state` + `emotional_awareness`: the feeling AND how much of it
  the character recognizes (recognize / sense vaguely / mislabel /
  rationalize / deny / bodily-only / delayed).
- `interpretations` / `misinterpretations`: meaning assigned to observations;
  for misinterpretations, record story truth separately.
- `blind_spots`: what the character cannot see about the situation or
  themselves, and why.
- `social_assumptions`: what the character assumes about others' intentions
  (marked as assumptions, never facts).
- `current_distractions`: background concerns that may intrude.
- `associations`: the character's associative hooks relevant to this scene
  (profession, hobbies, fears, habits — for metaphor sourcing downstream).
- `familiarity`: what is familiar here (→ compressed perception) vs new
  (→ heightened attention).
- `cognitive_noise`: pending tasks, physical discomfort, recent memories —
  raw material the narrator-voice layer may surface.

## Step 4 — Tag epistemic layers

For each plot-relevant element, assign one of: FACT, OBSERVATION, MEMORY,
BELIEF, GUESS, SUSPICION, RUMOR, INTERPRETATION, MISINTERPRETATION,
UNCERTAINTY, UNKNOWN. If an element would need to *change* layers to serve
the scene, that is a red flag — recheck the lattice instead of upgrading it.

## Step 5 — Salience map

List notable elements with two independent ratings:

- `story_importance`: HIGH / MEDIUM / LOW
- `character_salience`: HIGH / MEDIUM / LOW

Where they diverge, note the divergence explicitly — it is a feature, not
a bug. The narrator-voice layer uses it to calibrate description density.

## Step 6 — The "why" audit

For every non-trivial entry, answer: *Why would this character do this?
Notice this? Remember this? Misunderstand this? Focus on this?* If there is
no character-specific reason, remove the entry.

## Step 7 — Write the file

Write `.agent/cognition/vol-{N}-ch-{M}.md` with one `## Scene` section per
scene containing the lattice, the cognitive state, epistemic tags, and the
salience map. Keep it compact — downstream agents read this under token
pressure. Structured state, not prose.
