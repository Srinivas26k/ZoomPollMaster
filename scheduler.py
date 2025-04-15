"""
Scheduler Module for the Automated Zoom Poll Generator.
Handles scheduling of regular tasks such as transcript capture and poll posting.
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from logger import get_logger
from config import TRANSCRIPT_CAPTURE_INTERVAL, POLL_POSTING_INTERVAL

logger = get_logger()


class TaskScheduler:
    """
    Handles scheduling of application tasks at regular intervals.
    """
    
    def __init__(self):
        """Initialize the task scheduler."""
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.job_ids = {}
        self.last_transcript_time = None
        self.last_poll_time = None
        logger.info("Task scheduler initialized")
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            try:
                self.scheduler.start()
                self.is_running = True
                logger.info("Scheduler started")
                return True
            except Exception as e:
                logger.error(f"Error starting scheduler: {str(e)}")
                return False
        else:
            logger.warning("Scheduler already running")
            return True
    
    def stop(self):
        """Stop the scheduler and all scheduled jobs."""
        if self.is_running:
            try:
                self.scheduler.shutdown()
                self.is_running = False
                self.job_ids = {}
                logger.info("Scheduler stopped")
                return True
            except Exception as e:
                logger.error(f"Error stopping scheduler: {str(e)}")
                return False
        else:
            logger.warning("Scheduler not running")
            return True
    
    def schedule_transcript_capture(self, capture_func, interval=None):
        """
        Schedule regular transcript capture.
        
        Args:
            capture_func: Function to call for transcript capture
            interval: Interval in seconds (defaults to config value)
        """
        if not self.is_running:
            self.start()
        
        if not interval:
            interval = TRANSCRIPT_CAPTURE_INTERVAL
        
        try:
            # Remove existing job if present
            if 'transcript_capture' in self.job_ids:
                self.scheduler.remove_job(self.job_ids['transcript_capture'])
            
            # Add new job
            job = self.scheduler.add_job(
                capture_func,
                IntervalTrigger(seconds=interval),
                id='transcript_capture_job',
                replace_existing=True
            )
            
            self.job_ids['transcript_capture'] = job.id
            self.last_transcript_time = datetime.now()
            
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
        if not self.is_running:
            self.start()
        
        if not interval:
            interval = POLL_POSTING_INTERVAL
        
        try:
            # Remove existing job if present
            if 'poll_posting' in self.job_ids:
                self.scheduler.remove_job(self.job_ids['poll_posting'])
            
            # Add new job
            job = self.scheduler.add_job(
                post_func,
                IntervalTrigger(seconds=interval),
                id='poll_posting_job',
                replace_existing=True
            )
            
            self.job_ids['poll_posting'] = job.id
            self.last_poll_time = datetime.now()
            
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
        if not self.is_running:
            self.start()
        
        task_id = task_name or f"one_time_{int(time.time())}"
        
        try:
            # Calculate run time
            run_time = datetime.now() + timedelta(seconds=delay_seconds)
            
            # Add the job
            job = self.scheduler.add_job(
                task_func,
                DateTrigger(run_date=run_time),
                id=task_id,
                replace_existing=True
            )
            
            self.job_ids[task_id] = job.id
            
            logger.info(f"Scheduled one-time task '{task_id}' in {delay_seconds} seconds")
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
        if not self.is_running or job_type not in self.job_ids:
            return None
        
        try:
            job = self.scheduler.get_job(self.job_ids[job_type])
            return job.next_run_time if job else None
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
            return None
    
    def get_status(self):
        """
        Get the status of the scheduler and scheduled jobs.
        
        Returns:
            Dict containing scheduler status information
        """
        status = {
            "is_running": self.is_running,
            "scheduled_jobs": list(self.job_ids.keys()),
            "last_transcript_time": self.last_transcript_time,
            "last_poll_time": self.last_poll_time
        }
        
        # Add next run times if available
        if self.is_running:
            for job_type in self.job_ids:
                next_run = self.get_next_run_time(job_type)
                if next_run:
                    status[f"next_{job_type}_time"] = next_run
        
        return status
