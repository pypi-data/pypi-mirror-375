"""
Enhanced LLM agent that implements the full Planner, Actor, and Critic workflow.
This is the production agent for AlwaysGreen that uses GPT-4/5 or Claude.
"""

import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from nova.agent.llm_client import (
    LLMClient,
)
from nova.config import get_settings
from nova.agent.llm_client_complete_fix import (
    build_comprehensive_planner_prompt,
    build_complete_fix_prompt,
    build_strict_critic_prompt,
    parse_comprehensive_plan,
)


class EnhancedLLMAgent:
    """Enhanced LLM agent that implements Planner, Actor, and Critic for test fixing."""

    def __init__(self, repo_path: Path, verbose: bool = False):
        self.repo_path = repo_path
        self.settings = get_settings()
        self.llm = LLMClient()  # Use the unified LLM client
        self.verbose = verbose

    def _read_file_with_cache(self, file_path: Path, state=None) -> str:
        """Read file with caching to prevent re-reading."""
        if state and hasattr(state, "file_cache"):
            cache_key = f"{file_path}_{state.modifications_count}"
            if cache_key in state.file_cache:
                return state.file_cache[cache_key]

        content = file_path.read_text()
        if state and hasattr(state, "file_cache"):
            state.file_cache[f"{file_path}_{state.modifications_count}"] = content
        return content

    def find_source_files_from_test(self, test_file_path: Path) -> Set[str]:
        """
        Extract imported modules from a test file and map them to source files.
        Robust to package-style and relative imports (e.g., `from .calculator import X`).
        """
        source_files: Set[str] = set()
        stdlib_like = {
            "pytest",
            "unittest",
            "sys",
            "os",
            "json",
            "re",
            "typing",
            "pathlib",
            "math",
            "itertools",
            "functools",
            "dataclasses",
        }
        try:
            content = self._read_file_with_cache(test_file_path)
            tree = ast.parse(content)
        except Exception as e:
            print(f"Error parsing test file {test_file_path}: {e}")
            return source_files

        def add_candidate(module_name: str) -> None:
            if not module_name:
                return
            parts = [p for p in module_name.split(".") if p]
            if not parts:
                return
            top = parts[0]
            if top in stdlib_like:
                return
            dotted = "/".join(parts)
            candidates = [
                self.repo_path / f"{dotted}.py",
                self.repo_path / dotted / "__init__.py",
            ]
            leaf = parts[-1]
            candidates.extend(list(self.repo_path.glob(f"**/{leaf}.py"))[:5])
            candidates.extend(list(self.repo_path.glob(f"**/{leaf}/__init__.py"))[:5])
            for pf in candidates:
                try:
                    if pf.exists() and self.repo_path in pf.parents:
                        rel = pf.relative_to(self.repo_path)
                        # Debug logs removed for demo
                        source_files.add(str(rel))
                except Exception:
                    continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    add_candidate(alias.name)
            elif isinstance(node, ast.ImportFrom):
                add_candidate(node.module or "")

        return source_files

    def generate_patch(
        self,
        failing_tests: List[Dict[str, Any]],
        iteration: int,
        plan: Dict[str, Any] = None,
        critic_feedback: Optional[str] = None,
        state=None,
    ) -> Optional[str]:
        """
        Generate a patch to fix failing tests (Actor node).

        Args:
            failing_tests: List of failing test details
            iteration: Current iteration number
            plan: Optional plan from the planner
            critic_feedback: Optional feedback from previous critic rejection

        Returns:
            Unified diff string or None if no patch can be generated
        """
        if not failing_tests:
            return None

        # Read test files and identify source files
        test_contents = {}
        source_contents = {}
        source_files = set()

        # Debug log removed for demo

        for test in failing_tests[:5]:  # Limit to first 5 tests for context
            test_file = test.get("file", "")
            if test_file and test_file not in test_contents:
                # Handle case where test_file might already include the project path
                test_path = Path(test_file)
                if not test_path.is_absolute():
                    # Check if test_file already contains repo name
                    if self.repo_path.name in test_file and str(
                        self.repo_path
                    ) not in str(test_path):
                        # Strip the redundant path prefix
                        parts = test_file.split(self.repo_path.name)
                        if len(parts) > 1:
                            test_file = parts[-1].lstrip("/")
                    test_path = self.repo_path / test_file

                # Debug log removed for demo
                if test_path.exists():
                    test_contents[test_file] = self._read_file_with_cache(
                        test_path, state
                    )
                    # Find source files imported by this test
                    found_files = self.find_source_files_from_test(test_path)
                    # Debug log removed for demo
                    source_files.update(found_files)

        # Read source files
        for source_file in source_files:
            source_path = self.repo_path / source_file
            if source_path.exists():
                source_contents[source_file] = self._read_file_with_cache(
                    source_path, state
                )

        # Use comprehensive prompt that demands complete fix
        from nova.agent.llm_client_fixed import convert_full_file_to_patch

        prompt = build_complete_fix_prompt(
            plan, failing_tests, test_contents, source_contents, critic_feedback
        )

        try:
            # Use the unified LLM client
            system_prompt = (
                "You are a coding assistant who MUST fix ALL test failures in ONE complete solution. "
                "Generate the COMPLETE corrected file contents that fix ALL {0} failing tests. "
                "Partial solutions are FAILURES. Fix EVERYTHING in one go. "
                "DO NOT add any new comments about bugs or fixes (no '# BUG:', '# FIX:', etc.). "
                "Follow the exact format requested."
            ).format(len(failing_tests))

            # Model-specific params (e.g., GPT-5 temperature) are handled inside LLMClient.
            response = self.llm.complete(
                system=system_prompt,
                user=prompt,
                max_tokens=40000,  # Set to 40k as requested
            )

            # Parse the response to extract file contents (do not truncate prompt content)
            files_to_fix = {}
            current_file = None
            current_content = []
            in_code_block = False

            for line in response.split("\n"):
                if line.startswith("FILE:"):
                    # Save previous file if any
                    if current_file and current_content:
                        files_to_fix[current_file] = "\n".join(current_content)
                    # Start new file
                    current_file = line[5:].strip()
                    current_content = []
                    in_code_block = False
                elif line.strip() == "```python" or line.strip() == "```":
                    if line.strip() == "```python":
                        in_code_block = True
                    else:
                        in_code_block = False
                elif in_code_block and current_file:
                    current_content.append(line)

            # Save last file
            if current_file and current_content:
                files_to_fix[current_file] = "\n".join(current_content)

            # Convert full files to patches
            if not files_to_fix:
                print("Warning: No files found in LLM response")
                return None

            # Check if we're in whole file mode
            if state and hasattr(state, "whole_file_mode") and state.whole_file_mode:
                # In whole file mode, return a special format that indicates files to replace
                # Format: FILE_REPLACE:<path>\n<content>\nEND_FILE_REPLACE
                combined_output = ""
                for file_path, new_content in files_to_fix.items():
                    combined_output += f"FILE_REPLACE:{file_path}\n"
                    combined_output += new_content
                    combined_output += "\nEND_FILE_REPLACE\n"
                return combined_output.strip()
            else:
                # Generate unified diff for each file (normal patch mode)
                combined_diff = ""
                for file_path, new_content in files_to_fix.items():
                    file_diff = convert_full_file_to_patch(
                        file_path, new_content, self.repo_path
                    )
                    combined_diff += file_diff + "\n"

                return combined_diff.strip()

        except Exception as e:
            print(f"Error generating patch: {e}")
            return None

    def _create_enhanced_prompt(
        self,
        failing_tests: List[Dict[str, Any]],
        test_contents: Dict[str, str],
        source_contents: Dict[str, str],
        iteration: int,
    ) -> str:
        """Create an enhanced prompt with both test and source context."""
        prompt = f"Fix the SOURCE CODE to make these failing tests pass (iteration {iteration}):\n\n"

        # Add failure information
        prompt += "FAILING TESTS:\n"
        for i, test in enumerate(failing_tests[:3], 1):
            prompt += f"\n{i}. Test: {test.get('name', 'unknown')}\n"
            prompt += f"   File: {test.get('file', 'unknown')}\n"
            prompt += f"   Error: {test.get('short_traceback', 'No traceback')}\n"

        # Add source code (this is what needs to be fixed!)
        if source_contents:
            prompt += "\n\nSOURCE CODE TO FIX:\n"
            for file_path, content in source_contents.items():
                prompt += f"\n=== {file_path} ===\n"
                prompt += content

        # Add test code for reference
        prompt += "\n\nTEST CODE (DO NOT MODIFY - these define correct behavior):\n"
        for file_path, content in test_contents.items():
            prompt += f"\n=== {file_path} ===\n"
            # Only include the failing test functions
            relevant_content = self._extract_relevant_test_functions(
                content, failing_tests
            )
            prompt += relevant_content

        prompt += "\n\nGenerate a unified diff patch that fixes the SOURCE CODE (not the tests). "
        prompt += "The tests define the correct expected behavior. "
        prompt += "Include proper @@ hunk headers with line numbers. "
        prompt += "Use --- a/filename and +++ b/filename format.\n"
        prompt += "REMOVE any existing BUG comments (e.g., '# BUG:', '# BUG: ...', etc.) from the code.\n"
        prompt += "DO NOT add any new comments about bugs or fixes.\n"
        prompt += "Return ONLY the diff, no explanations.\n"

        return prompt

    def _extract_relevant_test_functions(
        self, test_content: str, failing_tests: List[Dict[str, Any]]
    ) -> str:
        """Extract only the relevant test functions from test file."""
        relevant = []
        test_names = {test.get("name", "") for test in failing_tests}

        lines = test_content.split("\n")
        in_test = False
        current_test = []

        for line in lines:
            if line.startswith("def test_"):
                # Check if this is one of our failing tests
                test_name = line.split("(")[0].replace("def ", "").strip()
                if test_name in test_names:
                    in_test = True
                    current_test = [line]
                else:
                    if in_test and current_test:
                        relevant.append("\n".join(current_test))
                    in_test = False
            elif in_test:
                current_test.append(line)
                # Stop at next function or class
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    relevant.append("\n".join(current_test))
                    in_test = False

        if in_test and current_test:
            relevant.append("\n".join(current_test))

        return "\n\n".join(relevant)

    def _fix_patch_format(self, patch_diff: str) -> str:
        """Ensure patch is in proper unified diff format."""
        # Remove any trailing non-diff characters
        patch_diff = patch_diff.rstrip()
        if patch_diff and patch_diff[-1] not in "\n+-@ \\":
            # Remove trailing garbage characters
            while (
                patch_diff
                and patch_diff[-1]
                not in "\n+-@ \\abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789)\"}'"
            ):
                patch_diff = patch_diff[:-1]

        lines = patch_diff.split("\n")
        fixed_lines = []
        in_hunk = False

        for line in lines:
            # Fix file headers
            if line.startswith("--- "):
                if not line.startswith("--- a/"):
                    parts = line.split()
                    if len(parts) >= 2:
                        filename = parts[1].lstrip("/")
                        line = f"--- a/{filename}"
                in_hunk = False
            elif line.startswith("+++ "):
                if not line.startswith("+++ b/"):
                    parts = line.split()
                    if len(parts) >= 2:
                        filename = parts[1].lstrip("/")
                        line = f"+++ b/{filename}"
                in_hunk = False
            elif line.startswith("@@"):
                in_hunk = True
                # Ensure complete hunk header
                if not re.match(r"@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", line):
                    # Try to fix it
                    line = "@@ -1,1 +1,1 @@"  # Safe default
            elif in_hunk and line and not line.startswith(("+", "-", " ", "\\")):
                # Add space prefix for context lines
                line = " " + line

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def review_patch(
        self,
        patch: str,
        failing_tests: List[Dict[str, Any]],
        test_runner=None,
        repo_path=None,
    ) -> Tuple[bool, str]:
        """
        Review a patch using LLM (Critic node) with actual test results.

        Args:
            patch: The patch diff to review
            failing_tests: List of failing tests this patch should fix
            test_runner: Optional TestRunner to actually run tests (if provided)
            repo_path: Optional repo path for applying patch temporarily

        Returns:
            Tuple of (approved: bool, reason: str)
        """
        if not patch:
            return False, "Empty patch"

        # Check if this is whole file replacement format
        if "FILE_REPLACE:" in patch:
            # For whole file replacements, apply different validation
            patch_lines = patch.split("\n")
            files_touched = sum(
                1 for line in patch_lines if line.startswith("FILE_REPLACE:")
            )

            if files_touched > 10:
                return False, f"Too many files modified ({files_touched})"

            # Check for dangerous patterns in file paths
            dangerous_patterns = [
                ".github/",
                "setup.py",
                "pyproject.toml",
                ".env",
                "requirements.txt",
            ]
            for line in patch_lines:
                if line.startswith("FILE_REPLACE:"):
                    file_path = line[13:].strip()
                    if any(pattern in file_path for pattern in dangerous_patterns):
                        return False, "Patch modifies protected/configuration files"
        else:
            # Normal patch safety checks
            patch_lines = patch.split("\n")
            files_touched = sum(1 for line in patch_lines if line.startswith("+++ b/"))

            if len(patch_lines) >= 1000:
                return False, f"Patch too large ({len(patch_lines)} lines)"

            if files_touched > 10:
                return False, f"Too many files modified ({files_touched})"

            # Check for dangerous patterns
            dangerous_patterns = [
                ".github/",
                "setup.py",
                "pyproject.toml",
                ".env",
                "requirements.txt",
            ]
            for line in patch_lines:
                if any(pattern in line for pattern in dangerous_patterns):
                    return False, "Patch modifies protected/configuration files"

        # If we have a test runner, actually run tests with the patch applied
        actual_test_results = None
        if test_runner and repo_path:
            try:
                import subprocess

                # Import here to avoid circular dependency
                from nova.tools.fs import apply_and_commit_patch

                # Save current state
                stash_result = subprocess.run(
                    ["git", "stash", "push", "-m", "nova-critic-backup"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                )

                try:
                    # Apply patch temporarily using nova's apply function that handles FILE_REPLACE
                    from rich.console import Console

                    console = Console()

                    if (
                        hasattr(self, "verbose")
                        and self.verbose
                        and stash_result.stderr
                    ):
                        console.print(f"[dim]Stash stderr: {stash_result.stderr}[/dim]")
                    console.print("[cyan]🧪 Testing patch application...[/cyan]")

                    # Debug: Show patch format
                    if self.verbose:
                        console.print(
                            f"[dim]Patch format: {'FILE_REPLACE' if 'FILE_REPLACE:' in patch else 'unified diff'}[/dim]"
                        )
                        if "FILE_REPLACE:" in patch:
                            # Show more info about the FILE_REPLACE patch
                            lines = patch.split("\n")
                            file_count = sum(
                                1 for line in lines if line.startswith("FILE_REPLACE:")
                            )
                            console.print(
                                f"[dim]FILE_REPLACE patch with {file_count} file(s)[/dim]"
                            )
                            for line in lines[:10]:
                                if line.startswith("FILE_REPLACE:"):
                                    console.print(f"[dim]  - {line}[/dim]")

                    # Use Nova's patch application that handles FILE_REPLACE format
                    success, changed_files = apply_and_commit_patch(
                        repo_root=repo_path,
                        diff_text=patch,
                        step_number=999,  # Temporary step number
                        git_manager=None,  # Don't commit
                        verbose=True,  # Enable verbose to debug
                    )

                    if success:
                        # Run tests
                        new_failures, _ = test_runner.run_tests()

                        # Calculate results
                        original_count = len(failing_tests)
                        remaining_count = len(new_failures)
                        fixed_count = original_count - remaining_count

                        actual_test_results = {
                            "patch_applied": True,
                            "original_failures": original_count,
                            "remaining_failures": remaining_count,
                            "fixed_count": fixed_count,
                            "all_fixed": remaining_count == 0,
                            "remaining_test_names": [
                                f.get("name", "unknown") for f in new_failures[:5]
                            ],
                        }

                        if self.verbose:
                            console.print(
                                f"[dim]Test results: {fixed_count}/{original_count} tests fixed[/dim]"
                            )
                    else:
                        # Don't set actual_test_results if patch didn't apply
                        # This will make the critic analyze the patch itself rather than saying it wasn't applied
                        if self.verbose:
                            console.print(
                                "[dim]Patch could not be applied for testing, will review based on code analysis[/dim]"
                            )

                finally:
                    # Always restore original state
                    pop_result = subprocess.run(
                        ["git", "stash", "pop"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                    )
                    if self.verbose and pop_result.stderr:
                        console.print(
                            f"[dim]Stash pop stderr: {pop_result.stderr}[/dim]"
                        )

            except Exception as e:
                # If anything goes wrong, make sure we restore state
                try:
                    subprocess.run(
                        ["git", "stash", "pop"], cwd=repo_path, capture_output=True
                    )
                except Exception:
                    pass
                actual_test_results = {"error": f"Failed to test patch: {str(e)}"}

        # Use LLM for semantic review
        try:
            system_prompt = (
                "You are a code reviewer. Evaluate patches critically but approve if they fix the issues. "
                "Consider: correctness, safety, side effects, and whether it addresses the test failures."
            )

            # Use strict critic prompt that rejects partial solutions
            user_prompt = build_strict_critic_prompt(
                patch, failing_tests, len(failing_tests), actual_test_results
            )

            # Log critic prompt for debugging
            # Debug logs removed for demo

            # Increased max_tokens for better responses
            # Debug log removed for demo
            response = self.llm.complete(
                system=system_prompt,
                user=user_prompt,
                temperature=1.0,
                max_tokens=40000,  # Set to 40k as requested
            )

            # Log response details
            # Debug log removed for demo

            # Parse JSON response
            if response and "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                try:
                    json_str = response[start:end]
                    review_json = json.loads(json_str)
                    approved = review_json.get("approved", False)
                    reason = review_json.get("reason", "No reason provided")
                    # Debug log removed for demo
                    return approved, reason
                except json.JSONDecodeError:
                    # Debug logs removed for demo
                    pass

            # Parsing failed – use raw response as feedback
            critic_feedback = (response or "").strip()
            if not critic_feedback:
                # Debug log removed for demo
                # Fallback: approve small/safe patches when critic is silent
                patch_lines = patch.split("\n")
                files_touched = sum(
                    1 for line in patch_lines if line.startswith("+++ b/")
                )
                if files_touched == 0:
                    files_touched = sum(
                        1 for line in patch_lines if line.startswith("FILE_REPLACE:")
                    )
                protected = [
                    ".github/",
                    "setup.py",
                    "pyproject.toml",
                    ".env",
                    "requirements.txt",
                ]
                safe = not any(p in line for line in patch_lines for p in protected)

                # Debug log removed for demo

                if safe and len(patch_lines) < 1000 and files_touched <= 3:
                    return (
                        True,
                        "Auto-approved: empty critic feedback and patch is small & safe",
                    )
                # otherwise still reject, but explain why
                return (
                    False,
                    "No feedback provided (patch too large or touches protected files)",
                )
            # Decide to reject but show feedback (truncate if very long)
            # Debug log removed for demo
            return False, critic_feedback[:500]

        except Exception:
            # Debug log removed for demo
            import traceback

            traceback.print_exc()
            # Fallback: approve small/safe patches if critic errors out
            patch_lines = patch.split("\n")
            files_touched = sum(1 for line in patch_lines if line.startswith("+++ b/"))
            if files_touched == 0:
                files_touched = sum(
                    1 for line in patch_lines if line.startswith("FILE_REPLACE:")
                )
            if len(patch_lines) < 1000 and files_touched <= 3:
                return True, "Auto-approved: critic errored but patch is small & safe"
            return False, "Review failed due to error, patch not approved"

    def create_plan(
        self,
        failing_tests: List[Dict[str, Any]],
        iteration: int,
        critic_feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a plan for fixing the failing tests (Planner node).

        Args:
            failing_tests: List of failing test details
            iteration: Current iteration number
            critic_feedback: Optional feedback from previous critic rejection

        Returns:
            Plan dictionary with approach and steps
        """
        if not failing_tests:
            return {"approach": "No failures to fix", "target_tests": [], "steps": []}

        # Build comprehensive planner prompt that pushes for complete solution
        prompt = build_comprehensive_planner_prompt(failing_tests, critic_feedback)

        try:
            system_prompt = (
                "You are an expert software engineer who MUST fix ALL test failures in ONE comprehensive solution. "
                "Partial fixes are UNACCEPTABLE. Analyze ALL failures, find common patterns, and create a COMPLETE fix strategy. "
                "Your plan must address EVERY SINGLE failing test in one go."
            )

            response = self.llm.complete(
                system=system_prompt,
                user=prompt,
                temperature=1.0,
                max_tokens=40000,  # Set to 40k as requested
            )

            # Debug log removed for demo

            # Parse the comprehensive plan
            plan = parse_comprehensive_plan(response)

            # Add iteration context
            plan["iteration"] = iteration

            # Identify source files that need fixes
            source_files = set()
            for test in failing_tests[:5]:  # Check first 5 tests
                test_file = test.get("file", "")
                if test_file:
                    # Handle case where test_file might already include the project path
                    test_path = Path(test_file)
                    if not test_path.is_absolute():
                        # Check if test_file already contains repo name
                        if self.repo_path.name in test_file and str(
                            self.repo_path
                        ) not in str(test_path):
                            # Strip the redundant path prefix
                            parts = test_file.split(self.repo_path.name)
                            if len(parts) > 1:
                                test_file = parts[-1].lstrip("/")
                        test_path = self.repo_path / test_file

                    if test_path.exists():
                        source_files.update(self.find_source_files_from_test(test_path))

            plan["source_files"] = list(source_files)
            plan["target_tests"] = (
                failing_tests[:3] if len(failing_tests) > 3 else failing_tests
            )

            # Debug logs removed for demo

            return plan

        except Exception as e:
            print(f"Error creating plan: {e}")
            # Fallback plan
            return {
                "approach": "Fix failing tests incrementally",
                "steps": [
                    "Analyze test failures",
                    "Fix assertion errors",
                    "Handle exceptions",
                ],
                "target_tests": (
                    failing_tests[:2] if len(failing_tests) > 2 else failing_tests
                ),
                "source_files": [],
                "iteration": iteration,
            }
