from __future__ import annotations
import os
import sys
from pathlib import Path

# Make `src/` importable (repo uses src layout)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from unidiff import PatchSet

# Import safety limits (expected public API)
from nova.tools.safety_limits import SafetyLimits

# Try to import the apply step; if absent, we’ll skip that integration test
try:
    from nova.nodes.apply_patch import apply_patch  # type: ignore
except Exception:  # pragma: no cover
    apply_patch = None


def _make_unified_diff(num_files: int, lines_per_file: int) -> str:
    """Create a minimal valid unified diff with only additions."""
    chunks = []
    for i in range(1, num_files + 1):
        name = f"foo{i}.py"
        header = (
            f"diff --git a/{name} b/{name}\n"
            f"index 0000000..1111111 100644\n"
            f"--- a/{name}\n"
            f"+++ b/{name}\n"
            f"@@ -0,0 +1,{lines_per_file} @@\n"
        )
        body = "".join(f"+print('line {j} in {name}')\n" for j in range(1, lines_per_file + 1))
        chunks.append(header + body)
    return "".join(chunks)


def _eval_ok(result) -> bool:
    """
    SafetyLimits.check_limits(...) may return either:
      - an object with `.ok`/`.files_changed`/`.lines_changed`
      - or a tuple `(ok, stats)`  (older versions)
    This makes the test resilient across minor refactors.
    """
    if hasattr(result, "ok"):
        return bool(result.ok)
    if isinstance(result, tuple) and result:
        return bool(result[0])
    raise AssertionError("Unexpected SafetyLimits.check_limits(...) return type")


def _eval_stats(result) -> dict:
    if hasattr(result, "files_changed") and hasattr(result, "lines_changed"):
        return {"files_changed": result.files_changed, "lines_changed": result.lines_changed}
    if isinstance(result, tuple) and len(result) >= 2 and isinstance(result[1], dict):
        return result[1]
    # Best effort: not critical for the assertions, but helpful for debugging
    return {}


def test_rejects_patch_exceeding_line_limit():
    limits = SafetyLimits(max_files_changed=5, max_lines_changed=40)
    # One file, 41 additions -> should violate the line limit
    diff = _make_unified_diff(num_files=1, lines_per_file=41)
    patch = PatchSet(diff)
    res = limits.check_limits(patch)

    assert _eval_ok(res) is False, f"Expected line-limit violation, got: {_eval_stats(res)}"


def test_rejects_patch_exceeding_file_limit():
    limits = SafetyLimits(max_files_changed=5, max_lines_changed=40)
    # Six files, 1 addition each -> should violate the file limit
    diff = _make_unified_diff(num_files=6, lines_per_file=1)
    patch = PatchSet(diff)
    res = limits.check_limits(patch)

    assert _eval_ok(res) is False, f"Expected file-limit violation, got: {_eval_stats(res)}"


def test_allows_patch_within_limits():
    limits = SafetyLimits(max_files_changed=5, max_lines_changed=40)
    # Three files, 10 additions each -> 30 LOC total, within both limits
    diff = _make_unified_diff(num_files=3, lines_per_file=10)
    patch = PatchSet(diff)
    res = limits.check_limits(patch)

    assert _eval_ok(res) is True, f"Expected patch to be allowed, got: {_eval_stats(res)}"


def test_apply_patch_integration_refuses_unsafe_patch(monkeypatch):
    """
    Integration-level guard: apply step must refuse/flag safety violations.
    If the repo hasn’t wired return flags yet, mark this as xfail.
    """
    if apply_patch is None:  # module not available in this build
        import pytest

        pytest.skip("apply_patch module not importable in this environment")

    # Force strict limits and craft an unsafe patch (41 lines in one file)
    limits = SafetyLimits(max_files_changed=5, max_lines_changed=40)
    diff = _make_unified_diff(num_files=1, lines_per_file=41)
    patch = PatchSet(diff)

    # Expect apply_patch(...) to either:
    #  - return a result object with .applied False and .safety_violation True
    #  - or raise a SafetyViolation / ValueError
    try:
        result = apply_patch(patch, safety_limits=limits)  # expected kw-only arg
    except Exception as e:  # raising is also acceptable enforcement
        assert "limit" in str(e).lower() or "safety" in str(e).lower()
        return

    # If it returned a result, validate flags in a tolerant way
    applied = getattr(result, "applied", None)
    violation = getattr(result, "safety_violation", None)

    assert applied is False, "Unsafe patch must not be applied"
    assert violation is True, "Unsafe patch must be flagged as a safety violation"


