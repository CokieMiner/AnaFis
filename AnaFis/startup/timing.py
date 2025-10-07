"""Timing and startup metrics tracking for AnaFis."""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union


class TimingTracker:
    """Tracks application startup timing"""

    def __init__(self):
        self.startup_start_time = time.time()
        self.splash_start_time: Optional[float] = None
        self.splash_end_time: Optional[float] = None
        self.app_ready_time: Optional[float] = None

    def mark_splash_start(self) -> None:
        """Mark the time when the splash screen is shown."""
        self.splash_start_time = time.time()
        logging.debug("Splash screen start time recorded")

    def mark_splash_end(self) -> None:
        """Mark the time when the splash screen is closed."""
        self.splash_end_time = time.time()
        logging.debug("Splash screen end time recorded")

    def mark_app_ready(self) -> None:
        """Mark the time when the application is fully ready."""
        self.app_ready_time = time.time()
        logging.debug("Application ready time recorded")
        self.log_timing_info()
        self.track_startup_metrics()

    def log_timing_info(self) -> None:
        """Log splash, startup, and post-splash timing info to the logger and console."""
        if self.splash_start_time and self.splash_end_time:
            splash_duration = self.splash_end_time - self.splash_start_time
            logging.info("Splash screen displayed for: %.3f seconds", splash_duration)

        if self.app_ready_time:
            total_startup_time = self.app_ready_time - self.startup_start_time
            logging.info(
                "Total application startup time: %.3f seconds", total_startup_time
            )

            if self.splash_end_time:
                post_splash_time = self.app_ready_time - self.splash_end_time
                logging.info(
                    "Post-splash initialization time: %.3f seconds", post_splash_time
                )

        if self.splash_start_time and self.splash_end_time and self.app_ready_time:
            splash_duration = self.splash_end_time - self.splash_start_time
            total_time = self.app_ready_time - self.startup_start_time
            print("\n=== AnaFis Startup Timing ===")
            print(f"Splash screen duration: {splash_duration:.3f}s")
            print(f"Total startup time: {total_time:.3f}s")
            print("================================\n")

    def track_startup_metrics(self) -> None:
        """Track and persist startup metrics for later analysis."""
        try:
            total_startup_time = time.time() - self.startup_start_time
            splash_duration = (
                (self.splash_end_time - self.splash_start_time)
                if self.splash_start_time and self.splash_end_time
                else 0
            )
            app_init_time = (
                (self.app_ready_time - self.splash_end_time)
                if self.splash_end_time and self.app_ready_time
                else 0
            )
            metrics: Dict[str, Union[str, float, int]] = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_startup_time": round(total_startup_time, 3),
                "splash_duration": round(splash_duration, 3),
                "app_initialization_time": round(app_init_time, 3),
                "python_version": sys.version.split()[0],
                "platform": os.name,
            }
            logging.info(
                "Startup metrics: Total=%.3fs, Splash=%.3fs, Init=%.3fs",
                metrics["total_startup_time"],
                metrics["splash_duration"],
                metrics["app_initialization_time"],
            )
            try:
                if os.name == "nt":
                    metrics_dir = (
                        Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
                        / "AnaFis"
                        / "metrics"
                    )
                else:
                    metrics_dir = Path.home() / ".config" / "anafis" / "metrics"
                metrics_dir.mkdir(parents=True, exist_ok=True)
                metrics_file = metrics_dir / "startup_metrics.jsonl"
                with open(metrics_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(metrics) + "\n")
                if metrics_file.exists():
                    with open(metrics_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    if len(lines) > 100:
                        with open(metrics_file, "w", encoding="utf-8") as f:
                            f.writelines(lines[-100:])
            except (OSError, PermissionError) as e:
                logging.debug("Could not save startup metrics: %s", e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Justification: Metrics tracking should never crash the app
            logging.debug("Error tracking startup metrics: %s", e)


timing_tracker = TimingTracker()


def get_startup_metrics_history(
    limit: int = 10,
) -> List[Dict[str, Union[str, float, int]]]:
    """Return the most recent startup metrics as a list of dicts."""
    try:
        if os.name == "nt":
            metrics_dir = (
                Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
                / "AnaFis"
                / "metrics"
            )
        else:
            metrics_dir = Path.home() / ".config" / "anafis" / "metrics"
        metrics_file = metrics_dir / "startup_metrics.jsonl"
        if not metrics_file.exists():
            return []
        with open(metrics_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        metrics_list: List[Dict[str, Union[str, float, int]]] = []
        for line in recent_lines:
            try:
                metric: Dict[str, Union[str, float, int]] = json.loads(line.strip())
                metrics_list.append(metric)
            except json.JSONDecodeError:
                continue
        return metrics_list
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Justification: Metrics history reading should never crash the app
        logging.debug("Error reading startup metrics: %s", e)
        return []


def analyze_startup_performance() -> Dict[str, Union[str, int, float]]:
    """Analyze and summarize recent startup performance metrics."""
    metrics_history: List[Dict[str, Union[str, float, int]]] = (
        get_startup_metrics_history(50)
    )
    if not metrics_history:
        return {"status": "no_data", "message": "No startup metrics available"}
    total_times: List[float] = [
        float(m["total_startup_time"])
        for m in metrics_history
        if isinstance(m.get("total_startup_time"), (int, float, str))
        and str(m.get("total_startup_time")).replace(".", "", 1).isdigit()
    ]
    splash_times: List[float] = [
        float(m["splash_duration"])
        for m in metrics_history
        if isinstance(m.get("splash_duration"), (int, float, str))
        and str(m.get("splash_duration")).replace(".", "", 1).isdigit()
    ]
    init_times: List[float] = [
        float(m["app_initialization_time"])
        for m in metrics_history
        if isinstance(m.get("app_initialization_time"), (int, float, str))
        and str(m.get("app_initialization_time")).replace(".", "", 1).isdigit()
    ]
    analysis: Dict[str, Union[str, int, float]] = {
        "status": "success",
        "sample_size": len(metrics_history),
        "average_startup_time": (
            round(sum(total_times) / len(total_times), 3) if total_times else 0
        ),
        "average_splash_time": (
            round(sum(splash_times) / len(splash_times), 3) if splash_times else 0
        ),
        "average_init_time": (
            round(sum(init_times) / len(init_times), 3) if init_times else 0
        ),
        "latest_startup_time": total_times[-1] if total_times else 0,
        "fastest_startup": min(total_times) if total_times else 0,
        "slowest_startup": max(total_times) if total_times else 0,
    }
    if len(total_times) >= 20:
        recent_avg = sum(total_times[-10:]) / 10
        previous_avg = sum(total_times[-20:-10]) / 10
        trend = round(((recent_avg - previous_avg) / previous_avg) * 100, 1)
        analysis["performance_trend"] = f"{'+' if trend > 0 else ''}{trend}%"
    else:
        analysis["performance_trend"] = "insufficient_data"
    return analysis
