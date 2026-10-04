# Human-Cognition Architecture

Why the framework models character cognition, assembles per-scene POV
filters, and enforces global writing rules — and why each piece exists in
the form it does.

## 1. The core problem

A large language model generates from statistical plausibility over its
whole context. Given a chapter outline, it naturally produces prose in
which the narrator knows everything relevant, every character articulates
feelings with equal precision, every observation pays off, and every
motivation is stated. This is **omniscient-model prose**: fluent, correct,
and inhuman. The pipeline's entire cognition layer exists to answer one
question per sentence: *who could know this, and how would they know it?*

## 2. Why 11 epistemic layers instead of "knows / doesn't know"

Binary knowledge tracking fails because human knowledge is graded: things
known as fact, things reasonably inferred, things merely guessed, things
actively avoided, things genuinely absent. The 11-layer lattice
(FACT → UNKNOWN, in `knowledge/cognition/epistemic-layers.md`) exists so
the writer can be told precisely *how* a detail may appear — directly
stated, hedged, or not at all — instead of guessing. The HEDGED layer is
the most important: it is where human prose lives ("she seemed tired",
"he took that as agreement"), and the validators deliberately never flag
hedged perception.

## 3. Why information asymmetry is a first-class object

Most plot interest comes from characters knowing different things. The
per-scene knowledge lattice (reader / POV / others / hidden) is tracked
explicitly because the model's default is to collapse it: it will hand
the POV character knowledge that belongs to the reader or the hidden
column whenever that makes the paragraph read more smoothly. Explicit
asymmetry tracking makes the smooth wrong choice visible.

## 4. Why an attention model (and not just "describe the scene")

Models describe what is story-important. Humans notice what is
salient *to them*: the exit if they are anxious, the smell if they are a
cook, the rival's hands if they are jealous. The attention model
(PRIMARY → ACTIVELY_AVOIDED) exists because `story_importance` and
`character_salience` are different axes, and the default generation
collapses them into one. "Never expand by story importance alone" is the
operational sentence.

## 5. Why blindness is modeled, not just knowledge

A character is defined as much by what they systematically do not see as
by what they know. Blind spots (self-flattering interpretations, topics
actively avoided, questions never asked) are first-class because the
model's instinct is therapeutic clarity: it heals blind spots by having
characters notice them. A modeled blind spot is a constraint the writer
must not violate; an unmodeled one is invisible and gets violated by
default.

## 6. Why memory has 9 fidelity levels

Humans remember semantics, not transcripts; they remember gist, emotional
residues, and wrong details with high confidence. A model given a story
bible will quote it verbatim in characters' heads. The 9 fidelity levels
exist to license *wrongness*: a character may misremember, and the
misremembering must be the one the writer uses. STORY MEMORY (canon, exact)
and CHARACTER MEMORY (lossy, personal) are stored separately for exactly
this reason.

## 7. Why interpretation is modeled separately from perception

Two characters can perceive the same event and interpret it oppositely.
The interpretation-error model exists because the model's default is
correct interpretation: the narrator quietly adopts the interpretation
that the plot needs. Modeling each character's interpretation system —
and its characteristic errors — forces the prose to commit to a possibly
wrong reading and stay in it.

## 8. Why self-blindness is a feature, not a bug

Characters do not see themselves clearly, and do not narrate themselves
clearly. The model loves psychology-telling ("he realized his fear of
abandonment made him cling"). The self-blindness model exists to keep
the narration at the character's actual level of self-knowledge — which
is usually lower than the reader's. The narrator may know more than the
character only through distance modulation (§74–75), never through the
character's own mouth.

## 9. Why emotional self-awareness has levels

"She was angry" is one of dozens of possible renderings, and the right
one depends on the character's awareness level: bodily-only (jaw
tightens), vague (something is off), mislabeled (calls fear "annoyance"),
recognized (names it), denied (rationalizes it away). The filter's
EMOTIONAL_FRAMING honors the level because upgrading awareness is the
model's favorite shortcut to "depth" — and it reads as mechanical.

## 10. Why wrong beliefs are protected

A character's wrong belief is plot fuel and human texture. The model's
instinct is to correct it — through narration, through another
character's timely exposition, through the sheer pressure of coherence.
Dead-ends are modeled and protected because premature correction is one
of the most reliable signatures of AI prose. The registry records them;
the filter forbids explaining them away.

## 11. Why social cognition gets its own model

People model other people constantly, badly, and strategically:
guardedness, evasion, face-saving, status calculation. The social model
(SPECIALTY / JURISDICTION / GUARDEDNESS / EVASION, plus narrator color)
exists because dialogue between model-generated characters defaults to
cooperative information exchange — everyone answering the question asked.
Humans deflect, perform, and misunderstand on purpose.

## 12. Why narrative restraint is a system, not taste

