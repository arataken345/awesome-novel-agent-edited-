#!/usr/bin/env python3
"""Human-cognition / narrator-voice / global-rules tests (§87).

20 tests: deterministic validator rules (check-prose-en), filter assembly
and rule-precedence contracts (pov_filter), and negative tests proving the
checker never punishes human-cognition behaviors (dead ends, non-closure,
misalignment, silent presence).

Usage: python tools/test_cognition.py
Returns 0 on all pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_util import check, summary, exit_code, load_module

CHECK_EN = load_module(
    "check_prose_en_mod", Path(__file__).resolve().parent / "check-prose-en.py"
)
POV_FILTER = load_module(
    "pov_filter_mod", Path(__file__).resolve().parent / "pov_filter.py"
)


def failures(text, **kwargs):
    return CHECK_EN.check_text(text, **kwargs).failures


def warnings(text, **kwargs):
    return CHECK_EN.check_text(text, **kwargs).warnings


def test_colon_fails():
    fails = failures("He arrived at noon and the room was empty.")
    check("clean prose has no colon failure", not any("Colon" in f for f in fails))
    fails = failures("She opened the box and found a note. It read: Run.")
    check("prose with colon fails", any("Colon" in f for f in fails))


def test_colon_in_code_masked():
    text = "The screen read `error: timeout`. She sighed and kept walking."
    fails = failures(text)
    check("colon inside code is masked (prose-only)", not any("Colon" in f for f in fails))


def test_semicolon_fails():
    fails = failures("He ran fast; she followed close behind.")
    check("prose with semicolon fails", any("Semicolon" in f for f in fails))


def test_em_dash_never_fails():
    text = "\n".join(
        f"He kept walking — block {i} — and never looked back at the empty street."
        for i in range(8)
    )
    result = CHECK_EN.check_text(text)
    check("em dash excess warns", any("dash" in w for w in result.warnings))
    check("em dash never deterministic-fails", not result.failures)


def test_two_dialogues_one_paragraph_fails():
    text = '"I will go," Mara said. "Stay," Jin said. The door stayed open.'
    fails = failures(text)
    check("two speakers in one paragraph fails",
          any("dialogue" in f.lower() for f in fails))


def test_interrupted_speech_allowed():
    text = '"I told you," she said, "it is over." She turned away slowly.'
    fails = failures(text)
    check("interrupted single speech is one dialogue unit",
          not any("dialogue" in f.lower() for f in fails))


def test_pov_headhop_warns():
    text = "Mara knew he was lying. Jin watched her from the doorway quietly."
    result = CHECK_EN.check_text(text, pov="Jin")
    check("head-hop warns", any("head-hop" in w for w in result.warnings))
    check("head-hop never fails", not result.failures)


def test_hedged_perception_never_flagged():
    # Epistemically required marking (epistemic-layers.md HEDGED) is not POV drift.
    text = ("He seemed nervous. She watched his hands and wondered whether "
            "he was hiding something important from everyone.")
    result = CHECK_EN.check_text(text, pov="she")
    check("hedged perception never fails", not result.failures)
    check("hedged perception never head-hop warns",
          not any("head-hop" in w for w in result.warnings))


def _profile_a():
    return {
        "emotional_vocabulary": ["tired"],
        "sensory_priorities": ["sound"],
        "certainty_tolerance": "low",
        "narrative_distance": "close",
        "familiarity_compression": ["market"],
        "social_perception": "wary",
        "characteristic_misinterpretations": ["reads politeness as mockery"],
    }


def _profile_b():
    return {
        "emotional_vocabulary": ["furious"],
        "sensory_priorities": ["smell", "touch"],
        "certainty_tolerance": "high",
        "narrative_distance": "distant",
        "familiarity_compression": [],
        "social_perception": "trusting",
    }


def _state():
    return {
        "attention": {"PRIMARY": ["the knife"], "SECONDARY": ["the window"],
                      "IGNORED": ["the dust"]},
        "emotional_state": "fear",
        "emotional_awareness": "mislabeled",
        "familiarity": ["the market"],
        "interpretations": ["he thinks she is lying"],
        "unknown_facts": ["who paid the bill"],
        "blind_spots": ["his own jealousy"],
        "canon_truth": "the vault code is 7749",
    }


def test_filter_has_16_fields():
    f = POV_FILTER.build_filter(_profile_a(), _state())
    check("filter has 16 contract fields",
          set(f.keys()) == set(POV_FILTER.FILTER_FIELDS),
          f"got {sorted(f.keys())}")


def test_filters_differ_per_profile():
    fa = POV_FILTER.build_filter(_profile_a(), _state())
    fb = POV_FILTER.build_filter(_profile_b(), _state())
    check("filters differ per profile", fa != fb)
    check("sensory priority follows profile",
          fa["SENSORY_PRIORITY"] == ["sound"] and fb["SENSORY_PRIORITY"] == ["smell", "touch"])


def test_mislabeled_emotion_honored():
    f = POV_FILTER.build_filter(_profile_a(), _state())
    framing = f["EMOTIONAL_FRAMING"]
    check("mislabeled emotion presents the mislabel, never the correction",
          "mislabel" in framing and "Never correct it in narration" in framing,
          framing)


def test_familiarity_compression():
    f = POV_FILTER.build_filter(_profile_a(), _state())
    check("familiar elements compress",
          "the market" in f["DESCRIPTION_DENSITY"]["compress"]
          and "the market" in f["FAMILIARITY_COMPRESSION"]["familiar"])


def test_explicit_user_rule_beats_agent_default():
    rules = [
        {"name": "no-colon", "source": "agent_default", "value": "allowed",
         "explicit": False, "by_user": False},
        {"name": "no-colon", "source": "user_explicit", "value": "forbidden",
         "explicit": True, "by_user": True},
    ]
    win = POV_FILTER.resolve_rule(rules, "no-colon")
    check("explicit user rule outranks agent default",
          win is not None and win["value"] == "forbidden")


def test_explicit_narrower_scope_wins():
    rules = [
        {"name": "no-colon", "source": "user_global", "value": "forbidden",
         "explicit": True, "by_user": True},
        {"name": "no-colon", "source": "chapter", "value": "allowed",
         "explicit": True, "by_user": True},
    ]
    win = POV_FILTER.resolve_rule(rules, "no-colon")
    check("explicit narrower-scope override wins",
          win is not None and win["value"] == "allowed")


def test_non_explicit_never_overrides():
    rules = [
        {"name": "no-colon", "source": "user_global", "value": "forbidden",
         "explicit": True, "by_user": True},
        {"name": "no-colon", "source": "chapter", "value": "allowed",
         "explicit": False, "by_user": False},
    ]
    win = POV_FILTER.resolve_rule(rules, "no-colon")
    check("non-explicit entry never overrides",
          win is not None and win["value"] == "forbidden")


def test_canon_belief_separation():
    f = POV_FILTER.build_filter(_profile_a(), _state())
    blob = str(list(f.values()))
    check("canon truth never leaks into the filter", "7749" not in blob)
    check("character belief stays as interpretation",
          "he thinks she is lying" in f["WHAT_THE_CHARACTER_THINKS_IT_MEANS"])


def test_dead_ends_permitted():
    # A wrong belief left uncorrected: human cognition, not a checker offense.
    text = ("He was sure the north road was safe. It was not. "
            "He kept walking north anyway, whistling softly.")
    result = CHECK_EN.check_text(text)
    check("dead-end (uncorrected wrong belief) not punished", not result.failures)


def test_non_closure_permitted():
    text = ("The letter stayed unopened on the table. She never asked about it. "
            "Outside, the rain kept falling on the empty street.")
    result = CHECK_EN.check_text(text)
    check("non-closure (unresolved thread) not punished", not result.failures)


def test_misalignment_permitted():
    text = ("He thought she was angry with him. She was only tired. "
            "He spent the evening avoiding her anyway.")
    result = CHECK_EN.check_text(text)
    check("misalignment (wrong interpretation) not punished", not result.failures)


def test_silent_presence_permitted():
    text = ("Mara sat in the corner and said nothing. The meeting went on "
            "without her. Jin kept glancing at her empty coffee cup.")
    result = CHECK_EN.check_text(text)
    check("silent presence not punished", not result.failures)


TESTS = [v for k, v in sorted(globals().items())
         if k.startswith("test_") and callable(v)]

if __name__ == "__main__":
    print("test_cognition.py")
    for test in TESTS:
        test()
    print(f"\n{summary()}")
    sys.exit(exit_code())
