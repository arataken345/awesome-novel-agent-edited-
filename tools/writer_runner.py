#!/usr/bin/env python3
"""Production Writer seam: protocol + live-model resolution.

The production Writer is a markdown agent role executed by an external
harness (agents/writer.md); the repository defines no model interface
of its own. This module is the honest seam between the deterministic
prompt assembly (tools/build_writer_prompt.py) and whatever backend the
USER supplies to actually generate prose:

    prompt document -> WriterRunner.generate() -> prose

Any backend is user-supplied via the NOVEL_WRITER_RUNNER environment
variable. No provider is hard-coded, no new dependency is introduced,
and no API-key handling exists in this repository (by design).

Usage (Level B of tools/test_writer_behavioral.py):
    NOVEL_WRITER_RUNNER="my_runners:openai_runner" \
        python3 tools/test_writer_behavioral.py --model gpt-x

where my_runners.openai_runner is a callable
``create(model: str) -> WriterRunner``.

STDLIB ONLY.
"""

from __future__ import annotations

import importlib
import os
from typing import Protocol


class WriterRunner(Protocol):
    """The production Writer seam.

    Given a Writer prompt document (the markdown produced by
    tools/build_writer_prompt.py::build_writer_prompt), produce prose.
    The protocol is the whole contract: how the backend generates is
    the user's business, not the framework's.
    """

    def generate(self, prompt_document: str) -> str:
        """Generate prose from the prompt document. Must return a string."""
        ...


class LiveModelUnavailable(Exception):
    """Raised when no live Writer backend can be resolved.

    Never a test failure: callers report an honest SKIP, never a pass.
    """


def resolve_live_runner(model: str | None) -> WriterRunner:
    """Resolve a user-supplied live Writer backend.

    Reads ``NOVEL_WRITER_RUNNER="module:factory_path"`` (e.g.
    ``"my_runners:openai_runner"``). The factory must be a callable
    with signature ``create(model: str) -> WriterRunner``; ``model`` is
    passed through verbatim (may be None when ``--model`` had no name).

    Raises LiveModelUnavailable when the env var is missing or
    malformed, the module cannot be imported, the factory is missing /
    not callable, the factory raises, or the returned object has no
    callable ``generate``.
    """
    spec = os.environ.get("NOVEL_WRITER_RUNNER", "").strip()
    if not spec:
        raise LiveModelUnavailable(
            "NOVEL_WRITER_RUNNER is not set "
            "(expected 'module:factory_path', e.g. 'my_runners:openai_runner')")
    if ":" not in spec:
        raise LiveModelUnavailable(
            f"NOVEL_WRITER_RUNNER={spec!r} is not 'module:factory_path'")
    module_name, _, factory_path = spec.partition(":")
    module_name = module_name.strip()
    factory_path = factory_path.strip()
    if not module_name or not factory_path:
        raise LiveModelUnavailable(
            f"NOVEL_WRITER_RUNNER={spec!r} is not 'module:factory_path'")
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 -- any import failure is "unavailable"
        raise LiveModelUnavailable(
            f"cannot import runner module {module_name!r}: {exc}") from exc
    factory = module
    for part in factory_path.split("."):
        factory = getattr(factory, part, None)
        if factory is None:
            raise LiveModelUnavailable(
                f"factory {factory_path!r} not found in module "
                f"{module_name!r}") from None
    if not callable(factory):
        raise LiveModelUnavailable(
            f"factory {factory_path!r} in module {module_name!r} "
            "is not callable")
    try:
        runner = factory(model)
    except Exception as exc:  # noqa: BLE001 -- factory failure is "unavailable"
        raise LiveModelUnavailable(
            f"factory {factory_path!r} failed for model {model!r}: "
            f"{exc}") from exc
    generate = getattr(runner, "generate", None)
    if not callable(generate):
        raise LiveModelUnavailable(
            f"runner returned by {factory_path!r} has no callable "
            "generate(prompt_document) method")
    return runner