Theme blindness (characters don't see the theme), dead-ends, non-closure,
optimization control — these are not stylistic preferences but structural
defenses against the model's optimization pressure: it optimizes for
reader comprehension, thematic clarity, and satisfying arcs. Restraint
exists to let the prose be worse at explaining and better at being human.
Non-closure is explicitly permitted; the unresolved registry exists so
threads can stay open without being lost.

## 13. Why a deterministic POV filter (16 fields)

The filter (`knowledge/narrator-voice/filter-spec.md`, §45) is a contract
between the planner's knowledge and the writer's prose. It is 16 fields
because those are the decisions a writer needs per scene: what to
notice, what to ignore, what not to explain, what the character thinks
things mean, what they don't know, emotional framing, density, distance.
It is deterministic (`tools/pov_filter.py build_filter`) because the same
profile + state must always produce the same filter — an LLM re-deriving
it each time would drift.

## 14. Why the filter is injected sparsely (≤5 constraints)

A prompt stuffed with 16 fields of constraints produces prose that
obeys the letter and murders the rhythm. Sparse injection exists because
constraints have a cost: every injected rule narrows the writer's
freedom, and past ~5 the prose starts sounding like it is checking boxes
— which is itself an AI tell. Inject the load-bearing constraints only;
the rest is enforced downstream by validators and the reader.

## 15. Why the writer's context is quarantined

The writer reads only the writing order, the prompt, and the genre
setting — never the full cognitive state, never the canon. This is
deliberate: if the writer can see the hidden column of the knowledge
lattice, it will leak. The pipeline is designed so that *not knowing* is
structural, not a matter of the writer's discipline. Prompt-crafter
injects only the current scene's POV filter; other scenes' cognition is
simply absent from context.

## 16. Why global rules are hard/soft, not all-or-nothing

Some user rules are identity (no colons, no semicolons — deterministic
failures). Some are tendencies (em-dash rarity — corpus-level warnings).
Treating a tendency as a ban produces mechanical avoidance prose; treating
a ban as a tendency produces drift. The hard/soft distinction exists
because the enforcement mechanism must match the rule's nature, and
because only explicit user statements change a rule's strength — never
corpus statistics, never agent convenience.

## 17. Why rule precedence is deterministic (§48/§54)

When rules conflict, someone must win, and "the model decides" is not an
answer. The 9-level hierarchy with explicit-narrower-scope-wins exists so
conflicts resolve the same way every time, and so that no lower rule can
silently override a higher one. The critical invariant: overrides are
never inferred. A chapter that happens to use colons is not an override;
only an explicit user statement is.

## 18. Why validators are prose-only by construction

Global rules apply to novel prose — never to code, config, JSON, prompts,
or docs. The checker masks non-prose content before validating because a
colon in a URL failing a prose check would train everyone to ignore the
checker. A validator that cries wolf about non-prose gets disabled; a
disabled validator is worse than none, because then the real violations
pass silently.

## 19. Why the reader audits but never judges

The reader has the 15-flag humanity taxonomy (H1–H15) and no pass/fail
power. This separation exists because judgment corrupts observation: a
reviewer who must deliver a verdict starts grading toward the verdict.
The reader's job is to notice — "this paragraph reads like the narrator
knows something the character couldn't" — and hand that noticing to the
director, who decides. Advisory-only is a structural choice, not politeness.

## 20. Why two new agents instead of extending old ones

`cognition-agent` and `narrator-voice-agent` were created because no
existing agent owns their responsibility: chapter-planner owns plot,
prompt-crafter owns assembly, writer owns prose. Cognition modeling
(building the per-scene knowledge lattice and cognitive profiles) and
filter assembly (turning profile + state into the 16-field contract) are
distinct skills with distinct inputs. Where a responsibility already
existed — the reader's harsh review, humanizer's machine screening, the
updater's archive duties — the command extended rather than duplicated.

## 21. Why the registries live with the updater

Unresolved details and delayed meanings are discovered during writing but
only *confirmed* at archive time, when the whole chapter exists. The
updater owns the registry because it is the last agent to see the finished
chapter, and because registration must never feed back into the writing
prompt (that would create automatic foreshadowing — the registry's
existence warping the prose toward telegraphing). One-way flow: writing →
registry, never registry → prompt.

## 22. How this prevents omniscient-model prose

The mechanism is layered, and each layer catches what the previous one
misses:

1. **Cognition modeling** defines what the POV character can know, notice,
   remember, and misinterpret — per scene, in 11 epistemic layers.
2. **Filter assembly** turns that into 16 concrete constraints, assembled
   deterministically so they don't drift.
3. **Sparse injection** gives the writer only this scene's filter — the
   writer's context is quarantined from canon, other scenes, and the
   hidden column.
4. **Global rules** constrain the prose's shape (punctuation, dialogue
   architecture) deterministically; violations fail the build.
