"""Agent module for AlwaysGreen.

Provide a minimal AgentState for CLI help/version and tests.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class AgentState:
    repo_path: Path
    max_iterations: int
    timeout_seconds: int
    branch_name: str | None = None
    current_iteration: int = 0
    patches_applied: List[str] = field(default_factory=list)
    initial_failures: int = 0
    total_failures: int = 0

    def increment_iteration(self) -> bool:
        self.current_iteration += 1
        return self.current_iteration <= self.max_iterations

    def add_failing_tests(self, tests: List[str]):
        self.initial_failures = len(tests)
        self.total_failures = len(tests)


__all__ = ["AgentState"]
