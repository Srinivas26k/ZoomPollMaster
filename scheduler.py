"""
Scheduler Module for the Automated Zoom Poll Generator.
Handles scheduling of regular tasks such as transcript capture and poll posting.
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from logger import get_logger

# Import config or use default values if not available
try:
    from config import TRANSCRIPT_CAPTURE_INTERVAL, POLL_POSTING_INTERVAL
except ImportError:
    # Default values if config module is not available
    TRANSCRIPT_CAPTURE_INTERVAL = 10 * 60  # 10 minutes in seconds
    POLL_POSTING_INTERVAL = 15 * 60  # 15 minutes in seconds

logger = get_logger()


class TaskScheduler:
    """
    Handles scheduling of application tasks at regular intervals.
    """
    
    def __init__(self):
        """Initialize the task scheduler."""
        self.scheduler = BackgroundScheduler()
        self.transcript_job = None
        self.poll_job = None
        self.one_time_jobs = {}
        logger.info("Task scheduler initialized")
    
    def start(self):
        """Start the scheduler."""
        try:
            # Prevent starting an already running scheduler
            if self.scheduler.running:
                logger.warning("Scheduler is already running")
                return True
                
            self.scheduler.start()
            logger.info("Scheduler started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            return False
    
    def stop(self):
        """Stop the scheduler and all scheduled jobs."""
        try:
            # Only attempt to shut down a running scheduler
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
                
                # Reset job references
                self.transcript_job = None
                self.poll_job = None
                self.one_time_jobs = {}
                
            else:
                logger.warning("Scheduler is not running")
                
            return True
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
            return False
    
    def schedule_transcript_capture(self, capture_func, interval=None):
        """
        Schedule regular transcript capture.
        
        Args:
            capture_func: Function to call for transcript capture
            interval: Interval in seconds (defaults to config value)
        """
        if interval is None:
            interval = TRANSCRIPT_CAPTURE_INTERVAL
            
        try:
            # Remove existing job if any
            if self.transcript_job:
                self.scheduler.remove_job(self.transcript_job.id)
                
            # Add new job with the specified interval
            self.transcript_job = self.scheduler.add_job(
                capture_func,
                IntervalTrigger(seconds=interval),
                id='transcript_capture',
                name='Transcript Capture',
                replace_existing=True
            )
            
            logger.info(f"Scheduled transcript capture every {interval} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling transcript capture: {str(e)}")
            return False
    
    def schedule_poll_posting(self, post_func, interval=None):
        """
        Schedule regular poll posting.
        
        Args:
            post_func: Function to call for poll posting
            interval: Interval in seconds (defaults to config value)
        """
        if interval is None:
            interval = POLL_POSTING_INTERVAL
            
        try:
            # Remove existing job if any
            if self.poll_job:
                self.scheduler.remove_job(self.poll_job.id)
                
            # Add new job with the specified interval
            self.poll_job = self.scheduler.add_job(
                post_func,
                IntervalTrigger(seconds=interval),
                id='poll_posting',
                name='Poll Posting',
                replace_existing=True
            )
            
            logger.info(f"Scheduled poll posting every {interval} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling poll posting: {str(e)}")
            return False
    
    def schedule_one_time_task(self, task_func, delay_seconds, task_name=None):
        """
        Schedule a one-time task after a specified delay.
        
        Args:
            task_func: Function to call
            delay_seconds: Delay in seconds before execution
            task_name: Optional name for the task
        """
        if task_name is None:
            task_name = f"one_time_task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        try:
            # Calculate the execution time
            run_time = datetime.now() + timedelta(seconds=delay_seconds)
            
            # Add one-time job with the specified delay
            job = self.scheduler.add_job(
                task_func,
                DateTrigger(run_date=run_time),
                id=task_name,
                name=task_name,
                replace_existing=True
            )
            
            # Store reference to the job
            self.one_time_jobs[task_name] = job
            
            logger.info(f"Scheduled one-time task '{task_name}' to run in {delay_seconds} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling one-time task: {str(e)}")
            return False
    
    def get_next_run_time(self, job_type):
        """
        Get the next scheduled run time for a specific job type.
        
        Args:
            job_type: String identifying the job type
            
        Returns:
            Datetime of next run, or None if job not scheduled
        """
        try:
            if job_type == 'transcript_capture' and self.transcript_job:
                return self.transcript_job.next_run_time
            elif job_type == 'poll_posting' and self.poll_job:
                return self.poll_job.next_run_time
            elif job_type in self.one_time_jobs:
                return self.one_time_jobs[job_type].next_run_time
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
            return None
    
    def get_status(self):
        """
        Get the status of the scheduler and scheduled jobs.
        
        Returns:
            Dict containing scheduler status information
        """
        try:
            status = {
                "scheduler_running": self.scheduler.running,
                "transcript_job_scheduled": self.transcript_job is not None,
                "poll_job_scheduled": self.poll_job is not None,
                "one_time_jobs_count": len(self.one_time_jobs)
            }
            
            # Add next run times if available
            if self.transcript_job:
                next_capture = self.transcript_job.next_run_time
                status["next_transcript_capture"] = next_capture.strftime("%H:%M:%S") if next_capture else "Not scheduled"
            
            if self.poll_job:
                next_poll = self.poll_job.next_run_time
                status["next_poll_posting"] = next_poll.strftime("%H:%M:%S") if next_poll else "Not scheduled"
            
            # Add list of one-time jobs
            one_time_job_status = {}
            for name, job in self.one_time_jobs.items():
                if job.next_run_time:
                    one_time_job_status[name] = job.next_run_time.strftime("%H:%M:%S")
                else:
                    one_time_job_status[name] = "Completed or removed"
            
            status["one_time_jobs"] = one_time_job_status
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {str(e)}")
            return {
                "scheduler_running": False,
                "error": str(e)
            }