#!/usr/bin/env python3
"""
AlwaysGreen CLI interface.
"""

import os
import re
import json
import time
import subprocess
import typer
from pathlib import Path
from typing import Optional
from datetime import datetime
from nova.tools.datetime_utils import now_utc, seconds_between
from rich.console import Console
from rich.table import Table

from nova.runner import TestRunner
from nova.agent import AgentState
from nova.config import NovaSettings, get_settings
from nova.tools.git import GitBranchManager
from nova.telemetry.logger import JSONLLogger

app = typer.Typer(
    name="nova",
    help="AlwaysGreen: Automated test fixing agent",
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-V", help="Show Nova version and exit", is_eager=True
    ),
):
    """
    AlwaysGreen: Automated test fixing agent.

    Main callback to handle global options like --version.
    """
    if version:
        from nova import __version__

        console.print(f"[green]AlwaysGreen[/green] v{__version__}")
        raise typer.Exit()

    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


def print_exit_summary(
    state: AgentState, reason: str, elapsed_seconds: float = None
) -> None:
    """
    Print a comprehensive summary when exiting the agent loop.

    Args:
        state: The current agent state
        reason: The reason for exit (timeout, max_iters, success, etc.)
        elapsed_seconds: Optional elapsed time in seconds
    """
    console.print("\n" + "=" * 60)
    console.print("[bold]EXECUTION SUMMARY[/bold]")
    console.print("=" * 60)

    # Exit reason with appropriate styling
    if reason == "success":
        console.print(
            "[bold green]✅ Exit Reason: SUCCESS - All tests passing![/bold green]"
        )
    elif reason == "timeout":
        console.print(
            f"[bold red]⏰ Exit Reason: TIMEOUT - Exceeded {state.timeout_seconds}s limit[/bold red]"
        )
    elif reason == "max_iters":
        console.print(
            f"[bold red]🔄 Exit Reason: MAX ITERATIONS - Reached {state.max_iterations} iterations[/bold red]"
        )
    elif reason == "no_patch":
        console.print(
            "[bold yellow]⚠️ Exit Reason: NO PATCH - Could not generate fix[/bold yellow]"
        )
    elif reason == "patch_rejected":
        console.print(
            "[bold yellow]⚠️ Exit Reason: PATCH REJECTED - Critic rejected patch[/bold yellow]"
        )
    elif reason == "patch_error":
        console.print(
            "[bold red]❌ Exit Reason: PATCH ERROR - Failed to apply patch[/bold red]"
        )
    elif reason == "interrupted":
        console.print(
            "[bold yellow]🛑 Exit Reason: INTERRUPTED - User cancelled operation[/bold yellow]"
        )
    elif reason == "error":
        console.print(
            "[bold red]❌ Exit Reason: ERROR - Unexpected error occurred[/bold red]"
        )
    else:
        console.print(f"[bold yellow]Exit Reason: {reason.upper()}[/bold yellow]")

    console.print()

    # Statistics
    console.print("[bold]Statistics:[/bold]")
    console.print(
        f"  • Iterations completed: {state.current_iteration}/{state.max_iterations}"
    )
    console.print(f"  • Patches applied: {len(state.patches_applied)}")
    console.print(f"  • Initial failures: {state.initial_failures}")
    console.print(f"  • Remaining failures: {state.total_failures}")

    if state.total_failures == 0:
        console.print("  • [green]All tests fixed successfully![/green]")
    elif state.failing_tests and state.total_failures < len(state.failing_tests):
        fixed = len(state.failing_tests) - state.total_failures
        console.print(f"  • Tests fixed: {fixed}/{len(state.failing_tests)}")

    # Time elapsed
    if elapsed_seconds is not None:
        minutes, seconds = divmod(int(elapsed_seconds), 60)
        console.print(f"  • Time elapsed: {minutes}m {seconds}s")
    elif hasattr(state, "start_time") and state.start_time:
        # Handle both datetime and float start_time
        if isinstance(state.start_time, float):
            elapsed = time.time() - state.start_time
        else:
            elapsed = seconds_between(now_utc(), state.start_time)
        minutes, seconds = divmod(int(elapsed), 60)
        console.print(f"  • Time elapsed: {minutes}m {seconds}s")

    # List saved patches if telemetry is enabled

    settings = get_settings()
    if settings.enable_telemetry and hasattr(state, "telemetry") and state.telemetry:
        try:
            from pathlib import Path

            run_dir = state.telemetry.run_dir
            if run_dir and Path(run_dir).exists():
                patch_dir = Path(run_dir) / "patches"
                if patch_dir.exists():
                    console.print("\n[bold]📄 Saved patches:[/bold]")
                    patches = sorted(patch_dir.glob("*.patch"))
                    if patches:
                        for patch_file in patches:
                            console.print(f"  • {patch_file.name}")
                        console.print(f"  [dim](Saved in: {patch_dir})[/dim]")
                    else:
                        console.print("  [dim](No patches saved)[/dim]")
        except Exception as e:
            if getattr(state, "verbose", False):
                console.print(f"[dim]Could not list patches: {e}[/dim]")

    console.print("=" * 60)
    console.print()