5. **Anti-ai screening** runs the machine checks (both languages) plus the
   Gate A–G review, with hedged perception explicitly protected.
6. **Humanity audit** has the reader flag the 15 behavioral symptoms of
   mechanical output — advisory, so observation stays honest.
7. **The registry** keeps unresolved threads open without losing them and
   without forcing payoff.

No single layer is sufficient. The model's omniscience is a strong prior;
it takes a pipeline of constraints — some deterministic, some advisory,
all explicit — to hold a single human consciousness per scene.

## 23. Why narrative distance is presentation, not epistemic access

(To be precise about §8's shorthand: distance modulation never grants the
narrator knowledge.) Narrative distance controls *presentation* distance —
descriptive density, abstraction level, emotional rendering distance,
sentence shape. It never controls *epistemic permissions*: what the POV
knows, observes, or infers; which secrets are accessible; what future
information is possessed. This distinction exists because the model's
favorite failure under "distant" narration is a quiet permission upgrade:
the cooler the diction, the more the prose starts stating other minds,
hidden causes, and future significance as fact. The invariant
(`CLOSED_POV_EPISTEMIC_INVARIANT`, in
`knowledge/narrator-voice/distance-modulation.md`) holds the line: even at
`narrative_distance=distant`, everything asserted must trace to the POV's
own epistemic layers. Distance may compress a thought; it may never invent
knowledge.

## 24. Why sparse filter injection is 0–5 — a ceiling, not a quota

§14 explains why injection is sparse. The hardening adds the second half:
**5 is a ceiling, never a quota.** A quota invites manufacturing —
prompt-crafter padding a scene with three load-bearing constraints and two
decorative ones to "reach five", which the writer then obeys at the cost
of rhythm and sense. The rule (`SPARSE_FILTER_RULE`, in
`skills/prompt-crafting.md` Step 1.6) is: inject 0–5, inject only what
materially changes how the scene is written, and if three constraints do
the work, inject exactly three. Zero is legal. An under-constrained prompt
is enforced downstream by validators and the reader; an over-constrained
one corrupts the prose at the source, where no downstream stage can
repair it.

## 25. Why cognitive behaviors must be motivated, never decorated

Restraint (§12) permits loose ends; the authenticity rule
(`COGNITIVE_BEHAVIOR_AUTHENTICITY`, in
`knowledge/cognition/narrative-restraint.md`) governs *texture*. A
self-correction, an irrelevant thought, a memory slip, an unfinished
sentence — each is allowed only when the cognitive state names its cause:
attention, emotion, distraction, memory, social pressure, interpretation
pattern. The prohibition list (typos, grammatical mistakes, arbitrary
fragments, random contradictions, random memory errors, random topic
shifts, random repetition, random ambiguity, fake uncertainty) exists
because the fastest way to fake "human" is to sprinkle defects — and
defects are exactly what a real consciousness does not produce. A mind
produces errors *with causes*; a defect generator produces errors with
none. "Model cognition, not defects" is the operational sentence:
when a texture element appears, the cognitive state must name its cause,
exactly as cognition-agent §4 demands.

## 26. Why the benchmark philosophy is behavioral differentiation

(The benchmark agent owns the benchmarks; this states the philosophy they
are built to.) A cognition benchmark that scores style — "does this read
like a human voice?" — rewards decoration: the same defect-sprinkling §25
prohibits. The framework's benchmarks must score *behavioral
differentiation*: given the same scene, do two different cognitive states
produce observably different attention, interpretation, and restraint?
Does the filter change what the narration is allowed to know? Stylistic
decoration is cheap to imitate and easy to game; behavioral difference —
what is noticed, what is hedged, what is left unsaid — is where the
machinery either works or doesn't.

## 27. Why Writer Behavioral Validation exists (and what it does not prove)

Filter-level tests prove the cognition layer *produces* different
artifacts per POV. That is necessary but insufficient: a filter that
differs beautifully on disk proves nothing if those differences never
survive the prompt-crafter and the Writer into narrative realization.
The Writer Behavioral Validation layer (`tools/test_writer_behavioral.py`)
closes the remaining gap in the chain:

    cognitive state -> POV filter -> prompt crafter -> Writer -> realization

**What it proves.** That cognitively different POV conditions — same
story, same scene, same Writer path, only the cognitive state changed —
produce meaningfully different narrative realization (attention order,
interpretation, emotional framing, familiarity compression, social
reading) while preserving story truth, closed-POV epistemic boundaries,
and the global prose rules. The proof is structural: a fixed,
POV-agnostic deterministic adapter renders each POV's realization from
*only* the prompt document, so any cross-POV difference demonstrably
originates in the prompt (hence in cognition), never in the renderer.

