"""
Nova Doctor - Comprehensive health checker for AlwaysGreen installation.
"""

from __future__ import annotations

import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class CheckResult:
    name: str
    ok: bool
    status: str
    detail: str = ""
    fix: str = ""


class NovaDoctor:
    """
    Lightweight health checker for Nova (AlwaysGreen) flows.

    What it verifies (non-destructive by default):
      1) Python version is modern enough for Nova usage (>=3.10 recommended).
      2) OPENAI_API_KEY is present.
      3) Nova CLI is available ("nova", with fallback to "alwaysgreen") and reports a version.
      4) Git repo context is valid (inside a work tree).
      5) Nova config exists at .github/nova.yml (path configurable).
      6) (Optional) Parse .github/nova.yml if PyYAML is available to sanity-check keys.
      7) (Optional, opt-in) Very safe smoke run of `nova --help` or a user-supplied `nova fix "<cmd>"`.

    Usage:
        from nova.tools.doctor import NovaDoctor
        doctor = NovaDoctor()
        result = doctor.run()
        
    NOTE: The smoke run is OFF by default to avoid branch mutations. If you enable it,
          prefer a harmless CI command in a scratch repo.
    """

    def __init__(
        self,
        repo_root: Optional[str] = None,
        config_path: str = ".github/nova.yml",
        ci_command: Optional[str] = None,
        enable_smoke_run: bool = False,
        require_python_minor: tuple = (3, 10),
        strict_warnings: bool = False,
    ) -> None:
        self.repo_root = pathlib.Path(repo_root or os.getcwd())
        self.config_path = self.repo_root / config_path
        self.ci_command = ci_command
        self.enable_smoke_run = enable_smoke_run
        self.require_python_minor = require_python_minor
        self.strict_warnings = strict_warnings

    # ---- public API ---------------------------------------------------------

    def run(self) -> Dict:
        checks: List[CheckResult] = []
        checks.append(self._check_python())
        checks.append(self._check_env_key())
        checks.extend(self._check_cli())
        checks.append(self._check_git())
        checks.append(self._check_config_exists())

        yaml_check = self._check_config_yaml()
        if yaml_check:
            checks.append(yaml_check)

        if self.enable_smoke_run:
            checks.append(self._smoke_run())

        checks_dicts = [asdict(c) for c in checks]
        if self.strict_warnings:
            overall_ok = all(c["ok"] for c in checks_dicts)
        else:
            overall_ok = all(c.get("status") != "error" for c in checks_dicts)
        summary = {
            "ok": overall_ok,
            "checks": checks_dicts,
        }
        return summary

    # ---- individual checks --------------------------------------------------

    def _check_python(self) -> CheckResult:
        want = self.require_python_minor
        cur = sys.version_info
        ok = (cur.major, cur.minor) >= want
        return CheckResult(
            name="python.version",
            ok=ok,
            status="ok" if ok else "warn",
            detail=f"Current Python {cur.major}.{cur.minor}.{cur.micro}; recommended ≥ {want[0]}.{want[1]}",
            fix="Use actions/setup-python to pin ≥3.10 for CI; update local interpreter if needed.",
        )

    def _check_env_key(self) -> CheckResult:
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
        has_key = has_openai or has_anthropic
        
        if has_openai and has_anthropic:
            detail = "Both OPENAI_API_KEY and ANTHROPIC_API_KEY are set."
        elif has_openai:
            detail = "OPENAI_API_KEY is set."
        elif has_anthropic:
            detail = "ANTHROPIC_API_KEY is set."
        else:
            detail = "No API keys found."
            
        return CheckResult(
            name="env.api_keys",
            ok=has_key,
            status="ok" if has_key else "error",
            detail=detail,
            fix="Export OPENAI_API_KEY or ANTHROPIC_API_KEY locally or set as CI secrets for runs.",
        )

    def _check_cli(self) -> List[CheckResult]:
        results: List[CheckResult] = []
        candidates = ["nova", "alwaysgreen"]  # prefer 'nova'; fall back to older/alt name if present
        found = None
        for c in candidates:
            if shutil.which(c):
                found = c
                break

        if not found:
            results.append(
                CheckResult(
                    name="cli.nova",
                    ok=False,
                    status="error",
                    detail="Nova CLI not found in PATH.",
                    fix="Install with: pip install nova-ci-rescue (adds the 'nova' command).",
                )
            )
            return results

        # version
        try:
            cp = subprocess.run([found, "version"], capture_output=True, text=True, timeout=15)
            ok = cp.returncode == 0
            ver = (cp.stdout or cp.stderr).strip()
        except Exception as e:
            ok = False
            ver = f"version check failed: {e!r}"

        results.append(
            CheckResult(
                name=f"cli.{found}",
                ok=ok,
                status="ok" if ok else "error",
                detail=f"{found} version → {ver}" if ver else f"{found} present",
                fix="Reinstall: pip install --upgrade nova-ci-rescue",
            )
        )
        return results

    def _check_git(self) -> CheckResult:
        try:
            cp = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True, text=True, timeout=10
            )
            ok = cp.returncode == 0 and cp.stdout.strip() == "true"
            detail = "Inside a Git work tree." if ok else "Not inside a Git repo."
            fix = "Run inside a Git repo (Nova works on branches) or init with `git init`."
        except Exception as e:
            ok = False
            detail = f"git check failed: {e!r}"
            fix = "Ensure git is installed and callable from this environment."

        return CheckResult(name="git.repo", ok=ok, status="ok" if ok else "error", detail=detail, fix=fix)

    def _check_config_exists(self) -> CheckResult:
        exists = self.config_path.exists()
        return CheckResult(
            name="config.path",
            ok=exists,
            status="ok" if exists else "warn",
            detail=f"{self.config_path} {'exists' if exists else 'not found'}",
            fix="Create .github/nova.yml to configure limits/risk/features for Nova.",
        )

    def _check_config_yaml(self) -> Optional[CheckResult]:
        if not self.config_path.exists():
            return None

        try:
            import yaml  # type: ignore
        except Exception:
            return CheckResult(
                name="config.parse",
                ok=False,
                status="warn",
                detail="PyYAML not installed; skipped structure validation.",
                fix="pip install pyyaml to validate nova.yml structure automatically.",
            )

        try:
            data = yaml.safe_load(self.config_path.read_text()) or {}
            problems = []

            # Shallow structure sanity checks based on docs
            if "limits" not in data:
                problems.append("missing: limits")
            else:
                for key in ("max_attempts", "max_files_changed", "max_loc_delta"):
                    if key not in data["limits"]:
                        problems.append(f"limits.{key} missing")

            if "risk" not in data:
                problems.append("missing: risk")
            else:
                for key in ("auto_commit", "suggest_only"):
                    if key not in data["risk"]:
                        problems.append(f"risk.{key} missing")

            # features optional; if present, check known keys
            if "features" in data:
                for key in ("generate_smoke_tests", "test_impact_selection"):
                    if key not in data["features"]:
                        problems.append(f"features.{key} missing")

            ok = not problems
            return CheckResult(
                name="config.structure",
                ok=ok,
                status="ok" if ok else "warn",
                detail="nova.yml structure looks good." if ok else " ; ".join(problems),
                fix="Populate missing keys per docs; start with a minimal nova.yml and iterate.",
            )
        except Exception as e:
            return CheckResult(
                name="config.parse",
                ok=False,
                status="error",
                detail=f"Failed to parse YAML: {e}",
                fix="Check your YAML indentation/format; try validating with yamllint.",
            )

    def _smoke_run(self) -> CheckResult:
        # Very conservative: default to `nova --help`. If ci_command is supplied,
        # we run `nova fix "<cmd>"` (this may modify branches — you opted in).
        cli = shutil.which("nova") or shutil.which("alwaysgreen")
        if not cli:
            return CheckResult(
                name="smoke.cli",
                ok=False,
                status="error",
                detail="Nova CLI not found; cannot smoke run.",
                fix="Install nova-ci-rescue first.",
            )

        if not self.ci_command:
            try:
                cp = subprocess.run([cli, "--help"], capture_output=True, text=True, timeout=20)
                ok = cp.returncode == 0
                return CheckResult(
                    name="smoke.help",
                    ok=ok,
                    status="ok" if ok else "error",
                    detail="`nova --help` executed." if ok else "Help failed.",
                    fix="Reinstall nova-ci-rescue or inspect stderr above.",
                )
            except Exception as e:
                return CheckResult(
                    name="smoke.help",
                    ok=False,
                    status="error",
                    detail=f"`{cli} --help` failed: {e!r}",
                    fix="Reinstall nova-ci-rescue or check Python env.",
                )

        # User explicitly requested a run — warn: may create side branches.
        try:
            cmd = [cli, "fix", ".", "--max-iters", "1", "--timeout", "60", "--verbose"]
            cp = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            ok = cp.returncode == 0
            detail = f"{'Succeeded' if ok else 'Exited with nonzero'}: {' '.join(cmd)}\n\nSTDOUT:\n{cp.stdout[-1000:]}\n\nSTDERR:\n{cp.stderr[-1000:]}"
            return CheckResult(
                name="smoke.run",
                ok=ok,
                status="ok" if ok else "warn",
                detail=detail,
                fix="Inspect output; ensure your repo has tests and API keys are valid.",
            )
        except Exception as e:
            return CheckResult(
                name="smoke.run",
                ok=False,
                status="error",
                detail=f"Smoke run crashed: {e!r}",
                fix="Re-run with --smoke omitted to test CLI only, or check your environment.",
            )
