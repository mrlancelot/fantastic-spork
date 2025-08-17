"""
Job Manager for async processing and status tracking
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum

from utils.convex_client import get_db

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobManager:
    def __init__(self):
        self.db = get_db()
    
    def create_job(
        self,
        job_type: str,
        user_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new job and return its ID"""
        job_data = {
            "type": job_type,
            "status": JobStatus.PENDING,
            "retryCount": 0,
            "maxRetries": 3,
        }
        
        # Only add optional fields if they have values
        if user_id:
            job_data["userId"] = user_id
        if payload:
            job_data["payload"] = payload
        
        try:
            saved_job_id = self.db.save_job(job_data)
            logger.info(f"Created job {saved_job_id} of type {job_type}")
            return saved_job_id
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            raise
    
    def start_job(self, job_id: str) -> None:
        """Mark job as processing"""
        updates = {
            "status": JobStatus.PROCESSING,
            "startedAt": int(datetime.now().timestamp() * 1000)
        }
        
        try:
            self.db.update_job(job_id, updates)
            logger.info(f"Started job {job_id}")
        except Exception as e:
            logger.error(f"Failed to start job {job_id}: {e}")
            raise
    
    def complete_job(self, job_id: str, result: Any = None) -> None:
        """Mark job as completed with result"""
        updates = {
            "status": JobStatus.COMPLETED,
            "completedAt": int(datetime.now().timestamp() * 1000),
            "result": result
        }
        
        try:
            self.db.update_job(job_id, updates)
            logger.info(f"Completed job {job_id}")
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            raise
    
    def fail_job(self, job_id: str, error: str) -> None:
        """Mark job as failed with error"""
        updates = {
            "status": JobStatus.FAILED,
            "completedAt": int(datetime.now().timestamp() * 1000),
            "error": error
        }
        
        try:
            self.db.update_job(job_id, updates)
            logger.error(f"Failed job {job_id}: {error}")
        except Exception as e:
            logger.error(f"Failed to update failed job {job_id}: {e}")
            raise
    
    def retry_job(self, job_id: str) -> None:
        """Increment retry count and reset to pending"""
        try:
            # Get current job data to check retry count
            job = self.db.query("queries:getJob", {"id": job_id})
            
            if job and job.get("retryCount", 0) < job.get("maxRetries", 3):
                updates = {
                    "status": JobStatus.PENDING,
                    "retryCount": job.get("retryCount", 0) + 1,
                    "error": None,
                    "scheduledFor": int(datetime.now().timestamp() * 1000)
                }
                self.db.update_job(job_id, updates)
                logger.info(f"Retrying job {job_id} (attempt {updates['retryCount']})")
            else:
                self.fail_job(job_id, "Max retries exceeded")
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and details"""
        try:
            job = self.db.query("queries:getJob", {"id": job_id})
            return job
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    def update_job_progress(self, job_id: str, progress_data: Dict[str, Any]) -> None:
        """Update job with progress information"""
        updates = {
            "result": progress_data  # Store progress in result field
        }
        
        try:
            self.db.update_job(job_id, updates)
            logger.info(f"Updated progress for job {job_id}")
        except Exception as e:
            logger.error(f"Failed to update progress for job {job_id}: {e}")
            raise


# Singleton instance
_job_manager_instance = None

def get_job_manager() -> JobManager:
    """Get singleton job manager instance"""
    global _job_manager_instance
    if _job_manager_instance is None:
        _job_manager_instance = JobManager()
    return _job_manager_instance