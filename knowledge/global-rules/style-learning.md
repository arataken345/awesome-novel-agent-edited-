# Style Learning

## How observed style becomes rules

When analyzing the user's existing writing or explicit statements:

- An **explicit statement** ("I never use semicolons") becomes a **hard
  rule** (`source: user_explicit`, `strength: hard`).
- A **statistical observation** ("the user rarely uses em dashes") becomes
  a **soft tendency** (`source: observed_style`, `strength: soft`).

Do not convert every corpus statistic into a hard rule. Do not let an
observed tendency silently outrank an explicit instruction — if they
conflict, the explicit instruction wins, always.

## What the style profile records

Persist the user's style as observable structural properties (not vibes):

- punctuation preferences and forbidden punctuation
- paragraph architecture and dialogue structure
- narrative distance and POV behavior
- description density and dialogue density
- rhythm preferences
- em-dash frequency (as a measured tendency)

Never reduce the profile to "write naturally" or "write like the user".
The profile is structural and checkable.

## Style vs character

Final prose combines: user writing style + character cognition + POV
narrative filter + scene requirements + project canon. It must NOT become
a user-style template that makes every character narrate identically. The
user's prose style stays recognizable while the consciousness behind the
narration changes — that separation is the entire point of the
cognition → filter → style pipeline.
