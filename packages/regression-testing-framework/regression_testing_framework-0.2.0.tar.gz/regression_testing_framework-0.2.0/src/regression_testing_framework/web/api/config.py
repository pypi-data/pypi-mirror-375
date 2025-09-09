"""
Configuration API endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import os
import yaml
from pathlib import Path

router = APIRouter()

@router.get("/")
async def list_configs() -> Dict[str, Any]:
    """List available configuration files."""
    try:
        configs = []
        
        # Look for config files in common locations
        search_paths = [
            Path.cwd(),  # Current directory
            Path.cwd() / "configs",  # configs subdirectory
            Path.home() / ".reggie",  # User configs
        ]
        
        config_files = []
        for search_path in search_paths:
            if search_path.exists():
                # Look for .yaml and .yml files
                for pattern in ["*.yaml", "*.yml"]:
                    config_files.extend(search_path.glob(pattern))
        
        # Also check for default config files
        common_names = ["config.yaml", "reggie.yaml", "test.yaml", "default.yaml"]
        for name in common_names:
            file_path = Path.cwd() / name
            if file_path.exists() and file_path not in config_files:
                config_files.append(file_path)
        
        # Build config list
        for config_file in config_files:
            try:
                # Try to read the config to validate it
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Extract some metadata if possible
                name = config_file.name
                description = None
                if isinstance(config_data, dict):
                    description = config_data.get('description', 
                                                config_data.get('name', 
                                                              f"Config file: {name}"))
                
                configs.append({
                    "name": name,
                    "path": str(config_file.absolute()),
                    "description": description,
                    "size": config_file.stat().st_size,
                    "modified": config_file.stat().st_mtime
                })
                
            except Exception:
                # If we can't read it, still include it but mark as potentially invalid
                configs.append({
                    "name": config_file.name,
                    "path": str(config_file.absolute()),
                    "description": f"Config file: {config_file.name} (validation failed)",
                    "size": config_file.stat().st_size,
                    "modified": config_file.stat().st_mtime,
                    "warning": "Could not validate config file"
                })
        
        return {
            "configs": configs,
            "total": len(configs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list configs: {str(e)}")

@router.get("/template")
async def get_config_template() -> Dict[str, Any]:
    """Get a template configuration file."""
    template = {
        "name": "Example Test Configuration",
        "description": "Template configuration for regression tests",
        "output_dir": "./test_runs",
        "max_workers": 4,
        "timeout": 300,
        "tests": [
            {
                "name": "example_test",
                "command": "echo 'Hello, World!'",
                "expected_exit_code": 0,
                "timeout": 30,
                "description": "Simple example test"
            }
        ]
    }
    
    return {
        "template": template,
        "description": "Basic configuration template for regression testing"
    }