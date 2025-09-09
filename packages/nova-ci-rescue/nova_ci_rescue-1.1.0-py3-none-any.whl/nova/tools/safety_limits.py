"""
Safety limits for AlwaysGreen operations.
Configures maximum allowed changes to prevent accidental large-scale modifications.
"""

from typing import Optional, List, Union
from pathlib import Path
import re


class SafetyLimits:
    """Safety limits for patch application and PR operations."""

    def __init__(
        self,
        max_files_changed: int = 5,
        max_lines_changed: int = 40,
        restricted_paths: Optional[List[str]] = None,
    ):
        # Maximum allowed changes (conservative defaults)
        self.max_lines_changed = int(max_lines_changed)
        # Internal name kept for backward compatibility with existing code
        self.max_files_modified = int(max_files_changed)

        # Restricted paths that should trigger extra caution
        self.restricted_paths = (
            restricted_paths
            if restricted_paths is not None
            else [
            ".github/workflows/",
            ".github/actions/",
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "Makefile",
            ".env",
            ".env.local",
            ".env.*",
            "secrets/",
            ".secrets/",
            "config/",
            "deploy/",
            "infrastructure/",
            "terraform/",
            "helm/",
            "kubernetes/",
        ]
        )

        # Risk policy defaults (can be overridden)
        self.auto_commit_low_risk = True
        self.suggest_medium_risk = True
        self.block_high_risk = True
        # File pattern buckets
        self.low_risk_globs = [
            "**/*.md",
            "**/*.rst",
            "**/*.txt",
            "**/*.toml",
            "**/*.ini",
            "**/*.cfg",
            "**/*.yaml",
            "**/*.yml",
        ]
        self.medium_risk_globs = [
            "**/*.py",
        ]
        self.high_risk_globs = [
            "requirements*.txt",
            "pyproject.toml",
            "setup.py",
            "Pipfile*",
            "poetry.lock",
            "migrations/**",
            "**/schema/**",
        ]

    def check_limits(
        self,
        changed_files_or_patch: Union[List[str], object],
        lines_changed: Optional[int] = None,
    ) -> tuple[bool, str]:
        """
        Check if the proposed changes violate safety limits.

        Args:
            changed_files_or_patch: Either a list of file paths OR a unified-diff/PatchSet-like object
            lines_changed: Total number of lines changed (required if passing a list of files)

        Returns:
            tuple: (is_safe, message)
        """
        # Normalize inputs to (changed_files, total_lines_changed)
        if lines_changed is None and not isinstance(changed_files_or_patch, list):
            # Attempt to parse a unified diff string representation
            patch_text = str(changed_files_or_patch)
            # Count changed files via diff headers
            file_headers = re.findall(r"^diff --git a/.+ b/.+$", patch_text, flags=re.MULTILINE)
            changed_files = []
            for header in file_headers:
                # Best effort extract file name after b/
                m = re.search(r" b/([^\n\r]+)$", header)
                changed_files.append(m.group(1) if m else header)
            # Count added/removed lines (treat both as change budget)
            total_add = len(
                [
                    1
                    for line in patch_text.splitlines()
                    if line.startswith("+") and not line.startswith("+++")
                ]
            )
            total_del = len(
                [
                    1
                    for line in patch_text.splitlines()
                    if line.startswith("-") and not line.startswith("---")
                ]
            )
            effective_lines_changed = total_add + total_del
        else:
            changed_files = list(changed_files_or_patch)  # type: ignore[arg-type]
            if lines_changed is None:
                # Attempt to infer from list of patch file objects (e.g., unidiff PatchedFile)
                total = 0
                normalized_files = []
                try:
                    for pf in changed_files:
                        name = (
                            getattr(pf, "path", None)
                            or getattr(pf, "target_file", None)
                            or getattr(pf, "source_file", None)
                            or str(pf)
                        )
                        if isinstance(name, str) and name.startswith("b/"):
                            name = name[2:]
                        normalized_files.append(name)

                        added = getattr(pf, "added", None)
                        removed = getattr(pf, "removed", None)
                        if isinstance(added, int) and isinstance(removed, int):
                            total += max(0, added) + max(0, removed)
                        else:
                            hunks = getattr(pf, "hunks", None)
                            if hunks is not None:
                                for h in hunks:
                                    try:
                                        for line in h:
                                            if getattr(line, "is_added", False) or getattr(line, "is_removed", False):
                                                total += 1
                                    except Exception:
                                        pass
                    changed_files = normalized_files
                    effective_lines_changed = total
                except Exception:
                    raise ValueError("lines_changed must be provided when passing a file list")
            else:
                effective_lines_changed = int(lines_changed)

        violations = []

        # Check line limit
        if effective_lines_changed > self.max_lines_changed:
            violations.append(
                f"Maximum lines changed: {self.max_lines_changed} "
                f"(current: {effective_lines_changed})"
            )

        # Check file limit
        if len(changed_files) > self.max_files_modified:
            violations.append(
                f"Maximum files modified: {self.max_files_modified} "
                f"(current: {len(changed_files)})"
            )

        # Check restricted paths
        restricted_modified = []
        for file_path in changed_files:
            for restricted_path in self.restricted_paths:
                if restricted_path in file_path or file_path.startswith(
                    restricted_path
                ):
                    restricted_modified.append(file_path)
                    break

        if restricted_modified:
            violations.append(
                f"Restricted paths modified: {', '.join(restricted_modified[:3])}"
                f"{'...' if len(restricted_modified) > 3 else ''}"
            )

        if violations:
            message = (
                "🛡️ AlwaysGreen Safety Check\n"
                "❌ Safety check failed\n\n"
                "This operation violates safety limits and cannot be automatically applied.\n\n"
                "ℹ️ Safety Limits\n"
                "Current safety limits:\n\n"
                f"Maximum lines changed: {self.max_lines_changed}\n"
                f"Maximum files modified: {self.max_files_modified}\n"
                f"Restricted paths: CI/CD configs, deployment files, secrets, etc.\n\n"
                "Violations:\n" + "\n".join(f"• {v}" for v in violations) + "\n\n"
                "Generated by AlwaysGreen Safety Check"
            )
            return False, message

        return True, "✅ All safety checks passed"

    def assess_patch_risk(self, changed_files: list, lines_changed: int, patch_text: str) -> tuple[str, str]:
        """
        Categorize patch risk as low|medium|high with a brief reason.

        Heuristics:
        - High risk if touching dependency/config/schema/migrations or restricted paths
        - Low risk if only formatting/imports/whitespace or docs
        - Medium otherwise
        """
        # High-risk if any restricted or high-risk globs match
        import fnmatch
        for f in changed_files:
            if any(p in f or f.startswith(p) for p in self.restricted_paths):
                return "high", f"Touches restricted path: {f}"
            if any(fnmatch.fnmatch(f, g) for g in self.high_risk_globs):
                return "high", f"High-risk file: {f}"

        # Low-risk if patch is whitespace/import/order/black-like changes
        lowered = patch_text.lower()
        import_only = ("\n+import " in patch_text or "\n-from " in patch_text) and "def " not in patch_text
        # Improved formatting-only detection: only consider added/removed lines, ignore empty lines and metadata
        formatting_only = True
        for line in patch_text.splitlines():
            if not line or line.startswith("@@"):
                continue
            if line[0] not in "+-":
                continue
            content = line[1:].strip()
            # If the line is not whitespace-only, comment-only, or import/order, it's not formatting-only
            if content and not (
                content == "" or
                content.startswith("#") or
                re.match(r"^(import\s|from\s)", content) or
                re.match(r"^[\s\(\)\[\]\{\},.:;]+$", content)
            ):
                formatting_only = False
                break
        docs_only = all(f.endswith(('.md', '.rst', '.txt')) for f in changed_files)
        if docs_only or (import_only and lines_changed <= 30) or (formatting_only and lines_changed <= 50):
            return "low", "Docs/format/import-only change"

        # Medium for the rest
        return "medium", "Code change outside restricted areas"


