#!/usr/bin/env python3
"""Seam-integrity regression test (Problem 14).

Guards the production/benchmark seam contract:

1. tools/test_writer_behavioral.py calls the PRODUCTION
   tools/build_writer_prompt.py::build_writer_prompt function object --
   not a local mirror/copy.
2. The behavioral test file contains no local `assemble_writer_prompt`.
3. tools/cognition_test_fixtures.py is the single fixture source (the
   test module's SCENE_CANON / POVS resolve to the fixture module's
   objects).
4. tools/writer_runner.py::resolve_live_runner raises
   LiveModelUnavailable when NOVEL_WRITER_RUNNER is unset (env
   quarantined during the check).
5. skills/prompt-crafting.md Step 1.6 names
   tools/build_writer_prompt.py::build_writer_prompt as the
   authoritative assembly seam (the doc worker owns that string).

Exit code: 0 iff all checks pass.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))
from test_util import check, exit_code, load_module, summary  # noqa: E402

# Plain imports (not load_module): sys.modules dedupes by module name,
# so these resolve to the same module objects the behavioral test file
# imported -- which is exactly what the identity assertions need.
import build_writer_prompt as BWP_PROD  # noqa: E402
import cognition_test_fixtures as FIX  # noqa: E402
import writer_runner as WR  # noqa: E402

WB = load_module("writer_behavioral_seam_mod",
                 TOOLS_DIR / "test_writer_behavioral.py")

# 1. The test calls the production function object, not a copy.
check("behavioral test calls production build_writer_prompt object",
      WB.build_writer_prompt is BWP_PROD.build_writer_prompt,
      "test_writer_behavioral.build_writer_prompt is not "
      "build_writer_prompt.build_writer_prompt")

# 2. No local assembler mirror survives in the test file.
wb_source = (TOOLS_DIR / "test_writer_behavioral.py").read_text(encoding="utf-8")
check("no local assemble_writer_prompt mirror in test file",
      "def assemble_writer_prompt" not in wb_source,
      "found 'def assemble_writer_prompt' in test_writer_behavioral.py")

# 3. cognition_test_fixtures is the single fixture source.
check("test SCENE_CANON is the fixture module's object",
      WB.SCENE_CANON is FIX.SCENE_CANON,
      "SCENE_CANON was copied instead of imported")
check("test POVS is the fixture module's object",
      WB.POVS is FIX.POVS,
      "POVS was copied instead of imported")
check("test MEMORY_VARIANTS is the fixture module's object",
      WB.MEMORY_VARIANTS is FIX.MEMORY_VARIANTS,
      "MEMORY_VARIANTS was copied instead of imported")

# 4. resolve_live_runner raises LiveModelUnavailable when env is unset.
_saved = os.environ.pop("NOVEL_WRITER_RUNNER", None)
try:
    try:
        WR.resolve_live_runner("any-model")
    except WR.LiveModelUnavailable:
        check("resolve_live_runner raises LiveModelUnavailable when "
              "NOVEL_WRITER_RUNNER unset", True)
    except Exception as exc:  # noqa: BLE001 -- wrong exception type is a FAIL
        check("resolve_live_runner raises LiveModelUnavailable when "
              "NOVEL_WRITER_RUNNER unset", False,
              f"raised {type(exc).__name__} instead: {exc}")
    else:
        check("resolve_live_runner raises LiveModelUnavailable when "
              "NOVEL_WRITER_RUNNER unset", False, "no exception raised")
finally:
    if _saved is not None:
        os.environ["NOVEL_WRITER_RUNNER"] = _saved

# 5. The prompt-crafting doc names the production seam as authoritative.
doc = (REPO_ROOT / "skills" / "prompt-crafting.md").read_text(encoding="utf-8")
check("prompt-crafting.md names "
      "tools/build_writer_prompt.py::build_writer_prompt as authoritative",
      "tools/build_writer_prompt.py::build_writer_prompt" in doc,
      "agreed reference string not found in skills/prompt-crafting.md")

print(f"\n{summary()}")
sys.exit(exit_code())
