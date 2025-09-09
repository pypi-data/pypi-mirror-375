from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, ConfigDict


# ------- Models -------


class Limits(BaseModel):
    max_attempts: int = Field(3, ge=1)
    max_files_changed: int = Field(5, ge=1)
    max_loc_delta: int = Field(40, ge=1)


class Risk(BaseModel):
    auto_commit: List[str] = Field(default_factory=lambda: ["lint", "format", "import", "type"])
    suggest_only: List[str] = Field(default_factory=lambda: ["dependency", "schema"])


class Features(BaseModel):
    generate_smoke_tests: bool = False
    test_impact_selection: bool = True


class AlwaysGreenSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limits: Limits = Field(default_factory=Limits)
    risk: Risk = Field(default_factory=Risk)
    features: Features = Field(default_factory=Features)
    model: Optional[str] = None
    ci_cmd: Optional[str] = None
    blocked_paths: List[str] = Field(default_factory=list)

    # Compatibility properties (for legacy callers in CLI)
    @property
    def max_changed_lines(self) -> int:
        return self.limits.max_loc_delta

    @property
    def max_changed_files(self) -> int:
        return self.limits.max_files_changed


# ------- Loader -------


DEFAULT_CONFIG_NAMES = (
    ".github/nova.yml",
    ".github/alwaysgreen.yml",
    "nova.yml",
    "alwaysgreen.yml",
)


class ConfigError(Exception):
    pass


def _find_config_file(repo_path: Path, explicit: Optional[Path]) -> Optional[Path]:
    if explicit:
        return explicit if explicit.exists() else None
    for name in DEFAULT_CONFIG_NAMES:
        candidate = repo_path / name
        if candidate.exists():
            return candidate
    return None


def _load_yaml(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ConfigError(f"Config at {path} must be a YAML mapping (got {type(data).__name__}).")
        return data
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}") from e
    except OSError as e:
        raise ConfigError(f"Failed to read {path}: {e}") from e


def _coerce_legacy_keys(raw: Dict[str, Any]) -> Dict[str, Any]:
    raw = dict(raw or {})
    limits = dict(raw.get("limits") or {})

    # Legacy top-level keys
    if "max_attempts" in raw:
        limits.setdefault("max_attempts", raw.pop("max_attempts"))
    if "max_iters" in raw:
        limits.setdefault("max_attempts", raw.pop("max_iters"))
    if "max_files_changed" in raw:
        limits.setdefault("max_files_changed", raw.pop("max_files_changed"))
    if "max_loc_delta" in raw:
        limits.setdefault("max_loc_delta", raw.pop("max_loc_delta"))

    if limits:
        raw["limits"] = limits

    return raw


def _env_overrides() -> Dict[str, Any]:
    env: Dict[str, Any] = {}
    getb = lambda v: str(v).lower() in {"1", "true", "yes", "on"}
    if v := os.getenv("ALWAYSGREEN_MAX_ATTEMPTS"):
        env.setdefault("limits", {})["max_attempts"] = int(v)
    if v := os.getenv("ALWAYSGREEN_MAX_FILES_CHANGED"):
        env.setdefault("limits", {})["max_files_changed"] = int(v)
    if v := os.getenv("ALWAYSGREEN_MAX_LOC_DELTA"):
        env.setdefault("limits", {})["max_loc_delta"] = int(v)
    if v := os.getenv("ALWAYSGREEN_GENERATE_SMOKE_TESTS"):
        env.setdefault("features", {})["generate_smoke_tests"] = getb(v)
    if v := os.getenv("ALWAYSGREEN_TEST_IMPACT_SELECTION"):
        env.setdefault("features", {})["test_impact_selection"] = getb(v)
    if v := os.getenv("ALWAYSGREEN_MODEL"):
        env["model"] = v
    if v := os.getenv("ALWAYSGREEN_CI_CMD"):
        env["ci_cmd"] = v
    return env


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _suggest_key(key: str) -> str:
    valid = {
        "limits",
        "risk",
        "features",
        "max_attempts",
        "max_iters",
        "max_files_changed",
        "max_loc_delta",
        "auto_commit",
        "suggest_only",
        "generate_smoke_tests",
        "test_impact_selection",
        "model",
        "ci_cmd",
        "blocked_paths",
    }
    match = get_close_matches(key, list(valid), n=1)
    return f" Did you mean '{match[0]}'?" if match else ""


def load_alwaysgreen_settings(
    repo_path: Path,
    *,
    config_path: Optional[Path] = None,
    cli_overrides: Optional[Dict[str, Any]] = None,
) -> AlwaysGreenSettings:
    repo_path = Path(repo_path).resolve()
    yaml_path = _find_config_file(repo_path, config_path)

    yaml_data: Dict[str, Any] = {}
    if yaml_path:
        yaml_data = _load_yaml(yaml_path)
        yaml_data = _coerce_legacy_keys(yaml_data)
        for key in list(yaml_data.keys()):
            if key not in {"limits", "risk", "features", "model", "ci_cmd", "blocked_paths",
                           "max_attempts", "max_iters", "max_files_changed", "max_loc_delta"}:
                warnings.warn(f"Unknown config key: '{key}'.{_suggest_key(key)}", stacklevel=1)

    merged = _deep_merge(yaml_data, _env_overrides())
    merged = _deep_merge(merged, cli_overrides or {})

    try:
        return AlwaysGreenSettings(**merged)
    except ValidationError as e:
        raise ConfigError(f"Config validation failed for {yaml_path or '<defaults>'}: {e}") from e


__all__ = [
    "AlwaysGreenSettings",
    "Limits",
    "Risk",
    "Features",
    "load_alwaysgreen_settings",
    "ConfigError",
]