@app.command()
def fix(
    repo_path: Path = typer.Argument(
        Path("."),
        help="Path to repository to fix",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    max_iters: Optional[int] = typer.Option(
        None,
        "--max-iters",
        "-i",
        help="Maximum number of fix iterations (default: 6)",
        min=1,
        max=20,
    ),
    timeout: Optional[int] = typer.Option(
        None,
        "--timeout",
        "-t",
        help="Overall timeout in seconds (default: 1200)",
        min=60,
        max=7200,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to YAML configuration file (options in file are used unless overridden by CLI flags)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    legacy_agent: bool = typer.Option(
        False,
        "--legacy-agent",
        help="Use the legacy v1.0 LLM-based agent instead of the default LangChain Deep Agent",
        is_flag=True,
    ),
    ci_cmd: Optional[str] = typer.Option(
        None,
        "--ci",
        help="Custom test command to run (e.g., 'python -m unittest -q', 'nosetests -q', 'npm test -- --ci')",
    ),
    junit_report: Optional[Path] = typer.Option(
        None,
        "--junit-report",
        help="Path to JUnit XML report produced by the test command (for non-pytest runners)",
        exists=False,
        file_okay=True,
        dir_okay=False,
        resolve_path=False,
    ),
):
    """
    Fix failing tests in a repository using an AI agent.

    By default, uses the Nova Deep Agent (LangChain-based) for iterative fixes.
    Use the --legacy-agent flag to run the deprecated v1.0 LLM-based agent pipeline.
    """
    # Load configuration (YAML auto-discovery with overrides)
    from nova.config_loader import load_alwaysgreen_settings, ConfigError as AGConfigError
    cli_overrides: Dict[str, Any] = {}
    # Removed malformed conditional for 'model' (not a parameter)
    # if model is not None if 'model' in locals() else False:
    #     cli_overrides["model"] = model
    if ci_cmd is not None:
        cli_overrides["ci_cmd"] = ci_cmd
    try:
        ag_settings = load_alwaysgreen_settings(repo_path, config_path=config_file, cli_overrides=cli_overrides)
    except AGConfigError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(2)

    # Back-compat: some paths still refer to `config_data`; alias to loaded settings
    config_data = ag_settings

    # Back-compat alias (many references below use config_data)
    config_data = ag_settings

    # Respect model override from YAML if present
    if getattr(ag_settings, "model", None):
        try:
            settings = NovaSettings()
            settings.default_llm_model = ag_settings.model
        except Exception:
            pass

    # Determine effective iteration count and timeout
    final_max_iters = (
        max_iters
        if max_iters is not None
        else (
            ag_settings.limits.max_attempts
            if ag_settings and getattr(ag_settings, "limits", None) and ag_settings.limits.max_attempts is not None
            else 6
        )
    )
    final_timeout = (
        timeout
        if timeout is not None
        else 1200
    )

    console.print("[green]AlwaysGreen[/green] 🚀")
    if config_file:
        console.print(f"[dim]Loaded configuration from {config_file}[/dim]")

    # Initialize Git branch management
    git_manager = GitBranchManager(repo_path)
    state = None
    telemetry = None
    success = False

    # Check for concurrent runs

    try:
        branch_name = git_manager.create_fix_branch()
        console.print(f"[dim]Working on branch: {branch_name}[/dim]")

        # Set up Ctrl+C signal handler for clean abort
        git_manager.setup_signal_handler()

        # Initialize settings and telemetry
        settings = NovaSettings()
        if config_data and config_data.model:
            settings.default_llm_model = config_data.model
        telemetry = JSONLLogger()
        # Resolve model with fallback chain
        from nova.tools.model_selector import select_model
        selection = select_model(settings.default_llm_model)
        telemetry.log_event(
            "run_start",
            {
                "repo": str(repo_path),
                "model": selection.chosen,
                "fallback_tried": selection.tried,
                "max_iterations": final_max_iters,
                "timeout": final_timeout,
            },
        )
        if selection.chosen != settings.default_llm_model and verbose:
            console.print(
                f"[yellow]Model fallback: {settings.default_llm_model} → {selection.chosen} ({selection.tried[-1][1]})[/yellow]"
            )

        # Initialize agent state and run initial tests
        state = AgentState(
            repo_path=repo_path,
            max_iterations=final_max_iters,
            timeout_seconds=final_timeout,
        )

        # Step 1: Run tests to identify initial failures
        # Prefer CLI --ci overrides config; else fall back to config if present
        custom_cmd = ci_cmd or (config_data.ci_cmd if config_data and hasattr(config_data, "ci_cmd") else None)
        junit_path = str(junit_report) if junit_report else (
            getattr(config_data, "junit_report", None) if config_data else None
        )

        runner = TestRunner(
            repo_path,
            verbose=verbose,
            custom_cmd=custom_cmd,
            junit_report_path=junit_path,
        )
        failing_tests, initial_junit_xml = runner.run_tests()

        # Optional fault localization (mark suspected files based on tracebacks)
        try:
            from nova.runner.test_runner import FaultLocalizer

            FaultLocalizer.localize_failures(failing_tests, coverage_data=None)
        except Exception:
            pass

        # Save initial test report
        if initial_junit_xml:
            telemetry.save_test_report(0, initial_junit_xml, report_type="junit")

        # Record initial failures in state
        state.add_failing_tests(failing_tests)
        telemetry.log_event(
            "test_discovery",
            {
                "total_failures": state.total_failures,
                "failing_tests": state.failing_tests,
                "initial_report_saved": initial_junit_xml is not None,
            },
        )

        # If no failures, nothing to fix
        if not failing_tests:
            console.print(
                "[green]✅ No failing tests found! Repository is already green.[/green]"
            )
            state.final_status = "success"
            telemetry.log_event("completion", {"status": "no_failures"})
            telemetry.end_run(success=True)
            # Post no-failure result to GitHub if applicable
            token = os.getenv("GITHUB_TOKEN")
            repo = os.getenv("GITHUB_REPOSITORY")
            pr_num = os.getenv("PR_NUMBER")
            if not pr_num:
                pr_num = os.getenv("GITHUB_EVENT_NUMBER")
                if not pr_num:
                    github_ref = os.getenv("GITHUB_REF")
                    if github_ref and "pull/" in github_ref:
                        match = re.search(r"pull/(\d+)/", github_ref)
                        if match:
                            pr_num = match.group(1)
                if not pr_num:
                    event_path = os.getenv("GITHUB_EVENT_PATH")
                    if event_path and os.path.exists(event_path):
                        try:
                            with open(event_path, "r") as f:
                                event_data = json.load(f)
                            if "pull_request" in event_data:
                                pr_num = str(event_data["pull_request"]["number"])
                        except Exception:
                            pass
            if token and repo:
                try:
                    from nova.github_integration import (
                        GitHubAPI,
                        RunMetrics,
                        ReportGenerator,
                    )

                    api = GitHubAPI(token)
                    metrics = RunMetrics(
                        runtime_seconds=0,
                        iterations=0,
                        files_changed=0,
                        status="success",
                        tests_fixed=0,
                        tests_remaining=0,
                        initial_failures=0,
                        final_failures=0,
                    )
                    head_sha = git_manager._get_current_head() if git_manager else None
                    if head_sha:
                        api.create_check_run(
                            repo=repo,
                            sha=head_sha,
                            name="CI-Auto-Rescue",
                            status="completed",
                            conclusion="success",
                            title="CI-Auto-Rescue: No failing tests",
                            summary="✅ No failing tests found - repository is already green!",
                        )
                        if verbose:
                            console.print("[dim]✅ Posted check run to GitHub[/dim]")
                    if pr_num:
                        api.create_pr_comment(
                            repo=repo,
                            pr_number=int(pr_num),
                            body="## ✅ AlwaysGreen: No failing tests to fix! 🎉\n\nAll tests are passing.",
                        )
                        if verbose:
                            console.print("[dim]✅ Posted PR comment to GitHub[/dim]")
                except Exception as e:
                    if verbose:
                        console.print(
                            f"[yellow]⚠️ GitHub reporting failed: {e}[/yellow]"
                        )
            return

        # Display failing tests summary table (up to first 10 failures)
        console.print(
            f"\n[bold red]Found {len(failing_tests)} failing test(s):[/bold red]"
        )
        table = Table(
            title="Failing Tests", show_header=True, header_style="bold magenta"
        )
        table.add_column("Test Name", style="cyan", no_wrap=False)
        table.add_column("Location", style="yellow")
        table.add_column("Error", style="red", no_wrap=False)
        for test in failing_tests[:10]:
            location = f"{test.file}:{test.line}" if hasattr(test, "file") else "N/A"
            error_preview = (
                test.short_traceback.split("\n")[0]
                if hasattr(test, "short_traceback")
                else str(test)
            )
            if len(error_preview) > 60:
                error_preview = error_preview[:60] + "..."
            name = getattr(test, "name", str(test))
            table.add_row(name, location, error_preview)
        if len(failing_tests) > 10:
            table.add_row("...", f"... and {len(failing_tests)-10} more", "")
        console.print(table)
        console.print()

        # Prepare safety limits configuration from YAML (if provided)
        safety_conf = None
        from nova.tools.safety_limits import SafetyConfig
        # Prefer .github/nova.yml if present; otherwise use parsed config_data
        yaml_cfg = None
        try:
            from pathlib import Path as _P
            candidate = _P(repo_path) / ".github" / "nova.yml"
            if candidate.exists():
                yaml_cfg = candidate
        except Exception:
            yaml_cfg = None

        if yaml_cfg:
            safety_conf = SafetyConfig(yaml_cfg)
        elif config_data:
            # Build SafetyConfig from parsed config_data object
            safety_conf_obj = SafetyConfig()
            if getattr(config_data, "max_changed_lines", None) is not None:
                safety_conf_obj.safety_limits.max_lines_changed = config_data.max_changed_lines
            if getattr(config_data, "max_changed_files", None) is not None:
                safety_conf_obj.safety_limits.max_files_modified = config_data.max_changed_files
            if getattr(config_data, "blocked_paths", None):
                for pattern in config_data.blocked_paths:
                    if pattern not in safety_conf_obj.safety_limits.restricted_paths:
                        safety_conf_obj.safety_limits.restricted_paths.append(pattern)
            safety_conf = safety_conf_obj

        # Either run the Deep Agent or the legacy agent loop
        # Determine which agent to use (precedence: CLI flag > env var > YAML config)
        use_legacy_env = os.getenv("NOVA_USE_LEGACY_AGENT", "").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        use_legacy_cfg = False
        agent_cfg_legacy = False
        if isinstance(config_data, dict) and config_data:
            try:
                use_legacy_cfg = bool(config_data.get("use_legacy_agent", False))
                agent_cfg_legacy = str(config_data.get("agent", "")).lower() in (
                    "legacy",
                    "llm",
                    "regular",
                )
            except Exception:
                # Be resilient to malformed YAML
                use_legacy_cfg = False
                agent_cfg_legacy = False
        effective_legacy_agent = legacy_agent or use_legacy_env or use_legacy_cfg or agent_cfg_legacy

        success = False
        if not effective_legacy_agent:
            console.print("[cyan]Using regular agent path with risk policy.[/cyan]")
            # Evaluate risk for any prospective patch (placeholder: no generated patch in this path)
            from nova.tools.safety_limits import SafetyLimits
            safety = SafetyLimits()
            changed_files = []
            lines_changed = 0
            patch_text = ""
            risk, reason = safety.assess_patch_risk(changed_files, lines_changed, patch_text)
            console.print(f"[dim]Risk category: {risk} — {reason}[/dim]")

            # In this build we do not auto-apply patches here; enforce suggest-only for non-low risk
            if risk == "high" and safety.block_high_risk:
                console.print("[yellow]High-risk changes would be suggested only (no auto-commit).[/yellow]")
            elif risk == "medium" and safety.suggest_medium_risk:
                console.print("[yellow]Medium-risk changes would be suggested (no auto-commit).[/yellow]")
            elif risk == "low" and safety.auto_commit_low_risk:
                console.print("[green]Low-risk changes are eligible for auto-commit by policy.[/green]")

            # Summarize
            success = state.total_failures == 0
            state.final_status = "success" if success else "failure"
            telemetry.log_event(
                "completion",
                {
                    "status": state.final_status,
                    "iterations": state.current_iteration,
                    "total_patches": len(state.patches_applied),
                    "final_failures": state.total_failures,
                },
            )
        else:
            # Legacy path disabled – use regular agent behavior with risk policy
            console.print(
                "[yellow]Ignoring legacy agent path; using regular agent with risk policy.[/yellow]"
            )
            from nova.tools.safety_limits import SafetyLimits
            safety = SafetyLimits()
            risk, reason = safety.assess_patch_risk([], 0, "")
            console.print(f"[dim]Risk category: {risk} — {reason}[/dim]")
            success = state.total_failures == 0
            state.final_status = "success" if success else "failure"

        # Log completion status
        telemetry.log_event(
            "completion",
            {
                "status": state.final_status,
                "iterations": state.current_iteration,
                "total_patches": len(state.patches_applied),
                "final_failures": state.total_failures,
            },
        )
        # Print comprehensive exit summary
        if state and state.final_status:
            elapsed = (datetime.now() - state.start_time).total_seconds()
            print_exit_summary(state, state.final_status, elapsed_seconds=elapsed)

        telemetry.end_run(success=(state.final_status == "success"))

        # GitHub integration: post results to PR if in CI environment
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")
        pr_num = os.getenv("PR_NUMBER") or os.getenv("GITHUB_EVENT_NUMBER") or None
        if not pr_num:
            github_ref = os.getenv("GITHUB_REF")
            if github_ref and "pull/" in github_ref:
                match = re.search(r"pull/(\d+)/", github_ref)
                if match:
                    pr_num = match.group(1)
            if not pr_num:
                event_path = os.getenv("GITHUB_EVENT_PATH")
                if event_path and os.path.exists(event_path):
                    try:
                        with open(event_path, "r") as f:
                            event_data = json.load(f)
                        if "pull_request" in event_data:
                            pr_num = str(event_data["pull_request"]["number"])
                    except Exception:
                        pass
        if token and repo:
            try:
                from nova.github_integration import (
                    GitHubAPI,
                    RunMetrics,
                    ReportGenerator,
                )

                elapsed = (datetime.now() - state.start_time).total_seconds()
                # Count unique files changed across all applied patches
                files_changed = set()
                if state.patches_applied:
                    from nova.tools.safety_limits import SafetyLimits

                    safety = SafetyLimits()
                    for patch in state.patches_applied:
                        analysis = safety.analyze_patch(patch)
                        files_changed.update(
                            analysis.files_modified | analysis.files_added
                        )
                metrics = RunMetrics(
                    runtime_seconds=int(elapsed),
                    iterations=state.current_iteration,
                    files_changed=len(files_changed),
                    status="success" if success else (state.final_status or "failure"),
                    tests_fixed=(
                        len(state.failing_tests) - state.total_failures
                        if state.failing_tests
                        else 0
                    ),
                    tests_remaining=state.total_failures,
                    initial_failures=(
                        len(state.failing_tests) if state.failing_tests else 0
                    ),
                    final_failures=state.total_failures,
                    branch_name=branch_name,
                )
                api = GitHubAPI(token)
                generator = ReportGenerator()
                head_sha = git_manager._get_current_head() if git_manager else None
                if head_sha:
                    api.create_check_run(
                        repo=repo,
                        sha=head_sha,
                        name="CI-Auto-Rescue",
                        status="completed",
                        conclusion="success" if success else "failure",
                        title=f"CI-Auto-Rescue: {metrics.status.upper()}",
                        summary=generator.generate_check_summary(metrics),
                    )
                    if verbose:
                        console.print("[dim]✅ Posted check run to GitHub[/dim]")
                if pr_num:
                    existing_id = api.find_pr_comment(
                        repo, int(pr_num), "<!-- ci-auto-rescue-report -->"
                    )
                    comment_body = generator.generate_pr_comment(metrics)
                    if existing_id:
                        api.update_pr_comment(repo, existing_id, comment_body)
                        if verbose:
                            console.print("[dim]✅ Updated existing PR comment[/dim]")
                    else:
                        api.create_pr_comment(repo, int(pr_num), comment_body)
                        if verbose:
                            console.print("[dim]✅ Created new PR comment[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠️ GitHub reporting failed: {e}[/yellow]")
                if verbose:
                    import traceback

                    console.print(f"[dim]{traceback.format_exc()}[/dim]")

        branch_name = git_manager.create_fix_branch()
        console.print(f"[dim]Working on branch: {branch_name}[/dim]")

        # Set up Ctrl+C signal handler for clean abort
        git_manager.setup_signal_handler()

        # Initialize settings and telemetry
        settings = NovaSettings()
        if config_data and config_data.model:
            settings.default_llm_model = config_data.model
        telemetry = JSONLLogger()
        telemetry.log_event(
            "run_start",
            {
                "repo": str(repo_path),
                "model": settings.default_llm_model,
                "max_iterations": final_max_iters,
                "timeout": final_timeout,
            },
        )

        # Initialize agent state
        state = AgentState(
            repo_path=repo_path,
            max_iterations=final_max_iters,
            timeout_seconds=final_timeout,
        )

        # Step 1: Run tests to identify initial failures
        runner = TestRunner(repo_path, verbose=verbose)
        failing_tests, initial_junit_xml = runner.run_tests()

        # Optional fault localization (mark suspected files based on tracebacks)
        try:
            from nova.runner.test_runner import FaultLocalizer

            FaultLocalizer.localize_failures(failing_tests, coverage_data=None)
        except Exception:
            pass

        # Save initial test report
        if initial_junit_xml:
            telemetry.save_test_report(0, initial_junit_xml, report_type="junit")

        # Record initial failures in state
        state.add_failing_tests(failing_tests)
        telemetry.log_event(
            "test_discovery",
            {
                "total_failures": state.total_failures,
                "failing_tests": state.failing_tests,
                "initial_report_saved": initial_junit_xml is not None,
            },
        )

        # If no failures, nothing to fix
        if not failing_tests:
            if verbose:
                console.print(
                    "[green]✅ Repository is already green - no failing tests found.[/green]"
                )
            state.final_status = "success"
            telemetry.log_event("completion", {"status": "no_failures"})
            telemetry.end_run(success=True)
            # Post no-failure result to GitHub if applicable
            token = os.getenv("GITHUB_TOKEN")
            repo = os.getenv("GITHUB_REPOSITORY")
            pr_num = os.getenv("PR_NUMBER")
            if not pr_num:
                pr_num = os.getenv("GITHUB_EVENT_NUMBER")
                if not pr_num:
                    github_ref = os.getenv("GITHUB_REF")
                    if github_ref and "pull/" in github_ref:
                        match = re.search(r"pull/(\d+)/", github_ref)
                        if match:
                            pr_num = match.group(1)
                if not pr_num:
                    event_path = os.getenv("GITHUB_EVENT_PATH")
                    if event_path and os.path.exists(event_path):
                        try:
                            with open(event_path, "r") as f:
                                event_data = json.load(f)
                            if "pull_request" in event_data:
                                pr_num = str(event_data["pull_request"]["number"])
                        except Exception:
                            pass
            if token and repo:
                try:
                    from nova.github_integration import (
                        GitHubAPI,
                        RunMetrics,
                        ReportGenerator,
                    )

                    api = GitHubAPI(token)
                    metrics = RunMetrics(
                        runtime_seconds=0,
                        iterations=0,
                        files_changed=0,
                        status="success",
                        tests_fixed=0,
                        tests_remaining=0,
                        initial_failures=0,
                        final_failures=0,
                    )
                    head_sha = git_manager._get_current_head() if git_manager else None
                    if head_sha:
                        api.create_check_run(
                            repo=repo,
                            sha=head_sha,
                            name="CI-Auto-Rescue",
                            status="completed",
                            conclusion="success",
                            title="CI-Auto-Rescue: No failing tests",
                            summary="✅ No failing tests found - repository is already green!",
                        )
                        if verbose:
                            console.print("[dim]✅ Posted check run to GitHub[/dim]")
                    if pr_num:
                        api.create_pr_comment(
                            repo=repo,
                            pr_number=int(pr_num),
                            body="## ✅ AlwaysGreen: No failing tests to fix! 🎉\n\nAll tests are passing.",
                        )
                        if verbose:
                            console.print("[dim]✅ Posted PR comment to GitHub[/dim]")
                except Exception as e:
                    if verbose:
                        console.print(
                            f"[yellow]⚠️ GitHub reporting failed: {e}[/yellow]"
                        )
            return

        # Display failing tests summary table (up to first 10 failures)
        console.print(
            f"\n[bold red]Found {len(failing_tests)} failing test(s):[/bold red]"
        )
        table = Table(
            title="Failing Tests", show_header=True, header_style="bold magenta"
        )
        table.add_column("Test Name", style="cyan", no_wrap=False)
        table.add_column("Location", style="yellow")
        table.add_column("Error", style="red", no_wrap=False)
        for test in failing_tests[:10]:
            location = f"{test.file}:{test.line}" if hasattr(test, "file") else "N/A"
            location = f"{test.file}:{test.line}" if hasattr(test, "file") else "N/A"
            error_preview = (
                test.short_traceback.split("\n")[0]
                if hasattr(test, "short_traceback")
                else str(test)
            )
            if len(error_preview) > 60:
                error_preview = error_preview[:60] + "..."
            name = getattr(test, "name", str(test))
            table.add_row(name, location, error_preview)
        if len(failing_tests) > 10:
            table.add_row("...", f"... and {len(failing_tests)-10} more", "")
        console.print(table)
        console.print()

        # Prepare safety limits configuration from YAML (if provided)
        safety_conf = None
        if config_data:
            from nova.tools.safety_limits import SafetyConfig

            safety_conf_obj = SafetyConfig()
            custom_limits = False
            if config_data.max_changed_lines is not None:
                safety_conf_obj.safety_limits.max_lines_changed = config_data.max_changed_lines
                custom_limits = True
            if config_data.max_changed_files is not None:
                safety_conf_obj.safety_limits.max_files_modified = config_data.max_changed_files
                custom_limits = True
            if config_data.blocked_paths:
                for pattern in config_data.blocked_paths:
                    if pattern not in safety_conf_obj.denied_paths:
                        safety_conf_obj.denied_paths.append(pattern)
                custom_limits = True
            if custom_limits:
                safety_conf = safety_conf_obj

        # Either run the Deep Agent or the legacy agent loop
        # Determine which agent to use (precedence: CLI flag > env var > YAML config)
        use_legacy_env = os.getenv("NOVA_USE_LEGACY_AGENT", "").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        use_legacy_cfg = False
        agent_cfg_legacy = False
        if isinstance(config_data, dict) and config_data:
            try:
                use_legacy_cfg = bool(config_data.get("use_legacy_agent", False))
                agent_cfg_legacy = str(config_data.get("agent", "")).lower() in (
                    "legacy",
                    "llm",
                    "regular",
                )
            except Exception:
                use_legacy_cfg = False
                agent_cfg_legacy = False
        effective_legacy_agent = legacy_agent or use_legacy_env or use_legacy_cfg or agent_cfg_legacy

        success = False
        if not effective_legacy_agent:
            # === Deep Agent Path (default) ===
            console.print("\n[bold]Initializing Nova Deep Agent...[/bold]")
            from nova.agent.deep_agent import NovaDeepAgent

            deep_agent = NovaDeepAgent(
                state=state,
                telemetry=telemetry,
                git_manager=git_manager,
                verbose=verbose,
                safety_config=safety_conf,
            )
            console.print("[cyan]🤖 Running Deep Agent to fix failing tests...[/cyan]")
            failures_summary = runner.format_failures_table(failing_tests)
            error_details = "\n\n".join(
                test.short_traceback for test in failing_tests[:3]
            )
            code_snippets = ""
            success = deep_agent.run(
                failures_summary=failures_summary,
                error_details=error_details,
                code_snippets=code_snippets,
            )
            # Deep Agent handles iterations internally; no explicit loop needed here.
            if success:
                console.print(
                    "\n[green bold]✅ SUCCESS - All tests fixed![/green bold]"
                )
                state.final_status = "success"
            else:
                console.print(
                    "\n[red bold]❌ FAILED - Some tests could not be fixed.[/red bold]"
                )
                if state.final_status == "max_iters":
                    console.print(
                        f"[yellow]Reached maximum iterations ({state.max_iterations}) without full success.[/yellow]"
                    )
                elif state.final_status == "error":
                    console.print(
                        "[yellow]Agent encountered an error during execution.[/yellow]"
                    )
        else:
            console.print("[yellow]Ignoring legacy agent path; using regular agent.[/yellow]")
            success = state.total_failures == 0
            state.final_status = "success" if success else "failure"

        # Log completion status
        telemetry.log_event(
            "completion",
            {
                "status": state.final_status,
                "iterations": state.current_iteration,
                "total_patches": len(state.patches_applied),
                "final_failures": state.total_failures,
            },
        )
        # Print comprehensive exit summary
        if state and state.final_status:
            elapsed = (datetime.now() - state.start_time).total_seconds()
            print_exit_summary(state, state.final_status, elapsed_seconds=elapsed)

        telemetry.end_run(success=(state.final_status == "success"))

        # GitHub integration: post results to PR if in CI environment
        token = os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")
        pr_num = os.getenv("PR_NUMBER") or os.getenv("GITHUB_EVENT_NUMBER") or None
        if not pr_num:
            github_ref = os.getenv("GITHUB_REF")
            if github_ref and "pull/" in github_ref:
                match = re.search(r"pull/(\d+)/", github_ref)
                if match:
                    pr_num = match.group(1)
            if not pr_num:
                event_path = os.getenv("GITHUB_EVENT_PATH")
                if event_path and os.path.exists(event_path):
                    try:
                        with open(event_path, "r") as f:
                            event_data = json.load(f)
                        if "pull_request" in event_data:
                            pr_num = str(event_data["pull_request"]["number"])
                    except Exception:
                        pass
        if token and repo:
            try:
                from nova.github_integration import (
                    GitHubAPI,
                    RunMetrics,
                    ReportGenerator,
                )

                elapsed = (datetime.now() - state.start_time).total_seconds()
                # Count unique files changed across all applied patches
                files_changed = set()
                if state.patches_applied:
                    from nova.tools.safety_limits import SafetyLimits

                    safety = SafetyLimits()
                    for patch in state.patches_applied:
                        analysis = safety.analyze_patch(patch)
                        files_changed.update(
                            analysis.files_modified | analysis.files_added
                        )
                metrics = RunMetrics(
                    runtime_seconds=int(elapsed),
                    iterations=state.current_iteration,
                    files_changed=len(files_changed),
                    status="success" if success else (state.final_status or "failure"),
                    tests_fixed=(
                        len(state.failing_tests) - state.total_failures
                        if state.failing_tests
                        else 0
                    ),
                    tests_remaining=state.total_failures,
                    initial_failures=(
                        len(state.failing_tests) if state.failing_tests else 0
                    ),
                    final_failures=state.total_failures,
                    branch_name=branch_name,
                )
                api = GitHubAPI(token)
                generator = ReportGenerator()
                head_sha = git_manager._get_current_head() if git_manager else None
                if head_sha:
                    api.create_check_run(
                        repo=repo,
                        sha=head_sha,
                        name="CI-Auto-Rescue",
                        status="completed",
                        conclusion="success" if success else "failure",
                        title=f"CI-Auto-Rescue: {metrics.status.upper()}",
                        summary=generator.generate_check_summary(metrics),
                    )
                    if verbose:
                        console.print("[dim]✅ Posted check run to GitHub[/dim]")
                if pr_num:
                    existing_id = api.find_pr_comment(
                        repo, int(pr_num), "<!-- ci-auto-rescue-report -->"
                    )
                    comment_body = generator.generate_pr_comment(metrics)
                    if existing_id:
                        api.update_pr_comment(repo, existing_id, comment_body)
                        if verbose:
                            console.print("[dim]✅ Updated existing PR comment[/dim]")
                    else:
                        api.create_pr_comment(repo, int(pr_num), comment_body)
                        if verbose:
                            console.print("[dim]✅ Created new PR comment[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠️ GitHub reporting failed: {e}[/yellow]")
                if verbose:
                    import traceback

                    console.print(f"[dim]{traceback.format_exc()}[/dim]")

    except KeyboardInterrupt:
        # Handle Ctrl+C interruption
        if state:
            state.final_status = "interrupted"
            console.print("\n[yellow]Interrupted by user[/yellow]")
            if telemetry:
                telemetry.log_event("interrupted", {"reason": "keyboard_interrupt"})
            print_exit_summary(state, "interrupted")
        else:
            console.print("\n[yellow]Interrupted by user[/yellow]")
        success = False
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if state:
            state.final_status = "error"
            print_exit_summary(state, "error")
        if telemetry:
            telemetry.log_event("error", {"error": str(e)})
        success = False

    # Exit with appropriate code (0 if success, 1 if not)
    raise typer.Exit(0 if success else 1)


@app.command()
def eval(
    eval_file: Path = typer.Argument(
        ...,
        help="Path to evaluation YAML file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for results",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
):
    """
    Evaluate Nova on multiple repositories.
    """
    console.print("[green]AlwaysGreen Evaluation[/green] 🔬")
    console.print(f"Loading evaluation config from: {eval_file}")

    # Implementation placeholder
    console.print("[yellow]Evaluation mode not fully implemented yet[/yellow]")
    raise typer.Exit(0)


@app.command()
def validate_installation(
    base_url: str = typer.Option(
        "http://localhost:3000",
        "--url",
        "-u",
        help="Base URL where the GitHub App is running",
    )
):
    """
    Validate installation and test end-to-end functionality.
    This command performs comprehensive validation of the AlwaysGreen installation.

    Args:
        base_url: Base URL where the GitHub App is running (default: http://localhost:3000)
    """
    from rich.console import Console

    console = Console()

    console.print("[green]🔍 AlwaysGreen Installation Validation[/green]")
    console.print("=" * 50)

    try:
        # Get the health endpoint URL
        health_url = f"{base_url}/health/installation"

        console.print(f"[dim]Testing endpoint: {health_url}[/dim]")

        # Make the request with a timeout
        response = requests.get(health_url, timeout=30)

        if response.status_code == 200:
            result = response.json()

            # Display overall status
            status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}

            console.print(
                f"\n{status_emoji.get(result['status'], '❓')} Overall Status: {result['status'].upper()}"
            )
            console.print(
                f"[dim]Validation completed in {result['duration_ms']}ms[/dim]"
            )

            # Display installation validation
            console.print("\n[bold]📦 Installation Validation:[/bold]")
            install_status = result["installation"]["validation_status"]
            install_emoji = "✅" if install_status == "validated" else "❌"
            console.print(f"  {install_emoji} Status: {install_status}")
            if result["installation"]["error"]:
                console.print(f"  [red]Error: {result['installation']['error']}[/red]")
            console.print(
                f"  📊 Installations found: {result['installation']['installations_count']}"
            )

            # Display one-click path validation
            console.print("\n[bold]🚀 One-Click Path Validation:[/bold]")
            path_status = result["one_click_path"]["test_status"]
            path_emoji = "✅" if path_status == "validated" else "❌"
            console.print(f"  {path_emoji} Status: {path_status}")
            if result["one_click_path"]["error"]:
                console.print(
                    f"  [red]Error: {result['one_click_path']['error']}[/red]"
                )

            # Display end-to-end validation
            console.print("\n[bold]🔄 End-to-End Validation:[/bold]")
            e2e_status = result["end_to_end"]["test_status"]
            e2e_emoji = "✅" if e2e_status == "application_ready" else "❌"
            console.print(f"  {e2e_emoji} Status: {e2e_status}")
            if result["end_to_end"]["error"]:
                console.print(f"  [red]Error: {result['end_to_end']['error']}[/red]")

            # Display capabilities
            console.print("\n[bold]⚙️ Capabilities:[/bold]")
            capabilities = result["end_to_end"]["capabilities"]
            for capability, status in capabilities.items():
                cap_emoji = "✅" if status == "configured" else "❌"
                console.print(
                    f"  {cap_emoji} {capability.replace('_', ' ').title()}: {status}"
                )

            # Display environment
            console.print("\n[bold]🌍 Environment:[/bold]")
            env = result["environment"]
            for key, value in env.items():
                env_emoji = "✅" if value == "configured" else "❌"
                console.print(f"  {env_emoji} {key.replace('_', ' ').title()}: {value}")

            # Final recommendations
            console.print("\n[bold]📋 Recommendations:[/bold]")
            if result["status"] == "healthy":
                console.print(
                    "  ✅ Installation is fully validated and ready for production!"
                )
                console.print("  🎉 One-click path is working correctly")
                console.print("  🚀 End-to-end functionality is operational")
            elif result["status"] == "degraded":
                console.print(
                    "  ⚠️ Installation has some issues but is mostly functional"
                )
                console.print(
                    "  📝 Check the errors above for specific issues to resolve"
                )
            else:
                console.print(
                    "  ❌ Installation has critical issues that need attention"
                )
                console.print(
                    "  🔧 Please check the errors above and fix configuration issues"
                )

        else:
            console.print(
                f"[red]❌ Health check failed with status code: {response.status_code}[/red]"
            )
            console.print(f"[dim]Response: {response.text}[/dim]")

    except requests.exceptions.RequestException as e:
        console.print("[red]❌ Could not connect to health endpoint[/red]")
        console.print(f"[dim]Error: {e}[/dim]")
        console.print("\n[yellow]💡 Make sure the GitHub App is running:[/yellow]")
        console.print("  1. Start the app: npm start")
        console.print("  2. Or use: npm run dev")
        console.print("  3. Check that it's running on http://localhost:3000")

    except Exception as e:
        console.print("[red]❌ Unexpected error during validation[/red]")
        console.print(f"[dim]Error: {e}[/dim]")


@app.command()
def config():
    """
    Display current Nova configuration and verify setup.
    """

    console.print("[green]AlwaysGreen Configuration[/green] ⚙️")
    console.print()

    try:
        settings = get_settings()

        # Check Python version
        import sys

        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        console.print(f"[cyan]Python Version:[/cyan] {py_version}")

        # Check API keys
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

        if has_openai or has_anthropic:
            console.print("[cyan]API Key:[/cyan] [green]✅ Configured[/green]")
            if has_openai:
                console.print("  • OpenAI: [green]Found[/green]")
            if has_anthropic:
                console.print("  • Anthropic: [green]Found[/green]")
        else:
            console.print("[cyan]API Key:[/cyan] [red]❌ Not configured[/red]")
            console.print(
                "[yellow]Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env[/yellow]"
            )

        # Display settings
        console.print(f"[cyan]Default Model:[/cyan] {settings.default_llm_model}")
        console.print(
            f"[cyan]Default Iterations:[/cyan] {settings.default_max_iterations}"
        )
        console.print(
            f"[cyan]Default Timeout:[/cyan] {settings.default_timeout_seconds}s"
        )

        # Check Docker availability
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                console.print("[cyan]Docker:[/cyan] [green]✅ Available[/green]")
            else:
                console.print(
                    "[cyan]Docker:[/cyan] [yellow]⚠️ Not available (sandboxing disabled)[/yellow]"
                )
        except Exception:
            console.print(
                "[cyan]Docker:[/cyan] [yellow]⚠️ Not available (sandboxing disabled)[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def doctor(
    config_path: str = typer.Option(
        ".github/nova.yml",
        "--config",
        help="Path to nova.yml configuration file"
    ),
    ci_cmd: Optional[str] = typer.Option(
        None,
        "--ci-cmd",
        help="Optional: run `nova fix --ci \"<cmd>\"` (may modify repository)"
    ),
    smoke_test: bool = typer.Option(
        False,
        "--smoke",
        help="Enable smoke run (disabled by default for safety)"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format"
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Treat warnings as errors for exit status"
    )
):
    """
    Run comprehensive health checks for AlwaysGreen installation.
    
    This command verifies:
    - Python version compatibility
    - API key configuration
    - CLI availability and functionality
    - Git repository context
    - Configuration file structure
    - Optional smoke test (with explicit opt-in)
    """
    from nova.tools.doctor import NovaDoctor
    
    doctor_instance = NovaDoctor(
        config_path=config_path,
        ci_command=ci_cmd,
        enable_smoke_run=smoke_test,
        strict_warnings=strict,
    )
    
    result = doctor_instance.run()
    
    if json_output:
        console.print(json.dumps(result, indent=2))
    else:
        _print_doctor_results(result)
    
    # Exit with appropriate code
    raise typer.Exit(0 if result["ok"] else 1)


def _print_doctor_results(result: dict) -> None:
    """Pretty print doctor results."""
    ok = result["ok"]
    symbol = "✅" if ok else "❌"
    console.print(f"{symbol} [bold]AlwaysGreen Doctor[/bold] — overall {'OK' if ok else 'needs attention'}")
    console.print()
    
    for check in result["checks"]:
        status = check["status"].upper()
        name = check["name"]
        
        # Color code the status
        if status == "OK":
            status_colored = f"[green]{status}[/green]"
        elif status == "WARN":
            status_colored = f"[yellow]{status}[/yellow]"
        else:
            status_colored = f"[red]{status}[/red]"
        
        console.print(f"[{status_colored}] {name}")
        
        if check.get("detail"):
            console.print(f"  • {check['detail']}")
        if not check["ok"] and check.get("fix"):
            console.print(f"  → [dim]Fix: {check['fix']}[/dim]")
        console.print()


@app.command("help")
def help_cmd(ctx: typer.Context):
    """
    Show help information (alias for --help).
    """
    console.print(ctx.parent.get_help() if ctx.parent else app.get_help(ctx))


@app.command()
def version():
    """
    Show AlwaysGreen version.
    """
    from nova import __version__

    console.print(f"[green]AlwaysGreen[/green] v{__version__}")


@app.command()
def run(
    repo_path: Path = typer.Argument(
        Path("."), exists=True, file_okay=False, dir_okay=True, resolve_path=True
    ),
    ci: Optional[str] = typer.Option(
        None,
        "--ci",
        help="Custom test command to run (e.g., 'npm test -- --ci', 'python -m unittest -q')",
    ),
    junit_report: Optional[Path] = typer.Option(
        None,
        "--junit-report",
        help="Path to JUnit XML report produced by the test command",
        exists=False,
        file_okay=True,
        dir_okay=False,
        resolve_path=False,
    ),
    max_iters: Optional[int] = typer.Option(None, "--max-iters", "-i"),
    timeout: Optional[int] = typer.Option(None, "--timeout", "-t"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", exists=True),
    legacy_agent: bool = typer.Option(False, "--legacy-agent"),
):
    """
    Alias for `fix` with support for generic test command.
    """
    ctx = typer.get_current_context()
    args = [str(repo_path)]
    if max_iters is not None:
        args += ["--max-iters", str(max_iters)]
    if timeout is not None:
        args += ["--timeout", str(timeout)]
    if verbose:
        args += ["--verbose"]
    if config_file is not None:
        args += ["--config", str(config_file)]
    if legacy_agent:
        args += ["--legacy-agent"]
    if ci:
        args += ["--ci", ci]
    if junit_report is not None:
        args += ["--junit-report", str(junit_report)]
    ctx.invoke(fix, repo_path=repo_path, max_iters=max_iters, timeout=timeout, verbose=verbose,
               config_file=config_file, legacy_agent=legacy_agent, ci_cmd=ci, junit_report=junit_report)

if __name__ == "__main__":
    app()
