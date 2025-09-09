"""
Web interface for the regression testing framework.

This module provides FastAPI-based web interface and REST API
for managing test jobs and monitoring their status.
"""

from .main import create_app, run_web

__all__ = ["create_app", "run_web"]