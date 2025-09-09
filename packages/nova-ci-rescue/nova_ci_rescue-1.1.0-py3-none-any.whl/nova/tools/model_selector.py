from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ModelSelection:
    chosen: str
    tried: List[Tuple[str, str]]  # (model, reason)


def _has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _is_model_available(model: str) -> Tuple[bool, str]:
    """
    Best-effort capability check without calling vendor APIs.

    - If OPENAI_API_KEY is present, assume GPT/o3 models are usable.
    - Otherwise, not available.
    """
    if model in {"gpt-5-fast", "gpt-4o", "o3-mini"}:
        if _has_openai_key():
            return True, "api_key_present"
        return False, "missing_openai_api_key"
    if model == "enhanced":
        return True, "local_enhanced_available"
    if model == "mock":
        return True, "mock_fallback"
    return False, "unknown_model"


def build_fallback_chain(primary: str) -> List[str]:
    secondary = os.getenv("NOVA_SECONDARY_MODEL") or os.getenv("ALWAYSGREEN_SECONDARY_MODEL")
    chain: List[str] = [primary]
    if secondary:
        chain.append(secondary)
    else:
        chain.append("gpt-4o")
    # Always include enhanced and mock as final fallbacks
    chain.extend(["enhanced", "mock"])
    # Deduplicate while preserving order
    out: List[str] = []
    for m in chain:
        if m not in out:
            out.append(m)
    return out


def select_model(default_model: str) -> ModelSelection:
    """
    Select an LLM model with fallbacks.

    Order: configured/default → (secondary or gpt-4o) → enhanced → mock.
    Returns the chosen model and the tried list with reasons.
    """
    tried: List[Tuple[str, str]] = []
    for candidate in build_fallback_chain(default_model):
        ok, reason = _is_model_available(candidate)
        tried.append((candidate, reason))
        if ok:
            return ModelSelection(chosen=candidate, tried=tried)
    # Should never happen because mock is always available
    return ModelSelection(chosen="mock", tried=tried)


__all__ = ["ModelSelection", "select_model", "build_fallback_chain"]


