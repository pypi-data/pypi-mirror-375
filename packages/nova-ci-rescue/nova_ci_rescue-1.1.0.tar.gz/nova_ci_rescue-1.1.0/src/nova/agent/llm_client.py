"""
Unified LLM client for AlwaysGreen supporting OpenAI, Grok, and Anthropic.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timezone
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

# Grok uses OpenAI compatible API, so we'll use OpenAI client for Grok models

from nova.config import get_settings
from nova.telemetry.logger import get_logger


class LLMClient:
    """Unified LLM client that supports OpenAI, Grok, and Anthropic models."""

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.provider = None
        # Verbose controlled via env NOVA_VERBOSE=true set by CLI --verbose
        self._verbose = os.environ.get("NOVA_VERBOSE", "").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        # Token usage tracking
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "calls": [],  # List of individual call details
        }

        # Determine which provider to use based on model name and available API keys
        model_name = self.settings.default_llm_model.lower()

        if "claude" in model_name and self.settings.anthropic_api_key:
            # Use Anthropic
            if anthropic is None:
                raise ImportError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
            self.client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
            self.provider = "anthropic"
            self.model = self._get_anthropic_model_name()
        elif "grok" in model_name and self.settings.openai_api_key:
            # Use Grok (via OpenAI compatible API)
            if OpenAI is None:
                raise ImportError(
                    "openai package not installed. Run: pip install openai"
                )
            # For Grok, we'll use a different base URL or API key
            grok_api_key = (
                os.environ.get("GROK_API_KEY") or self.settings.openai_api_key
            )
            grok_base_url = os.environ.get("GROK_BASE_URL", "https://api.x.ai/v1")
            self.client = OpenAI(api_key=grok_api_key, base_url=grok_base_url)
            self.provider = "grok"
            self.model = self._get_grok_model_name()
        elif self.settings.openai_api_key:
            # Use OpenAI
            if OpenAI is None:
                raise ImportError(
                    "openai package not installed. Run: pip install openai"
                )
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self.provider = "openai"
            self.model = self._get_openai_model_name()
        else:
            raise ValueError(
                "No valid API key found. Please set OPENAI_API_KEY (for OpenAI/Grok) or ANTHROPIC_API_KEY (for Claude)."
            )

    def _get_openai_model_name(self) -> str:
        """Get the OpenAI model name to use."""
        model = self.settings.default_llm_model

        # Map special names to actual API model names and handle fallback preference
        if model in {"gpt-5-fast", "gpt-5-chat-latest", "gpt-5"}:
            # Prefer fast GPT-5; if unavailable at runtime, caller should catch and fallback
            return "gpt-5"
        elif model in [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ]:
            return model
        else:
            # Default to GPT-4o
            return "gpt-4o"

    def _get_anthropic_model_name(self) -> str:
        """Get the Anthropic model name to use."""
        model = self.settings.default_llm_model.lower()

        # Map to actual Anthropic models
        if "claude-3-opus" in model:
            return "claude-3-opus-20240229"
        elif "claude-3-sonnet" in model:
            return "claude-3-sonnet-20240229"
        elif "claude-3-haiku" in model:
            return "claude-3-haiku-20240307"
        elif "claude-3.5-sonnet" in model or "claude-3-5-sonnet" in model:
            return "claude-3-5-sonnet-20241022"
        else:
            # Default to Claude 3.5 Sonnet
            return "claude-3-5-sonnet-20241022"

    def _get_grok_model_name(self) -> str:
        """Get the Grok model name to use."""
        model = self.settings.default_llm_model.lower()

        # Map to actual Grok models
        if "grok-code-fast-1" in model:
            return "grok-code-fast-1"
        elif "grok-2" in model:
            return "grok-2-1212"
        elif "grok-1" in model:
            return "grok-1"
        else:
            # Default to Grok Code Fast 1
            return "grok-code-fast-1"

    def complete(
        self, system: str, user: str, temperature: float = 1.0, max_tokens: int = 40000
    ) -> str:
        """
        Get a completion from the LLM.

        Args:
            system: System prompt
            user: User prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            The LLM's response text
        """
        # Get logger
        logger = get_logger()

        # Log the request details
        logger.debug(
            "LLM Request Configuration",
            {
                "provider": self.provider,
                "model": self.model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            component="LLM",
        )

        logger.debug(
            "Prompt Statistics",
            {
                "system_length": f"{len(system)} chars",
                "user_length": f"{len(user)} chars",
                "total_length": f"{len(system) + len(user)} chars",
            },
            component="LLM",
        )

        logger.trace(
            "System Prompt",
            system[:200] + "..." if len(system) > 200 else system,
            component="LLM",
        )
        logger.trace(
            "User Prompt",
            user[:200] + "..." if len(user) > 200 else user,
            component="LLM",
        )

        # Daily usage tracking and alerts
        self._increment_daily_usage()
        try:
            if self.provider == "openai":
                # Force OpenAI params, respecting env MAX_TOKENS
                try:
                    max_tok = int(os.environ.get("MAX_TOKENS", "40000"))
                except Exception:
                    max_tok = 40000
                return self._complete_openai(
                    system, user, temperature=1.0, max_tokens=max_tok
                )
            elif self.provider == "grok":
                # Grok uses OpenAI compatible API
                try:
                    max_tok = int(os.environ.get("MAX_TOKENS", "40000"))
                except Exception:
                    max_tok = 40000
                return self._complete_openai(
                    system, user, temperature=1.0, max_tokens=max_tok
                )
            elif self.provider == "anthropic":
                return self._complete_anthropic(
                    system, user, temperature=1.0, max_tokens=max_tokens
                )
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
        finally:
            logger = get_logger()
            # if elapsed > self.settings.llm_call_timeout_sec:
            #     # logger.warning(f"LLM call exceeded {self.settings.llm_call_timeout_sec}s (took {int(elapsed)}s)")
            #     pass

    def _usage_path(self) -> Path:
        root = Path(os.path.expanduser("~")) / ".nova"
        try:
            root.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        return root / "usage.json"

    def _increment_daily_usage(self) -> None:
        try:
            path = self._usage_path()
            data: Dict[str, Any] = {}
            if path.exists():
                try:
                    data = json.loads(path.read_text() or "{}")
                except Exception:
                    data = {}
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            counts = data.get(today, {"calls": 0})
            counts["calls"] = int(counts.get("calls", 0)) + 1
            data[today] = counts
            try:
                path.write_text(json.dumps(data))
            except Exception:
                pass
            # Alerts
            max_calls = int(getattr(self.settings, "max_daily_llm_calls", 0) or 0)
            warn_pct = float(
                getattr(self.settings, "warn_daily_llm_calls_pct", 0.8) or 0.8
            )
            if max_calls > 0:
                warn_threshold = int(max_calls * warn_pct)
                logger = get_logger()
                if counts["calls"] == warn_threshold:
                    logger.warning(
                        f"Daily LLM calls reached {counts['calls']}/{max_calls} ({int(warn_pct*100)}%)."
                    )
                if counts["calls"] > max_calls:
                    logger.warning(
                        f"Daily LLM calls exceeded limit: {counts['calls']}/{max_calls}. Consider pausing or lowering usage."
                    )
        except Exception:
            # Never block on usage tracking
            pass

    def _complete_openai(
        self, system: str, user: str, temperature: float, max_tokens: int
    ) -> str:
        """Complete using OpenAI API."""
        try:
            # Use Chat Completions API for all models
            # Build kwargs
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }

            # Handle model-specific parameters
            if "gpt-5" in self.model.lower():
                kwargs["max_completion_tokens"] = max_tokens
                kwargs["temperature"] = temperature
                kwargs["reasoning_effort"] = self.settings.reasoning_effort
            else:
                # Limit max_tokens for GPT-4o and other models
                if "gpt-4o" in self.model.lower():
                    kwargs["max_tokens"] = min(max_tokens, 16384)  # GPT-4o limit
                elif self.model.lower() == "gpt-4" or (
                    self.model.lower().startswith("gpt-4-")
                    and not self.model.lower().startswith("gpt-4o")
                ):
                    kwargs["max_tokens"] = min(max_tokens, 8192)  # GPT-4 limit
                else:
                    kwargs["max_tokens"] = max_tokens
                kwargs["temperature"] = temperature

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            # Track token usage
            if hasattr(response, "usage"):
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
                completion_tokens = getattr(response.usage, "completion_tokens", 0)
                total_tokens = getattr(response.usage, "total_tokens", 0)

                self.token_usage["prompt_tokens"] += prompt_tokens
                self.token_usage["completion_tokens"] += completion_tokens
                self.token_usage["total_tokens"] += total_tokens
                self.token_usage["calls"].append(
                    {
                        "model": self.model,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

            logger = get_logger()
            if content:
                content = content.strip()
                logger.verbose(
                    f"Response length: {len(content)} chars", component="LLM"
                )
                if hasattr(response, "usage"):
                    logger.verbose(
                        f"Tokens used: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total",
                        component="LLM",
                    )
                logger.debug(
                    "Response preview",
                    {"first_100_chars": content[:100] + "..."},
                    component="LLM",
                )
                logger.trace("Full Response", content, component="LLM")
            else:
                logger.warning("OpenAI returned None/empty content!")
                content = ""
            return content

        except Exception as e:
            logger = get_logger()
            logger.error(f"OpenAI API error: {type(e).__name__}: {e}")
            raise

    def _complete_anthropic(
        self, system: str, user: str, temperature: float = 1.0, max_tokens: int = 40000
    ) -> str:
        """Complete using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system,
                messages=[{"role": "user", "content": user}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Track token usage (Anthropic provides usage info)
            if hasattr(response, "usage"):
                prompt_tokens = getattr(response.usage, "input_tokens", 0)
                completion_tokens = getattr(response.usage, "output_tokens", 0)
                total_tokens = prompt_tokens + completion_tokens

                self.token_usage["prompt_tokens"] += prompt_tokens
                self.token_usage["completion_tokens"] += completion_tokens
                self.token_usage["total_tokens"] += total_tokens
                self.token_usage["calls"].append(
                    {
                        "model": self.model,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

            if response.content and len(response.content) > 0:
                content = response.content[0].text
                logger = get_logger()
                if content:
                    content = content.strip()
                    logger.verbose(
                        f"Response length: {len(content)} chars", component="LLM"
                    )
                    if hasattr(response, "usage"):
                        logger.verbose(
                            f"Tokens used: {prompt_tokens} prompt + {completion_tokens} completion = {total_tokens} total",
                            component="LLM",
                        )
                    logger.debug(
                        "Response preview",
                        {"first_100_chars": content[:100] + "..."},
                        component="LLM",
                    )
                    logger.trace("Full Response", content, component="LLM")
                else:
                    logger.warning("Anthropic returned None/empty text!")
                    content = ""
            else:
                logger = get_logger()
                logger.warning("Anthropic returned empty content array!")
                content = ""
            return content
        except Exception as e:
            logger = get_logger()
            logger.error(f"Anthropic API error: {type(e).__name__}: {e}")
            raise


def parse_plan(response: str) -> Dict[str, Any]:
    """
    Parse the LLM's planning response into a structured plan.

    Args:
        response: The LLM's response text

    Returns:
        Structured plan dictionary
    """
    # Try to extract JSON if present
    if "{" in response and "}" in response:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            plan_json = json.loads(response[start:end])
            return plan_json
        except json.JSONDecodeError:
            # JSON parsing failed, fall back to bullet parsing
            pass
        except Exception:
            # Other unexpected error, fall back to bullet parsing
            pass

    # Parse numbered list or bullets
    lines = response.strip().split("\n")
    steps = []

    for line in lines:
        line = line.strip()
        # Remove numbering or bullets
        if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
            # Remove leading numbers, dots, dashes, etc.
            import re

            cleaned = re.sub(r"^[\d\.\-\*\s]+", "", line).strip()
            if cleaned:
                steps.append(cleaned)

    if steps:
        return {"approach": "Fix failing tests systematically", "steps": steps}
    else:
        # Return the whole response as the approach
        return {"approach": response.strip(), "steps": []}


def build_planner_prompt(
    failing_tests: List[Dict[str, Any]], critic_feedback: Optional[str] = None
) -> str:
    """
    Build a prompt for the planner to analyze failures and create a fix strategy.

    Args:
        failing_tests: List of failing test details
        critic_feedback: Optional feedback from previous critic rejection

    Returns:
        Formatted prompt string
    """
    prompt = ""

    # Include critic feedback if available
    if critic_feedback:
        prompt += "⚠️ PREVIOUS ATTEMPT REJECTED:\n"
        prompt += "The critic rejected the last patch with this feedback:\n"
        prompt += f'"{critic_feedback}"\n\n'
        prompt += "Please create a NEW plan that addresses this feedback and avoids the same mistakes.\n\n"

    prompt += "Analyze these failing tests and create a plan to fix them:\n\n"
    prompt += "FAILING TESTS:\n"
    prompt += "| Test Name | File | Line | Error |\n"
    prompt += "|-----------|------|------|-------|\n"

    for test in failing_tests[:10]:  # Limit to first 10 tests
        name = test.get("name", "unknown")[:40]
        file = test.get("file", "unknown")[:30]
        line = test.get("line", 0)
        error = test.get("short_traceback", "")
        if error:
            # Get first line of error
            error = error.split("\n")[0]
        else:
            error = "No error details"

        prompt += f"| {name} | {file} | {line} | {error} |\n"

    if len(failing_tests) > 10:
        prompt += f"\n... and {len(failing_tests) - 10} more failing tests\n"

    prompt += "\n"
    prompt += "Provide a structured plan to fix these failures. Include:\n"
    prompt += "1. A general approach/strategy\n"
    prompt += "2. Specific steps to take\n"
    prompt += "3. Which tests to prioritize\n"
    prompt += "\n"
    prompt += "Format your response as a numbered list of actionable steps."

    return prompt


def build_patch_prompt(
    plan: Dict[str, Any],
    failing_tests: List[Dict[str, Any]],
    test_contents: Dict[str, str] = None,
    source_contents: Dict[str, str] = None,
    critic_feedback: Optional[str] = None,
) -> str:
    """
    Build a prompt for the actor to generate a patch based on the plan.

    Args:
        plan: The plan created by the planner
        failing_tests: List of failing test details
        test_contents: Optional dict of test file contents
        source_contents: Optional dict of source file contents
        critic_feedback: Optional feedback from previous critic rejection

    Returns:
        Formatted prompt string
    """
    prompt = ""

    # Include critic feedback if available
    if critic_feedback:
        prompt += "⚠️ PREVIOUS PATCH REJECTED:\n"
        prompt += f'"{critic_feedback}"\n\n'
        prompt += "Generate a DIFFERENT patch that avoids these issues.\n\n"

    prompt += "Generate a unified diff patch to fix the failing tests.\n\n"

    # Include the plan
    if plan:
        prompt += "PLAN:\n"
        if isinstance(plan.get("approach"), str):
            prompt += f"Approach: {plan['approach']}\n"
        if plan.get("steps"):
            prompt += "Steps:\n"
            for i, step in enumerate(plan["steps"][:5], 1):
                prompt += f"  {i}. {step}\n"
        prompt += "\n"

    # Include failing test details with clear actual vs expected
    prompt += "FAILING TESTS TO FIX:\n"
    for i, test in enumerate(failing_tests[:3], 1):
        prompt += f"\n{i}. Test: {test.get('name', 'unknown')}\n"
        prompt += f"   File: {test.get('file', 'unknown')}\n"
        prompt += f"   Line: {test.get('line', 0)}\n"

        # Extract actual vs expected from error message if present
        error_msg = test.get("short_traceback", "No traceback")
        prompt += f"   Error:\n{error_msg}\n"

        # Highlight the mismatch if we can identify it
        if "Expected" in error_msg and "but got" in error_msg:
            prompt += (
                "   ⚠️ Pay attention to the EXACT expected vs actual values above!\n"
            )
            prompt += "   If the expected value is logically wrong, fix the test, not the code.\n"

    # Include test file contents if provided
    if test_contents:
        prompt += (
            "\n\nTEST FILE CONTENTS (modify ONLY if tests have wrong expectations):\n"
        )
        for file_path, content in test_contents.items():
            prompt += f"\n=== {file_path} ===\n"
            prompt += content

    # Include source file contents if provided
    if source_contents:
        prompt += "\n\nSOURCE CODE (FIX THESE FILES):\n"
        for file_path, content in source_contents.items():
            prompt += f"\n=== {file_path} ===\n"
            prompt += content

    prompt += "\n\n"
    prompt += "Generate a unified diff patch that fixes these test failures.\n"
    prompt += "The patch should:\n"
    prompt += "1. Be in standard unified diff format (like 'git diff' output)\n"
    prompt += "2. Include proper file paths (--- a/file and +++ b/file)\n"
    prompt += "3. Include proper @@ hunk headers with line numbers\n"
    prompt += "4. Fix the actual issues causing test failures\n"
    prompt += "5. IMPORTANT: If a test expects an obviously wrong value (e.g., 2+2=5, sum([1,2,3,4,5])=20), \n"
    prompt += "   fix the TEST's expectation, not the implementation\n"
    prompt += "6. Be minimal and focused\n"
    prompt += "7. DO NOT introduce arbitrary constants or magic numbers just to make tests pass\n"
    prompt += (
        "8. DO NOT add/remove spaces or characters unless they logically belong there\n"
    )
    prompt += "9. REMOVE any existing BUG comments (e.g., '# BUG:', '# BUG: ...', etc.) from the code\n"
    prompt += "10. DO NOT add any new comments about bugs or fixes (no '# BUG:', '# FIX:', etc.)\n"
    prompt += "\n"
    prompt += (
        "WARNING: Avoid quick hacks like hardcoding values. Focus on the root cause.\n"
    )
    prompt += "If the test's expected value is mathematically or logically wrong, fix the test.\n"
    prompt += "\n"
    prompt += "Return ONLY the unified diff, starting with --- and no other text."

    return prompt

    # Include source file contents if provided
    if source_contents:
        prompt += "\n\nSOURCE CODE (FIX THESE FILES):\n"
        for file_path, content in source_contents.items():
            prompt += f"\n=== {file_path} ===\n"
            prompt += content

    prompt += "\n\n"
    prompt += "Generate a unified diff patch that fixes these test failures.\n"
    prompt += "The patch should:\n"
    prompt += "1. Be in standard unified diff format (like 'git diff' output)\n"
    prompt += "2. Include proper file paths (--- a/file and +++ b/file)\n"
    prompt += "3. Include proper @@ hunk headers with line numbers\n"
    prompt += "4. Fix the actual issues causing test failures\n"
    prompt += "5. IMPORTANT: If a test expects an obviously wrong value (e.g., 2+2=5, sum([1,2,3,4,5])=20), \n"
    prompt += "   fix the TEST's expectation, not the implementation\n"
    prompt += "6. Be minimal and focused\n"
    prompt += "7. DO NOT introduce arbitrary constants or magic numbers just to make tests pass\n"
    prompt += (
        "8. DO NOT add/remove spaces or characters unless they logically belong there\n"
    )
    prompt += "9. REMOVE any existing BUG comments (e.g., '# BUG:', '# BUG: ...', etc.) from the code\n"
    prompt += "10. DO NOT add any new comments about bugs or fixes (no '# BUG:', '# FIX:', etc.)\n"
    prompt += "\n"
    prompt += (
        "WARNING: Avoid quick hacks like hardcoding values. Focus on the root cause.\n"
    )
    prompt += "If the test's expected value is mathematically or logically wrong, fix the test.\n"
    prompt += "\n"
    prompt += "Return ONLY the unified diff, starting with --- and no other text."

    return prompt

    # Include source file contents if provided
    if source_contents:
        prompt += "\n\nSOURCE CODE (FIX THESE FILES):\n"
        for file_path, content in source_contents.items():
            prompt += f"\n=== {file_path} ===\n"
            prompt += content

    prompt += "\n\n"
    prompt += "Generate a unified diff patch that fixes these test failures.\n"
    prompt += "The patch should:\n"
    prompt += "1. Be in standard unified diff format (like 'git diff' output)\n"
    prompt += "2. Include proper file paths (--- a/file and +++ b/file)\n"
    prompt += "3. Include proper @@ hunk headers with line numbers\n"
    prompt += "4. Fix the actual issues causing test failures\n"
    prompt += "5. IMPORTANT: If a test expects an obviously wrong value (e.g., 2+2=5, sum([1,2,3,4,5])=20), \n"
    prompt += "   fix the TEST's expectation, not the implementation\n"
    prompt += "6. Be minimal and focused\n"
    prompt += "7. DO NOT introduce arbitrary constants or magic numbers just to make tests pass\n"
    prompt += (
        "8. DO NOT add/remove spaces or characters unless they logically belong there\n"
    )
    prompt += "9. REMOVE any existing BUG comments (e.g., '# BUG:', '# BUG: ...', etc.) from the code\n"
    prompt += "10. DO NOT add any new comments about bugs or fixes (no '# BUG:', '# FIX:', etc.)\n"
    prompt += "\n"
    prompt += (
        "WARNING: Avoid quick hacks like hardcoding values. Focus on the root cause.\n"
    )
    prompt += "If the test's expected value is mathematically or logically wrong, fix the test.\n"
    prompt += "\n"
    prompt += "Return ONLY the unified diff, starting with --- and no other text."

    return prompt

    # Include source file contents if provided
    if source_contents:
        prompt += "\n\nSOURCE CODE (FIX THESE FILES):\n"
        for file_path, content in source_contents.items():
            prompt += f"\n=== {file_path} ===\n"
            prompt += content

    prompt += "\n\n"
    prompt += "Generate a unified diff patch that fixes these test failures.\n"
    prompt += "The patch should:\n"
    prompt += "1. Be in standard unified diff format (like 'git diff' output)\n"
    prompt += "2. Include proper file paths (--- a/file and +++ b/file)\n"
    prompt += "3. Include proper @@ hunk headers with line numbers\n"
    prompt += "4. Fix the actual issues causing test failures\n"
    prompt += "5. IMPORTANT: If a test expects an obviously wrong value (e.g., 2+2=5, sum([1,2,3,4,5])=20), \n"
    prompt += "   fix the TEST's expectation, not the implementation\n"
    prompt += "6. Be minimal and focused\n"
    prompt += "7. DO NOT introduce arbitrary constants or magic numbers just to make tests pass\n"
    prompt += (
        "8. DO NOT add/remove spaces or characters unless they logically belong there\n"
    )
    prompt += "9. REMOVE any existing BUG comments (e.g., '# BUG:', '# BUG: ...', etc.) from the code\n"
    prompt += "10. DO NOT add any new comments about bugs or fixes (no '# BUG:', '# FIX:', etc.)\n"
    prompt += "\n"
    prompt += (
        "WARNING: Avoid quick hacks like hardcoding values. Focus on the root cause.\n"
    )
    prompt += "If the test's expected value is mathematically or logically wrong, fix the test.\n"
    prompt += "\n"
    prompt += "Return ONLY the unified diff, starting with --- and no other text."

    return prompt
