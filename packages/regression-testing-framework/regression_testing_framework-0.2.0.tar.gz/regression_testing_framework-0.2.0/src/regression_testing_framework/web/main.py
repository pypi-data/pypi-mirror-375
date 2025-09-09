"""
FastAPI application for the regression testing framework web interface.
"""

import os
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ..celery_app import celery_app
from .api import jobs, status, config, files

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Reggie - Regression Testing Framework",
        description="Web interface for managing and monitoring regression tests",
        version="0.1.11"
    )
    
    # Get the web directory path
    web_dir = Path(__file__).parent
    
    # Mount static files
    static_dir = web_dir / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Setup templates
    templates_dir = web_dir / "templates"
    if templates_dir.exists():
        templates = Jinja2Templates(directory=str(templates_dir))
        app.state.templates = templates
    
    # Include API routers
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
    app.include_router(status.router, prefix="/api/status", tags=["status"])
    app.include_router(config.router, prefix="/api/config", tags=["config"])
    app.include_router(files.router, prefix="/api/files", tags=["files"])
    
    # Root route - dashboard
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Main dashboard page."""
        if hasattr(app.state, 'templates'):
            return app.state.templates.TemplateResponse(
                "dashboard.html", 
                {"request": request}
            )
        return HTMLResponse("""
        <html>
            <head><title>Reggie Dashboard</title></head>
            <body>
                <h1>Reggie - Regression Testing Framework</h1>
                <p>API is running. Install with reggie[web] for full UI.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)
    
    # File browser page
    @app.get("/files", response_class=HTMLResponse)
    async def file_browser(request: Request):
        """File browser page."""
        if hasattr(app.state, 'templates'):
            return app.state.templates.TemplateResponse(
                "files.html", 
                {"request": request}
            )
        return HTMLResponse("""
        <html>
            <head><title>File Browser - Reggie</title></head>
            <body>
                <h1>File Browser</h1>
                <p>Install with reggie[web] for full UI.</p>
                <p><a href="/">Back to Dashboard</a></p>
            </body>
        </html>
        """)
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Check Celery connection
            i = celery_app.control.inspect()
            stats = i.stats()
            worker_count = len(stats) if stats else 0
            
            return {
                "status": "healthy",
                "celery_workers": worker_count,
                "celery_broker": "connected" if stats is not None else "disconnected"
            }
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "error": str(e)}
            )
    
    return app

def run_web(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the web application."""
    app = create_app()
    uvicorn.run(
        "regression_testing_framework.web.main:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload
    )

if __name__ == "__main__":
    run_web()