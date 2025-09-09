import functools
import json
import os
import subprocess
import time
import tracemalloc
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import yaml

from adaptiq.agents.crew_ai import (
    CrewConfig,
    CrewLogger,
    CrewLogParser,
    CrewPromptParser,
)
from adaptiq.core.abstract.integrations import BaseInstrumental
from adaptiq.core.pipelines import AdaptiqRun


class CrewInstrumental(BaseInstrumental):
    """
    A comprehensive instrumentation class for tracking and monitoring function execution,
    crew performance, and token usage with AdaptiQ pipeline integration.
    """

    def __init__(self):
        """Initialize the Instrumental instance with fresh tracking data."""
        self._token_tracking: Dict[str, Any] = {}
        self._crew_counter: int = 0
        self.logger = CrewLogger()
        self._agent_metrics: List[Dict[str, Any]] = []
        self.current_dir = os.getcwd()
        self.logs_path = "./log.json"

    def display_agent_last_exec(self):
        crew_metrics = None
        try:
            crew_metrics = self.get_agent_metrics()

            print("[INSTRUMENT] === CREW METRICS CAPTURED ===")
            print(f"[INSTRUMENT] Total executions tracked: {len(crew_metrics)}")

            # Print summary of crew metrics for testing
            if crew_metrics:
                total_tokens = sum(
                    metric.get("total_tokens", 0) for metric in crew_metrics
                )
                total_time = sum(
                    metric.get("execution_time_seconds", 0) for metric in crew_metrics
                )
                print(
                    f"[INSTRUMENT] Total tokens across all executions: {total_tokens:,}"
                )
                print(f"[INSTRUMENT] Total execution time: {total_time:.2f}s")

                # Show last execution details
                if crew_metrics:
                    last_metric = crew_metrics[-1]
                    print(
                        f"[INSTRUMENT] Last execution: {last_metric.get('execution_time_seconds', 0):.2f}s, "
                        f"{last_metric.get('total_tokens', 0):,} tokens"
                    )

            print("[INSTRUMENT] === END CREW METRICS ===")

        except Exception as e:
            print(f"[INSTRUMENT] Warning: Error capturing crew metrics: {e}")
            crew_metrics = None

    def run(
        self,
        config_path: Optional[str] = None,
        enable_pipeline: bool = True,
        prompt_auto_update: bool = False,
        feedback: Optional[str] = None,
    ):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):

                base_config = CrewConfig(config_path=config_path, preload=True)
                base_log_parser = CrewLogParser(
                    logs_path=self.logs_path,
                    output_path=os.path.join(self.current_dir, "results"),
                )
                base_prompt_parser = CrewPromptParser(
                    config_data=base_config.get_config(),
                    task=base_config.get_prompt(get_newest=True),
                    tools=base_config.get_tools(),
                )

                adaptiq_run = AdaptiqRun(
                    base_config=base_config,
                    base_log_parser=base_log_parser,
                    base_prompt_parser=base_prompt_parser,
                    feedback=feedback,
                    current_dir=self.current_dir,
                    template="crew-ai",
                    prompt_auto_update=prompt_auto_update,
                    allow_pipeline=enable_pipeline,
                )

                result = adaptiq_run.init_run(func=func, *args, **kwargs)

                adaptiq_run.run(agent_metrics=self._agent_metrics)

                return {"original_result": result, "crew_metrics": self._agent_metrics}

            return wrapper

        return decorator

    def agent_logger(self, func: Callable) -> Callable:
        """
        Decorator to automatically add step_callback logging to CrewAI agents.

        This decorator modifies the agent creation to include step_callback
        that logs agent steps/thoughts after each execution step.

        Args:
            func (callable): The function that creates and returns an Agent.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # Create a step callback function that logs thoughts
            def step_callback(step_output):
                """Callback to log agent steps/thoughts"""

                self.logger.log_thoughts(step_output)

            # Execute the original function to get the Agent
            agent = func(*args, **kwargs)

            # Add the step callback to the agent
            agent.step_callback = step_callback

            return agent

        return wrapper

    def task_logger(self, func: Callable) -> Callable:
        """
        Decorator to automatically add callback logging to CrewAI tasks.

        This decorator modifies the task creation to include callback
        that logs task information after task completion.

        Args:
            func (callable): The function that creates and returns a Task.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # Create a task callback function that logs task completion
            def task_callback(task_output):
                """Callback to log task completion"""
                self.logger.log_task(task_output)

            # Execute the original function to get the Task
            task = func(*args, **kwargs)

            # Add the callback to the task (CrewAI uses 'callback' not 'task_callback')
            task.callback = task_callback

            return task

        return wrapper

    def crew_logger(self, log_to_console: bool = True) -> Callable:
        """
        Decorator to track time, tokens, memory usage, model information, and execution count for CrewAI crew execution.

        This decorator can be applied to the crew kickoff method or any method that
        executes a crew and returns a result with token_usage attribute.

        Args:
            log_to_console (bool): Whether to print metrics to console

        Usage:
            @instrumental.crew_logger(log_to_console=True)
            def run_crew(self):
                return self.crew().kickoff(inputs={"topic": "AI"})
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Increment the crew counter
                self._crew_counter += 1
                current_execution = self._crew_counter

                # Start memory tracking
                tracemalloc.start()

                # Record start time
                start_time = time.time()
                start_timestamp = datetime.now()

                # Execute the original function
                result = func(*args, **kwargs)

                # Record end time
                end_time = time.time()
                end_timestamp = datetime.now()
                execution_time = end_time - start_time

                # Get memory usage
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                # Extract token usage information
                token_usage = getattr(result, "token_usage", None)

                # Extract model information from crew agents
                models_used = []

                # Store the crew instance in the result for access by the decorator
                if hasattr(result, "_crew_instance"):
                    crew_instance = result._crew_instance
                    if hasattr(crew_instance, "agents"):
                        for agent in crew_instance.agents:
                            if hasattr(agent, "llm") and hasattr(agent.llm, "model"):
                                models_used.append(
                                    {
                                        "agent_role": getattr(agent, "role", "Unknown"),
                                        "model": agent.llm.model,
                                    }
                                )

                # Initialize metrics
                metrics = {
                    "execution_count": current_execution,
                    "total_executions": self._crew_counter,
                    "start_timestamp": start_timestamp.isoformat(),
                    "end_timestamp": end_timestamp.isoformat(),
                    "execution_time_seconds": round(execution_time, 2),
                    "execution_time_minutes": round(execution_time / 60, 2),
                    "current_memory_mb": round(current / 1024 / 1024, 2),
                    "peak_memory_mb": round(peak / 1024 / 1024, 2),
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cached_prompt_tokens": 0,
                    "successful_requests": 0,
                    "models_used": models_used,
                    "function_name": func.__name__,
                }

                # Process token usage if available
                if token_usage:
                    metrics["total_tokens"] = getattr(token_usage, "total_tokens", 0)
                    metrics["prompt_tokens"] = getattr(token_usage, "prompt_tokens", 0)
                    metrics["completion_tokens"] = getattr(
                        token_usage, "completion_tokens", 0
                    )
                    metrics["cached_prompt_tokens"] = getattr(
                        token_usage, "cached_prompt_tokens", 0
                    )
                    metrics["successful_requests"] = getattr(
                        token_usage, "successful_requests", 0
                    )

                # Store metrics in instance variable
                self._agent_metrics.append(metrics)

                # Log to console if requested
                if log_to_console:
                    print("\n" + "=" * 50)
                    print("🚀 CREW PERFORMANCE METRICS")
                    print("=" * 50)
                    print(
                        f"🔢 Execution #{current_execution} (Total: {self._crew_counter})"
                    )
                    print(
                        f"⏱️ Execution Time: {metrics['execution_time_seconds']}s ({metrics['execution_time_minutes']} min)"
                    )
                    print(f"🧠 Current Memory: {metrics['current_memory_mb']} MB")
                    print(f"📊 Peak Memory: {metrics['peak_memory_mb']} MB")
                    print(f"🔢 Total Tokens: {metrics['total_tokens']:,}")
                    print(f"📝 Prompt Tokens: {metrics['prompt_tokens']:,}")
                    print(
                        f"💾 Cached Prompt Tokens: {metrics['cached_prompt_tokens']:,}"
                    )
                    print(f"✅ Completion Tokens: {metrics['completion_tokens']:,}")
                    print(f"🔄 Successful Requests: {metrics['successful_requests']}")

                    # Display model information
                    if models_used:
                        print("🤖 Models Used:")
                        for model_info in models_used:
                            print(
                                f"   • {model_info['agent_role']}: {model_info['model']}"
                            )
                    else:
                        print("🤖 Models Used: Unable to detect")

                    print("=" * 50 + "\n")

                return result

            return wrapper

        return decorator

    def get_token_stats(self, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Get token statistics for a specific mode or all modes.

        Args:
            mode: Optional mode to get stats for. If None, returns all modes with summary.

        Returns:
            Dictionary containing token statistics
        """
        if mode:
            return self._token_tracking.get(mode, {})
        else:
            # Return all modes with a summary
            result = self._token_tracking.copy()

            # Add summary statistics
            summary = {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "total_calls": 0,
            }

            modes_summary = {}
            for mode_name, data in self._token_tracking.items():
                summary["total_input_tokens"] += data["total_input_tokens"]
                summary["total_output_tokens"] += data["total_output_tokens"]
                summary["total_tokens"] += data["total_tokens"]
                summary["total_calls"] += data["total_calls"]

                # Create per-mode summary
                modes_summary[mode_name] = {
                    "input_tokens": data["total_input_tokens"],
                    "output_tokens": data["total_output_tokens"],
                    "total_tokens": data["total_tokens"],
                    "calls": data["total_calls"],
                }

            result["_summary"] = summary
            result["_modes_summary"] = modes_summary

            return result

    def reset_token_tracking(self, mode: Optional[str] = None) -> None:
        """
        Reset token tracking data.

        Args:
            mode: Optional mode to reset. If None, resets all tracking data.
        """
        if mode:
            if mode in self._token_tracking:
                del self._token_tracking[mode]
                print(f"Reset tracking data for mode: {mode}")
            else:
                print(f"No tracking data found for mode: {mode}")
        else:
            self._token_tracking = {}
            print("Reset all tracking data")

    def get_agent_metrics(self) -> List[Dict[str, Any]]:
        """
        Get all stored crew metrics.

        Returns:
            List[Dict[str, Any]]: List of all metrics collected from crew executions
        """
        return (
            self._agent_metrics.copy()
        )  # Return a copy to prevent external modification

    def reset_crew_metrics(self) -> None:
        """
        Reset all stored crew metrics and execution counter.
        """
        self._crew_counter = 0
        self._agent_metrics = []
        print("🔄 Crew metrics and counter have been reset.")

    def update_token_tracking(
        self, mode: str, input_tokens: int, output_tokens: int
    ) -> None:
        """
        Update token tracking for a specific mode.

        Args:
            mode: The mode identifier
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        if mode not in self._token_tracking:
            self._token_tracking[mode] = {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "total_calls": 0,
            }

        self._token_tracking[mode]["total_input_tokens"] += input_tokens
        self._token_tracking[mode]["total_output_tokens"] += output_tokens
        self._token_tracking[mode]["total_tokens"] += input_tokens + output_tokens
        self._token_tracking[mode]["total_calls"] += 1


# Convenience functions for backward compatibility
def create_crew_instrumental() -> CrewInstrumental:
    """Create a new Instrumental instance."""
    return CrewInstrumental()
