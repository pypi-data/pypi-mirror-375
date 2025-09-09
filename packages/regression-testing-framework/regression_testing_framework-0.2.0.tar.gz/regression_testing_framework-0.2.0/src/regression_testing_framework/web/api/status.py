"""
System status API endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from datetime import datetime

from ...celery_app import celery_app

router = APIRouter()

@router.get("/system")
async def get_system_status() -> Dict[str, Any]:
    """Get overall system status."""
    try:
        # Get Celery worker information
        i = celery_app.control.inspect()
        stats = i.stats() or {}
        active = i.active() or {}
        scheduled = i.scheduled() or {}
        
        # Count jobs
        active_jobs = sum(len(tasks) for tasks in active.values())
        scheduled_jobs = sum(len(tasks) for tasks in scheduled.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "celery": {
                "workers": len(stats),
                "active_jobs": active_jobs,
                "scheduled_jobs": scheduled_jobs,
                "broker_connected": stats is not None
            },
            "status": "healthy" if stats else "degraded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/workers")
async def get_worker_status() -> Dict[str, Any]:
    """Get detailed worker status."""
    try:
        i = celery_app.control.inspect()
        
        # Get various worker information
        stats = i.stats() or {}
        active = i.active() or {}
        scheduled = i.scheduled() or {}
        reserved = i.reserved() or {}
        
        workers = []
        
        for worker_name in stats.keys():
            worker_stats = stats.get(worker_name, {})
            worker_active = active.get(worker_name, [])
            worker_scheduled = scheduled.get(worker_name, [])
            worker_reserved = reserved.get(worker_name, [])
            
            workers.append({
                "name": worker_name,
                "status": "online",
                "pool": worker_stats.get("pool", {}).get("implementation", "unknown"),
                "processes": worker_stats.get("pool", {}).get("max-concurrency", 0),
                "tasks": {
                    "active": len(worker_active),
                    "scheduled": len(worker_scheduled),
                    "reserved": len(worker_reserved),
                    "total": worker_stats.get("total", {})
                }
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_workers": len(workers),
            "workers": workers
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get worker status: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Quick health check endpoint."""
    try:
        i = celery_app.control.inspect()
        stats = i.stats()
        
        return {
            "status": "healthy" if stats else "degraded",
            "celery_workers": len(stats) if stats else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }