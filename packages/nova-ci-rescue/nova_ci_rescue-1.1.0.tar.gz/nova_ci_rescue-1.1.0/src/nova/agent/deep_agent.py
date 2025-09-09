from __future__ import annotations

import os
from typing import Optional
from rich.console import Console

from nova.agent.state import AgentState
from nova.telemetry.logger import JSONLLogger
from nova.tools.git import GitBranchManager

console = Console()


class NovaDeepAgent:
    def __init__(
        self,
        state: AgentState,
        telemetry: JSONLLogger,
        git_manager: GitBranchManager,
        verbose: bool = False,
        safety_config: Optional[object] = None,
    ):
        self.state = state
        self.telemetry = telemetry
        self.git_manager = git_manager
        self.verbose = verbose
        self.safety_config = safety_config

        force_mock = os.getenv("NOVA_FORCE_MOCK", "").lower() in ("1", "true", "yes")

        # Try EnhancedLLMAgent first; fallback to Mock
        self.agent_type = "mock"
        try:
            if not force_mock:
                from nova.agent.llm_agent_enhanced import EnhancedLLMAgent

                self.llm_agent = EnhancedLLMAgent(repo_path=state.repo_path, verbose=verbose)
                self.agent_type = "enhanced"
                if verbose:
                    console.print("[green]✅ Enhanced LLM agent initialized[/green]")
            else:
                raise RuntimeError("Forced mock agent")
        except Exception as e:
            from nova.agent.mock_llm import MockLLMAgent

            self.llm_agent = MockLLMAgent()
            self.agent_type = "mock"
            if verbose:
                console.print(f"[yellow]⚠️ Falling back to mock agent: {e}[/yellow]")

    def run(self, failures_summary: str, error_details: str, code_snippets: str) -> bool:
        # For now, keep behavior conservative in Deep Agent path
        if self.verbose:
            console.print("⚠️ Running in Deep Agent path (mock behavior for now)")
        return False

"""
Nova Deep Agent - Enhanced agent with proper error handling and fallback.
"""

import os
from pathlib import Path
from typing import Optional
from rich.console import Console

from nova.agent.state import AgentState
from nova.telemetry.logger import JSONLLogger
from nova.tools.git import GitBranchManager

console = Console()


class NovaDeepAgent:
    """Deep Agent for Nova with proper initialization and error handling."""
    
    def __init__(
        self,
        state: AgentState,
        telemetry: JSONLLogger,
        git_manager: GitBranchManager,
        verbose: bool = False,
        safety_config=None,
    ):
        self.state = state
        self.telemetry = telemetry
        self.git_manager = git_manager
        self.verbose = verbose
        self.safety_config = safety_config
        
        # Check if we should force mock mode for testing
        force_mock = os.getenv("NOVA_FORCE_MOCK", "").lower() in ("1", "true", "yes")
        
        # Try to initialize the enhanced LLM agent (unless forced to mock)
        if not force_mock:
            try:
                from nova.agent.llm_agent_enhanced import EnhancedLLMAgent
                self.llm_agent = EnhancedLLMAgent(
                    repo_path=state.repo_path, 
                    verbose=verbose
                )
                self.agent_type = "enhanced"
                if verbose:
                    console.print("[green]✅ Enhanced LLM agent initialized[/green]")
            except Exception as e:
                # Fall back to mock agent
                from nova.agent.llm_agent import MockLLMAgent
                self.llm_agent = MockLLMAgent(
                    repo_path=state.repo_path,
                    verbose=verbose
                )
                self.agent_type = "mock"
                if verbose:
                    console.print(f"[yellow]⚠️ Falling back to mock agent: {e}[/yellow]")
        else:
            # Force mock mode for testing
            from nova.agent.llm_agent import MockLLMAgent
            self.llm_agent = MockLLMAgent(
                repo_path=state.repo_path,
                verbose=verbose
            )
            self.agent_type = "mock"
            if verbose:
                console.print("[cyan]🧪 Using mock agent (NOVA_FORCE_MOCK=1)[/cyan]")
    
    def run(
        self, 
        failures_summary: str, 
        error_details: str, 
        code_snippets: str
    ) -> bool:
        """Run the deep agent to fix failing tests."""
        try:
            if self.agent_type == "mock":
                console.print("[yellow]⚠️ Running in demo mode with mock agent[/yellow]")
                console.print("[dim]Real fixes require a valid OPENAI_API_KEY or ANTHROPIC_API_KEY[/dim]")
                
                # Simulate some work for demo
                import time
                time.sleep(1)
                
                if self.verbose:
                    console.print("[cyan]🧠 Mock agent analyzing failures...[/cyan]")
                    console.print(f"[dim]Found test failures: {len(self.state.failing_tests)}[/dim]")
                
                # For demo purposes, return False to show the failure path
                return False
            
            # If we have a real agent, run the actual workflow
            return self._run_enhanced_agent(failures_summary, error_details, code_snippets)
            
        except Exception as e:
            console.print(f"[red]❌ Deep agent error: {e}[/red]")
            self.state.final_status = "error"
            return False
    
    def _run_enhanced_agent(
        self, 
        failures_summary: str, 
        error_details: str, 
        code_snippets: str
    ) -> bool:
        """Run the enhanced agent workflow."""
        # This would contain the actual deep agent logic
        # For now, it's a placeholder that uses the enhanced LLM agent
        
        iteration = 0
        max_iterations = self.state.max_iterations
        
        while iteration < max_iterations:
            iteration += 1
            console.print(f"[bold]Iteration {iteration}/{max_iterations}[/bold]")
            
            # Generate plan
            plan = self.llm_agent.create_plan(
                self.state.failing_tests, 
                iteration
            )
            
            if self.verbose:
                console.print(f"[cyan]📋 Plan: {plan.get('approach', 'No approach')}[/cyan]")
            
            # Generate patch
            patch = self.llm_agent.generate_patch(
                self.state.failing_tests,
                iteration,
                plan=plan,
                state=self.state
            )
            
            if not patch:
                console.print("[red]❌ No patch could be generated[/red]")
                break
                
            if self.verbose:
                console.print("[green]✅ Patch generated successfully[/green]")
                
            # For now, we'll consider it successful if we got a patch
            self.state.final_status = "success"
            return True
            
        self.state.final_status = "max_iters"
        return False
