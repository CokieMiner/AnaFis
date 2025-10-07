"""Initialization manager for AnaFis startup tasks."""

import logging
from typing import Any, Callable, List


class InitializationManager:
    """Manages the initialization process with progress tracking"""

    def __init__(self, language: str):
        self.language = language
        self.tasks: List[tuple[str, Callable[[], Any]]] = []
        self.current_task = 0
        self.total_tasks = 0

    def add_task(self, name: str, func: Callable[[], Any]) -> None:
        """Add a new initialization task with a name and function."""
        self.tasks.append((name, func))
        self.total_tasks = len(self.tasks)

    def execute_tasks(self, progress_callback: Callable[[int, str], None]) -> None:
        """Execute all initialization tasks, reporting progress via the callback."""
        for i, (task_name, task_func) in enumerate(self.tasks):
            try:
                progress_callback(int((i / self.total_tasks) * 100), task_name)
                task_func()
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Justification: Continue initialization even if a single task fails.
                logging.error("Error in initialization task '%s': %s", task_name, e)
        progress_callback(
            100, self.language
        )  # The final message should be set by the caller
