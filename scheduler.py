"""
Scheduler Module for the Automated Zoom Poll Generator.
Handles scheduled execution of tasks at specific intervals.
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional, List
from threading import Timer, Thread, Event

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

# Configure logger
logger = logging.getLogger(__name__)

class TaskScheduler:
    """
    Handles scheduling of recurring and one-time tasks.
    Manages the timing of transcript capture, poll generation, and poll posting.
    """
    
    def __init__(self):
        """Initialize the task scheduler."""
        self.scheduler = BackgroundScheduler()
        self.running = False
        self.jobs = {}  # Dictionary to keep track of scheduled jobs
        self.next_transcript_time = None
        self.next_poll_time = None
        
        # Default configuration
        self.transcript_interval = 10  # minutes
        self.poll_interval = 15  # minutes
        
        logger.info("TaskScheduler initialized")
    
    def start(self) -> bool:
        """
        Start the scheduler.
        
        Returns:
            Boolean indicating whether start was successful
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return True
        
        try:
            self.scheduler.start()
            self.running = True
            logger.info("Scheduler started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the scheduler and clear all jobs.
        
        Returns:
            Boolean indicating whether stop was successful
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return True
        
        try:
            # Remove all jobs
            for job_id in list(self.jobs.keys()):
                self.remove_job(job_id)
            
            # Shut down the scheduler
            self.scheduler.shutdown()
            self.running = False
            self.next_transcript_time = None
            self.next_poll_time = None
            
            logger.info("Scheduler stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
            return False
    
    def schedule_transcript_capture(self, callback: Callable, interval_minutes: int = None) -> bool:
        """
        Schedule regular transcript captures.
        
        Args:
            callback: Function to call for transcript capture
            interval_minutes: Interval between captures in minutes (default: use instance default)
            
        Returns:
            Boolean indicating whether scheduling was successful
        """
        if not self.running:
            logger.error("Scheduler is not running - call start() first")
            return False
        
        interval = interval_minutes if interval_minutes is not None else self.transcript_interval
        
        try:
            # Remove existing job if any
            if 'transcript_capture' in self.jobs:
                self.remove_job('transcript_capture')
            
            # Calculate next run time
            next_run_time = datetime.now() + timedelta(minutes=interval)
            self.next_transcript_time = next_run_time
            
            # Add new job
            job = self.scheduler.add_job(
                callback,
                IntervalTrigger(minutes=interval),
                next_run_time=next_run_time,
                id='transcript_capture',
                replace_existing=True
            )
            
            self.jobs['transcript_capture'] = job
            logger.info(f"Scheduled transcript capture every {interval} minutes, starting at {next_run_time.strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule transcript capture: {str(e)}")
            return False
    
    def schedule_poll_posting(self, callback: Callable, interval_minutes: int = None) -> bool:
        """
        Schedule regular poll postings.
        
        Args:
            callback: Function to call for poll posting
            interval_minutes: Interval between postings in minutes (default: use instance default)
            
        Returns:
            Boolean indicating whether scheduling was successful
        """
        if not self.running:
            logger.error("Scheduler is not running - call start() first")
            return False
        
        interval = interval_minutes if interval_minutes is not None else self.poll_interval
        
        try:
            # Remove existing job if any
            if 'poll_posting' in self.jobs:
                self.remove_job('poll_posting')
            
            # Calculate next run time
            next_run_time = datetime.now() + timedelta(minutes=interval)
            self.next_poll_time = next_run_time
            
            # Add new job
            job = self.scheduler.add_job(
                callback,
                IntervalTrigger(minutes=interval),
                next_run_time=next_run_time,
                id='poll_posting',
                replace_existing=True
            )
            
            self.jobs['poll_posting'] = job
            logger.info(f"Scheduled poll posting every {interval} minutes, starting at {next_run_time.strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule poll posting: {str(e)}")
            return False
    
    def schedule_one_time_task(self, callback: Callable, delay_seconds: int, job_id: str) -> bool:
        """
        Schedule a one-time task to run after a specified delay.
        
        Args:
            callback: Function to call
            delay_seconds: Delay in seconds before executing the task
            job_id: Unique identifier for the job
            
        Returns:
            Boolean indicating whether scheduling was successful
        """
        if not self.running:
            logger.error("Scheduler is not running - call start() first")
            return False
        
        try:
            # Remove existing job with same ID if any
            if job_id in self.jobs:
                self.remove_job(job_id)
            
            # Calculate run time
            run_time = datetime.now() + timedelta(seconds=delay_seconds)
            
            # Add new job
            job = self.scheduler.add_job(
                callback,
                DateTrigger(run_date=run_time),
                id=job_id,
                replace_existing=True
            )
            
            self.jobs[job_id] = job
            logger.info(f"Scheduled one-time task '{job_id}' to run at {run_time.strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule one-time task: {str(e)}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: ID of the job to remove
            
        Returns:
            Boolean indicating whether removal was successful
        """
        if job_id not in self.jobs:
            logger.warning(f"Job '{job_id}' not found")
            return False
        
        try:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            logger.info(f"Removed job '{job_id}'")
            
            # Update next times if needed
            if job_id == 'transcript_capture':
                self.next_transcript_time = None
            elif job_id == 'poll_posting':
                self.next_poll_time = None
                
            return True
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {str(e)}")
            return False
    
    def reschedule_job(self, job_id: str, new_interval_minutes: int = None, next_run_time: datetime = None) -> bool:
        """
        Reschedule an existing job with a new interval or next run time.
        
        Args:
            job_id: ID of the job to reschedule
            new_interval_minutes: New interval in minutes (optional)
            next_run_time: New next run time (optional)
            
        Returns:
            Boolean indicating whether rescheduling was successful
        """
        if job_id not in self.jobs:
            logger.warning(f"Job '{job_id}' not found - cannot reschedule")
            return False
        
        try:
            job = self.jobs[job_id]
            
            if new_interval_minutes is not None:
                # Update the interval
                self.scheduler.reschedule_job(
                    job_id,
                    trigger=IntervalTrigger(minutes=new_interval_minutes)
                )
                
                # Update internal tracking
                if job_id == 'transcript_capture':
                    self.transcript_interval = new_interval_minutes
                elif job_id == 'poll_posting':
                    self.poll_interval = new_interval_minutes
            
            if next_run_time is not None:
                # Update the next run time
                job.next_run_time = next_run_time
                
                # Update internal tracking
                if job_id == 'transcript_capture':
                    self.next_transcript_time = next_run_time
                elif job_id == 'poll_posting':
                    self.next_poll_time = next_run_time
            
            logger.info(f"Rescheduled job '{job_id}'")
            return True
        except Exception as e:
            logger.error(f"Failed to reschedule job '{job_id}': {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler.
        
        Returns:
            Dict containing status information
        """
        status = {
            "scheduler_running": self.running,
            "num_scheduled_jobs": len(self.jobs),
            "scheduled_jobs": list(self.jobs.keys()),
        }
        
        # Add next run times if available
        if self.next_transcript_time:
            status["next_transcript_time"] = self.next_transcript_time.strftime("%H:%M:%S")
        
        if self.next_poll_time:
            status["next_poll_time"] = self.next_poll_time.strftime("%H:%M:%S")
        
        return status

# Simple alternative implementation using Python's Timer class
# This can be used as a fallback if APScheduler is not available
class SimpleScheduler:
    """
    Simplified scheduler implementation using Python's Timer class.
    Provides a subset of the TaskScheduler functionality.
    """
    
    def __init__(self):
        """Initialize the simple scheduler."""
        self.timers = {}
        self.running = False
        self.next_transcript_time = None
        self.next_poll_time = None
        
        # Default configuration
        self.transcript_interval = 10 * 60  # seconds
        self.poll_interval = 15 * 60  # seconds
        
        logger.info("SimpleScheduler initialized")
    
    def start(self) -> bool:
        """
        Start the scheduler.
        
        Returns:
            Boolean indicating whether start was successful
        """
        self.running = True
        logger.info("SimpleScheduler started")
        return True
    
    def stop(self) -> bool:
        """
        Stop all scheduled tasks.
        
        Returns:
            Boolean indicating whether stop was successful
        """
        for timer_id in list(self.timers.keys()):
            self.cancel_timer(timer_id)
        
        self.running = False
        logger.info("SimpleScheduler stopped")
        return True
    
    def schedule_recurring_task(self, callback: Callable, interval_seconds: int, timer_id: str) -> bool:
        """
        Schedule a recurring task.
        
        Args:
            callback: Function to call
            interval_seconds: Interval between executions in seconds
            timer_id: Unique identifier for the timer
            
        Returns:
            Boolean indicating whether scheduling was successful
        """
        if not self.running:
            logger.error("Scheduler is not running - call start() first")
            return False
        
        # Cancel existing timer if any
        self.cancel_timer(timer_id)
        
        def recurring_task():
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in recurring task '{timer_id}': {str(e)}")
            finally:
                # Reschedule the task
                if self.running:
                    self.schedule_recurring_task(callback, interval_seconds, timer_id)
        
        # Create and start the timer
        timer = Timer(interval_seconds, recurring_task)
        timer.daemon = True
        timer.start()
        
        # Store the timer
        self.timers[timer_id] = timer
        
        # Update next run time
        next_run_time = datetime.now() + timedelta(seconds=interval_seconds)
        if timer_id == 'transcript_capture':
            self.next_transcript_time = next_run_time
        elif timer_id == 'poll_posting':
            self.next_poll_time = next_run_time
        
        logger.info(f"Scheduled recurring task '{timer_id}' every {interval_seconds} seconds")
        return True
    
    def schedule_one_time_task(self, callback: Callable, delay_seconds: int, timer_id: str) -> bool:
        """
        Schedule a one-time task.
        
        Args:
            callback: Function to call
            delay_seconds: Delay before execution in seconds
            timer_id: Unique identifier for the timer
            
        Returns:
            Boolean indicating whether scheduling was successful
        """
        if not self.running:
            logger.error("Scheduler is not running - call start() first")
            return False
        
        # Cancel existing timer if any
        self.cancel_timer(timer_id)
        
        # Create and start the timer
        timer = Timer(delay_seconds, callback)
        timer.daemon = True
        timer.start()
        
        # Store the timer
        self.timers[timer_id] = timer
        
        logger.info(f"Scheduled one-time task '{timer_id}' with {delay_seconds} seconds delay")
        return True
    
    def cancel_timer(self, timer_id: str) -> bool:
        """
        Cancel a scheduled timer.
        
        Args:
            timer_id: ID of the timer to cancel
            
        Returns:
            Boolean indicating whether cancellation was successful
        """
        if timer_id in self.timers:
            timer = self.timers[timer_id]
            timer.cancel()
            del self.timers[timer_id]
            
            # Update next run times if needed
            if timer_id == 'transcript_capture':
                self.next_transcript_time = None
            elif timer_id == 'poll_posting':
                self.next_poll_time = None
                
            logger.info(f"Cancelled timer '{timer_id}'")
            return True
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler.
        
        Returns:
            Dict containing status information
        """
        status = {
            "scheduler_running": self.running,
            "num_active_timers": len(self.timers),
            "active_timers": list(self.timers.keys()),
        }
        
        # Add next run times if available
        if self.next_transcript_time:
            status["next_transcript_time"] = self.next_transcript_time.strftime("%H:%M:%S")
        
        if self.next_poll_time:
            status["next_poll_time"] = self.next_poll_time.strftime("%H:%M:%S")
        
        return status

# Helper function to create an instance with appropriate implementation
def create_scheduler(use_simple_scheduler: bool = False) -> Any:
    """
    Create and return a scheduler instance.
    
    Args:
        use_simple_scheduler: Whether to use the SimpleScheduler implementation
    
    Returns:
        TaskScheduler or SimpleScheduler instance
    """
    if use_simple_scheduler:
        return SimpleScheduler()
    else:
        return TaskScheduler()