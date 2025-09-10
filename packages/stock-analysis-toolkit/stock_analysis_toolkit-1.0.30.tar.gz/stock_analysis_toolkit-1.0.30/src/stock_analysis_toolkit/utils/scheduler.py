"""
Scheduler Module

This module provides functionality to schedule stock analysis tasks.
"""

import time
import logging
import schedule
import threading
from datetime import datetime, time as dt_time, timedelta
from typing import Callable, Dict, Any, Optional
from pathlib import Path

scheduler_logger = logging.getLogger(__name__)

class AnalysisScheduler:
    """Class for scheduling stock analysis tasks."""

    def __init__(
        self, analysis_callback: Callable, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the scheduler.

        Args:
            analysis_callback: Function to call when analysis is triggered
            config: Configuration dictionary with scheduling options
        """
        self.analysis_callback = analysis_callback
        self.config = config or {}
        self.schedule = schedule.Scheduler()
        self.scheduler_thread = None
        self.running = False

        # Default configuration
        self.default_config = {
            "daily_time": "09:30",  # Default to market open time
            "timezone": "Asia/Kolkata",
            "weekdays_only": True,
            "run_on_start": False,
        }

        # Update with user config
        self.default_config.update(self.config)

    def _get_next_run_time(self) -> datetime:
        """Calculate the next run time based on the configuration."""
        now = datetime.now()
        target_time = dt_time(*map(int, self.default_config["daily_time"].split(":")))

        # If we're past the target time today, schedule for tomorrow
        if now.time() > target_time:
            next_run = datetime.combine(now.date() + timedelta(days=1), target_time)
        else:
            next_run = datetime.combine(now.date(), target_time)

        # Adjust for weekdays if needed
        if self.default_config["weekdays_only"]:
            # 5 = Saturday, 6 = Sunday
            while next_run.weekday() >= 5:
                next_run += timedelta(days=1)

        return next_run

    def _run_analysis(self):
        """Wrapper function to run the analysis and handle errors."""
        try:
            logger.info("Running scheduled analysis...")
            self.analysis_callback()
            logger.info("Scheduled analysis completed successfully")
        except Exception as e:
            logger.error(f"Error during scheduled analysis: {e}")

    def _scheduler_loop(self):
        """Run the scheduler loop in a separate thread."""
        logger.info("Starting scheduler loop")

        # Run immediately on start if configured
        if self.default_config.get("run_on_start", False):
            self._run_analysis()

        # Schedule the job
        schedule_time = self.default_config["daily_time"]

        if self.default_config["weekdays_only"]:
            self.schedule.every().monday.at(schedule_time).do(self._run_analysis)
            self.schedule.every().tuesday.at(schedule_time).do(self._run_analysis)
            self.schedule.every().wednesday.at(schedule_time).do(self._run_analysis)
            self.schedule.every().thursday.at(schedule_time).do(self._run_analysis)
            self.schedule.every().friday.at(schedule_time).do(self._run_analysis)
        else:
            self.schedule.every().day.at(schedule_time).do(self._run_analysis)

        logger.info(f"Next analysis scheduled for: {self._get_next_run_time()}")

        # Run the scheduler loop
        self.running = True
        while self.running:
            self.schedule.run_pending()
            time.sleep(60)  # Check every minute

    def start(self):
        """Start the scheduler in a separate thread."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Scheduler is already running")
            return

        logger.info("Starting scheduler...")
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True
        )
        self.scheduler_thread.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler...")
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def run_once(self):
        """Run the analysis once immediately."""
        self._run_analysis()

    def get_next_run(self) -> Optional[datetime]:
        """Get the next scheduled run time."""
        if not self.schedule.jobs:
            return None

        # Get the next run time from the first job
        job = next(iter(self.schedule.jobs), None)
        if job:
            return job.next_run
        return None


def schedule_analysis(
    analysis_callback: Callable, config: Optional[Dict[str, Any]] = None
) -> AnalysisScheduler:
    """
    Create and start a scheduler for stock analysis.

    Args:
        analysis_callback: Function to call when analysis is triggered
        config: Configuration dictionary with scheduling options
            - daily_time: Time to run analysis (format: 'HH:MM')
            - timezone: Timezone for scheduling
                (default: 'Asia/Kolkata')
            - weekdays_only: Whether to run only on weekdays
                (default: True)
            - run_on_start: Whether to run analysis immediately on start
                (default: False)

    Returns:
        AnalysisScheduler instance
    """
    scheduler = AnalysisScheduler(analysis_callback, config)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    # Example usage
    def test_analysis():
        print(f"Analysis run at {datetime.now()}")

    # Configure scheduler to run every minute for testing
    config = {
        "daily_time": (datetime.now() + timedelta(minutes=1)).strftime("%H:%M"),
        "weekdays_only": False,
        "run_on_start": True,
    }

    print("Starting scheduler...")
    print(f"Current time: {datetime.now()}")
    print(f"Next run at: {config['daily_time']}")

    scheduler = schedule_analysis(test_analysis, config)

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped")