class SafetyConfig:
    """Configuration for safety limits."""

    def __init__(self, config_file: Optional[Path] = None):
        self.safety_limits = SafetyLimits()

        # Load from config file if provided
        if config_file and config_file.exists():
            try:
                import yaml
                data = yaml.safe_load(config_file.read_text()) or {}
            except Exception:
                data = {}

            if isinstance(data, dict):
                # Limits
                limits = data.get('limits') or {}
                if isinstance(limits, dict):
                    if 'max_loc_delta' in limits:
                        try:
                            self.safety_limits.max_lines_changed = int(limits['max_loc_delta'])
                        except Exception:
                            pass
                    if 'max_files_changed' in limits:
                        try:
                            self.safety_limits.max_files_modified = int(limits['max_files_changed'])
                        except Exception:
                            pass

                # Restricted paths (blocked_paths)
                blocked = data.get('blocked_paths') or data.get('restricted_paths') or []
                if isinstance(blocked, list):
                    for p in blocked:
                        if isinstance(p, str) and p not in self.safety_limits.restricted_paths:
                            self.safety_limits.restricted_paths.append(p)

                # Optional risk policy tuning
                policy = (data.get('risk_policy') or {}) if isinstance(data, dict) else {}
                self.safety_limits.auto_commit_low_risk = bool(policy.get('auto_commit_low_risk', True))
                self.safety_limits.suggest_medium_risk = bool(policy.get('suggest_medium_risk', True))
                self.safety_limits.block_high_risk = bool(policy.get('block_high_risk', True))
