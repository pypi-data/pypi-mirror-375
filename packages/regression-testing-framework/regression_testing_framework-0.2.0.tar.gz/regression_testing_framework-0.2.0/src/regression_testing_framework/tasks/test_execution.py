"""
Individual test execution tasks for Celery.

This module contains the core task for running a single test in a Celery worker.
Each test runs as a separate Celery task, allowing for distributed processing
across multiple CPU cores.
"""

import os
import subprocess
from datetime import datetime
from celery import current_task
from ..celery_app import celery_app
from ..database import log_run
from ..config_parser import (
    load_config,
    get_test_config,
    get_base_command,
    process_params,
    process_environment
)


def execute_command(cmd, env, timeout=None):
    """
    Execute a shell command and return the result.
    
    Args:
        cmd: Command string to execute
        env: Environment dictionary
        timeout: Maximum time in seconds to wait for the command to complete
        
    Returns:
        (stdout, stderr, returncode)
    """
    print(f"Running command: {cmd}")
    
    try:
        # Simple command execution using shell=True
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            shell=True,
            timeout=timeout
        )
        return process.stdout, process.stderr, process.returncode
        
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds: {cmd}")
        return f"Command timed out after {timeout} seconds", "Timeout", 124
    except Exception as e:
        print(f"Error executing command: {e}")
        return "", str(e), 1


def create_log_file(run_dir, test_name, start_time, cmd, env_vars, stdout, stderr, returncode):
    """Create a log file with test execution details."""
    success = returncode == 0
    status_str = "PASS" if success else "FAIL"
    start_time_formatted = start_time.strftime("%Y%m%d_%H%M%S")
    
    log_filename = f"{start_time_formatted}_{test_name}_{status_str}.log"
    log_file = os.path.join(run_dir, log_filename)
    
    with open(log_file, "w") as log:
        log.write(f"Test: {test_name}\n")
        log.write(f"Status: {'SUCCESS' if success else 'FAILURE'}\n")
        log.write(f"Command: {cmd}\n")
        
        if env_vars:
            log.write("Environment:\n")
            for key, value in env_vars.items():
                log.write(f"  {key}={value}\n")
        
        log.write(f"Return code: {returncode}\n")
        log.write(f"Start time: {start_time}\n")
        log.write(f"End time: {datetime.utcnow()}\n\n")
        log.write(f"--- STDOUT ---\n")
        log.write(stdout)
        if stderr:
            log.write("\n\n--- STDERR ---\n")
            log.write(stderr)
    
    return log_file


def get_test_command(config, test_config):
    """
    Get the command string for a test, handling both direct command and base_command + params styles.
    """
    if "command" in test_config:
        # Direct command format
        cmd = test_config["command"]
        
        # Add parameters if they exist
        if "params" in test_config and test_config["params"]:
            params = " ".join(str(p) for p in test_config["params"])
            cmd = f"{cmd} {params}"
        return cmd
    else:
        # Legacy format with base_command and params
        base_command = get_base_command(config, test_config)
        params = process_params(test_config)
        
        # Build command
        cmd_parts = [base_command]
        if params:
            cmd_parts.extend(params)
        return ' '.join(cmd_parts)


def get_test_timeout(config, test_config, default_timeout=1800):
    """
    Get the timeout value for a test, handling defaults.
    """
    timeout = test_config.get('timeout', config.get('timeout', default_timeout))
    try:
        return int(timeout)
    except (ValueError, TypeError):
        return default_timeout


def find_test_config(config, test_name):
    """
    Find the configuration for a test, handling both top-level and nested configurations.
    """
    # First check top-level
    test_config = get_test_config(config, test_name)
    
    # If not found, check under 'tests' key
    if not test_config and "tests" in config and test_name in config["tests"]:
        test_config = config["tests"][test_name]
        
    return test_config


@celery_app.task(bind=True, name='regression_testing_framework.tasks.run_single_test')
def run_single_test_task(self, config_path, test_name, run_dir):
    """
    Celery task to run a single test.
    
    Args:
        config_path: Path to the configuration file
        test_name: Name of the test to run
        run_dir: Directory to store test results
        
    Returns:
        Dictionary with test results
    """
    # Update task state to PROGRESS
    self.update_state(
        state='PROGRESS',
        meta={'test_name': test_name, 'status': 'starting'}
    )
    
    try:
        # Load configuration
        config = load_config(config_path)
        test_config = find_test_config(config, test_name)
        
        if not test_config:
            return {
                "config": test_name,
                "success": False,
                "error_trace": ["Test configuration not found"],
                "log_file": None,
                "task_id": self.request.id
            }
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'test_name': test_name, 'status': 'executing'}
        )
        
        # Start timing
        start_time = datetime.utcnow()
        
        # Get command, environment variables, and timeout
        cmd = get_test_command(config, test_config)
        env = os.environ.copy()
        env_vars = process_environment(test_config)
        env.update(env_vars)
        timeout = get_test_timeout(config, test_config)
        
        # Execute command
        stdout, stderr, returncode = execute_command(cmd, env, timeout)
        
        # Create log file
        log_file = create_log_file(run_dir, test_name, start_time, cmd, env_vars, stdout, stderr, returncode)
        
        # A test is successful if return code is 0, regardless of stderr content
        success = returncode == 0
        error_trace = [] if success else [f"Command failed with return code {returncode}"]
        failure = "" if success else (stderr or f"Command failed with return code {returncode}")
        
        # Record to database
        end_time = datetime.utcnow()
        log_run(test_name, test_name, cmd, success, start_time, end_time, log_file, error_trace, failure)
        
        print(f"Test '{test_name}' {'Succeeded' if success else 'Failed'}")
        
        result = {
            "config": test_name,
            "success": success,
            "error_trace": error_trace,
            "log_file": log_file,
            "task_id": self.request.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        # Update final state
        self.update_state(
            state='SUCCESS',
            meta={
                'test_name': test_name, 
                'status': 'completed',
                'success': success,
                'result': result
            }
        )
        
        return result
        
    except Exception as e:
        print(f"Error running test '{test_name}': {e}")
        import traceback
        traceback.print_exc()
        
        # Update error state
        self.update_state(
            state='FAILURE',
            meta={
                'test_name': test_name,
                'status': 'failed',
                'error': str(e)
            }
        )
        
        return {
            "config": test_name,
            "success": False,
            "error_trace": [str(e)],
            "log_file": None,
            "task_id": self.request.id
        }
