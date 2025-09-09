"""
Job management API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Form
from celery.result import AsyncResult
from ...celery_app import celery_app
import os
from pathlib import Path

router = APIRouter()

@router.post("/", response_model=dict)
async def create_job(
    config_path: str = Form(...),
    max_workers: Optional[int] = Form(None),
    description: Optional[str] = Form(None)
):
    """Create a new test job."""
    try:
        # Validate config file exists
        if not os.path.exists(config_path):
            raise HTTPException(status_code=400, detail=f"Config file not found: {config_path}")
        
        # Submit job to Celery
        task = celery_app.send_task(
            'regression_testing_framework.tasks.run_test_suite',
            args=[config_path, max_workers]
        )
        
        return {
            "job_id": task.id,
            "status": "queued",
            "message": "Job has been queued for execution"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[dict])
async def list_jobs(limit: int = 20):
    """List recent jobs."""
    try:
        # Get active tasks from Celery
        i = celery_app.control.inspect()
        active_tasks = i.active()
        scheduled_tasks = i.scheduled()
        
        jobs = []
        
        # Add active tasks
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    jobs.append({
                        "job_id": task["id"],
                        "status": "running",
                        "worker": worker,
                        "name": task["name"],
                        "args": task.get("args", []),
                        "time_start": task.get("time_start")
                    })
        
        # Add scheduled tasks
        if scheduled_tasks:
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    jobs.append({
                        "job_id": task["request"]["id"],
                        "status": "scheduled",
                        "worker": worker,
                        "name": task["request"]["name"],
                        "eta": task.get("eta")
                    })
        
        return jobs[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a specific job."""
    try:
        result = AsyncResult(job_id, app=celery_app)
        
        status_data = {
            "job_id": job_id,
            "status": result.status,
            "progress": None,
            "result": None,
            "error": None
        }
        
        if result.status == "PENDING":
            status_data["progress"] = {"message": "Job is waiting to be processed"}
        elif result.status == "PROGRESS":
            status_data["progress"] = result.info
        elif result.status == "SUCCESS":
            status_data["result"] = result.result
        elif result.status == "FAILURE":
            status_data["error"] = str(result.info)
        
        return status_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running job."""
    try:
        celery_app.control.revoke(job_id, terminate=True)
        return {"message": f"Job {job_id} has been cancelled"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}/logs")
async def get_job_logs(job_id: str):
    """Get logs for a specific job."""
    try:
        result = AsyncResult(job_id, app=celery_app)
        
        if result.status == "SUCCESS" and result.result:
            # Return log file paths from the result
            if isinstance(result.result, dict) and "run_dir" in result.result:
                run_dir = result.result["run_dir"]
                log_files = []
                
                if os.path.exists(run_dir):
                    for file in os.listdir(run_dir):
                        if file.endswith(".log"):
                            log_files.append({
                                "filename": file,
                                "path": os.path.join(run_dir, file)
                            })
                
                return {"job_id": job_id, "log_files": log_files}
        
        return {"job_id": job_id, "log_files": [], "message": "No logs available yet"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))