**Deterministic vs model-backed.** Level A runs always, with no API key,
no network, no model: it verifies cognitive state -> filter -> prompt
and that Writer *input* differs correctly. Level B (`--model`) is opt-in
and reports an honest SKIP — this repository defines the Writer as a
markdown agent role executed by an external harness and exposes no
model interface, so there is nothing to invoke. A skipped Level B is
not a failure, and no prose is ever fabricated to pretend otherwise.

**Behavioral dimensions.** Eight are checked semantically: attention
differentiation (output reflects WHAT_TO_NOTICE / WHAT_TO_IGNORE),
interpretation differentiation (beliefs preserved as POV beliefs; the
benchmark detects collapse into a single authorial truth), emotional
framing (behavioral consequence, never a required emotion word),
association differentiation (may shape comparison; absence is valid),
familiarity compression (familiar -> compressed, unfamiliar -> noted,
situation-dependent), social cognition (same dialogue, different
reading; dialogue never rewritten to manufacture difference),
self-blindness (the true state vs the character's awareness, protected),
and epistemic preservation (narrative distance never grants epistemic
permission).

**Semantic comparison philosophy.** No Levenshtein, no token overlap, no
cosine similarity as a behavioral metric: two good POV realizations may
share many words, two bad ones may differ dramatically. Checks compare
field-level semantic content — which beliefs are tagged to which POV,
which items are omitted, which unknowns stay unknown. Same observation
is not failure (two POVs may both notice the door); different wording
is not success. Negative controls (a deliberately smuggled secret, a
forged asserted unknown) prove the detectors are not vacuous.

**Why no humanity score exists.** A number like "humanity: 87%" would
turn the benchmark into an optimization target, and optimizing for
looking human produces exactly the defect-sprinkling §25 prohibits.
The benchmark reports PASS / FAIL / ADVISORY with concrete evidence per
dimension. ADVISORY is never a failure: it marks a cognitively optional
behavior the scene did not require.

**Why unsupported imperfections are rejected.** A typo, fragment, or
memory error with no cognitive cause is not humanity — it is noise the
model added. The benchmark structurally asserts that every realization
string derives from the prompt document (or is a fixed structural
label): the adapter invents nothing, so any unsupported defect would
have to come from the architecture, where it would be caught.

**Limitations of model-backed testing.** Even with a real model, the
benchmark could not prove prose is human-written — only that
cognitively different conditions change realization without violating
constraints. Model outputs also vary across runs, providers, and
temperatures, so Level B must use semantic acceptance criteria, never
exact-sentence assertions, and must always report model, provider,
runtime, and seed.

The mandatory distinction, stated plainly:

«The benchmark does not prove that generated prose is human-written.»

It proves only that:

«cognitively different POV conditions can survive the architecture into
narrative realization without violating epistemic and structural
constraints.»

## 28. Why the tests are organized into four categories

The suites below test different things, and conflating them produces
false confidence (a contract test passing is not proof the behavior
survives; a behavioral test passing is not proof the prose is human).
Each category has a distinct verdict vocabulary, and none of them
produces a "humanity score" — **no humanity score exists anywhere in
this repository**, and **ADVISORY ≠ FAIL** (an ADVISORY is a flagged
judgment call for a human, never a red gate).

**CONTRACT tests** — data and architecture invariants. Deterministic,
always run, fail hard. They assert what the machinery *must* do or
never do, independent of any generated prose:
closed-POV epistemic boundaries (`tools/test_cognition.py`),
the closed-POV invariant plus the sparse-injection 0–5 ceiling plus
prompt-level knowledge quarantine (`tools/test_cognition_hardening.py`),
filter differentiation across POVs, and memory isolation — the
state→filter→prompt memory links with no phantom injection
(`tools/test_memory_path.py`).

**BEHAVIORAL tests** — generated behavior, not invariants. They ask
whether cognitive differences *survive* into artifacts: attention and
interpretation differentiation across POVs, memory-uncertainty
survival (degraded recall never restored to canon wording, hedges
never upgraded — `tools/test_cognition_benchmark.py`, nine benchmarks
reporting PASS / FAIL / ADVISORY with one sentence of evidence), and
the cognitive-state→filter→prompt→realization chain
(`tools/test_writer_behavioral.py` Level A: fully deterministic, no
model, no network).

**PRESERVATION tests** — downstream stages must not destroy what
cognition built. The anti-AI pass and the reader-rewrite step are
explicitly forbidden from stripping hedged perception or upgrading
epistemic layers; the preservation suite (`tools/test_cognition_preservation.py`,
added in this integration-hardening pass) guards those seams.

**LIVE INTEGRATION tests** — a real model, optional, clearly marked.
Level B of `tools/test_writer_behavioral.py` (`--model`) is the only
live-model surface: opt-in, reports an honest SKIP when no model
runtime exists, and is never part of CI. Nothing in this category may
be required for a green build, and no prose is ever fabricated to
pretend a live run happened.
