"""
Test suite orchestration tasks for Celery.

This module contains tasks for coordinating multiple test executions,
managing test suites, and providing progress tracking.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from celery import group, chord
from ..celery_app import celery_app
from ..config_parser import load_config, get_test_names

# Base logs directory
BASE_LOG_DIR = "test_runs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)


def create_run_directory():
    """Create a timestamped directory for this test run"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(BASE_LOG_DIR, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def get_all_test_names(config):
    """
    Get all test names from the configuration, handling both top-level and nested tests.
    """
    # Get top-level tests first
    test_names = get_test_names(config)
    
    # If empty, check if tests are under 'tests' key
    if len(test_names) == 0 and "tests" in config and isinstance(config["tests"], dict):
        test_names = list(config["tests"].keys())
        print(f"Found {len(test_names)} tests under 'tests' section")
    
    return test_names


def calculate_summary(results):
    """Calculate test summary statistics."""
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    success_percent = (successful / total) * 100 if total > 0 else 0
    failing_tests = [r for r in results if not r.get("success", False)]
    
    return successful, total, success_percent, failing_tests


def write_report(output_path, successful, total, success_percent, results):
    """Write test report to file."""
    with open(output_path, "w") as f:
        f.write(f"Test Summary\n")
        f.write(f"============\n")
        f.write(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)\n\n")
        
        f.write("Test Results:\n")
        for result in results:
            status = "PASS" if result.get("success", False) else "FAIL"
            f.write(f"{result.get('config', 'unknown')}: {status}\n")
            if not result.get("success", False) and result.get("error_trace"):
                for line in result["error_trace"]:
                    f.write(f"  Error: {line}\n")
        
        f.write("\nLog Files:\n")
        for result in results:
            if result.get("log_file"):
                log_filename = os.path.basename(result["log_file"])
                f.write(f"{result.get('config', 'unknown')}: {log_filename}\n")


def create_latest_symlink(run_dir):
    """Create or update the 'latest' symlink to point to the most recent test run."""
    latest_link = os.path.join(BASE_LOG_DIR, "latest")
    
    if os.path.exists(latest_link):
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        else:
            shutil.rmtree(latest_link)
    
    try:
        os.symlink(os.path.basename(run_dir), latest_link)
    except (OSError, AttributeError):
        os.makedirs(latest_link, exist_ok=True)
        for file in os.listdir(run_dir):
            src = os.path.join(run_dir, file)
            dst = os.path.join(latest_link, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)


@celery_app.task(bind=True, name='regression_testing_framework.tasks.finalize_test_suite')
def finalize_test_suite_task(self, results, run_dir, config_path):
    """
    Callback task to finalize test suite execution.
    This runs after all individual tests complete.
    """
    try:
        # Calculate summary
        successful, total, success_percent, failing_tests = calculate_summary(results)
        
        # Write report
        output_path = os.path.join(run_dir, "test_report.txt")
        write_report(output_path, successful, total, success_percent, results)
        
        # Create latest symlink
        create_latest_symlink(run_dir)
        
        # Return summary
        summary = {
            "successful": successful,
            "total": total,
            "success_percent": success_percent,
            "failing_tests": len(failing_tests),
            "run_dir": run_dir,
            "report_path": output_path,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        print(f"Test suite completed: {successful}/{total} tests passed ({success_percent:.1f}%)")
        
        return summary
        
    except Exception as e:
        print(f"Error finalizing test suite: {e}")
        return {
            "error": str(e),
            "run_dir": run_dir,
            "completed_at": datetime.utcnow().isoformat()
        }


@celery_app.task(bind=True, name='regression_testing_framework.tasks.run_test_suite')
def run_test_suite_task(self, config_path, max_workers=None):
    """
    Celery task to orchestrate running a complete test suite.
    
    This task coordinates the execution of multiple individual test tasks
    using Celery's group and chord primitives for parallel execution.
    
    Args:
        config_path: Path to the configuration file
        max_workers: Maximum number of concurrent test tasks (optional)
        
    Returns:
        Dictionary with test suite results and metadata
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'initializing', 'config_path': config_path}
        )
        
        # Load configuration and get test names
        config = load_config(config_path)
        test_names = get_all_test_names(config)
        
        if not test_names:
            return {
                "success": False,
                "error": "No tests found in configuration file",
                "total_tests": 0
            }
        
        # Create run directory
        run_dir = create_run_directory()
        print(f"Created test run directory: {run_dir}")
        
        # Copy config file to run directory
        config_filename = os.path.basename(config_path)
        try:
            shutil.copy2(config_path, os.path.join(run_dir, config_filename))
        except Exception as e:
            print(f"Warning: Failed to copy config file: {e}")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'launching_tests',
                'total_tests': len(test_names),
                'run_dir': run_dir
            }
        )
        
        print(f"Launching {len(test_names)} tests in parallel using Celery")
        
        # Create a group of individual test tasks
        test_jobs = group(
            celery_app.signature('regression_testing_framework.tasks.run_single_test', 
                                args=[config_path, test_name, run_dir])
            for test_name in test_names
        )
        
        # Create a chord that runs all tests in parallel and then finalizes
        chord_job = chord(test_jobs)(
            celery_app.signature('regression_testing_framework.tasks.finalize_test_suite',
                                args=[run_dir, config_path])
        )
        
        # Store chord result ID for tracking
        chord_result_id = chord_job.id
        
        # Update state with job information
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'tests_running',
                'total_tests': len(test_names),
                'run_dir': run_dir,
                'chord_id': chord_result_id,
                'test_names': test_names
            }
        )
        
        # Return job information without waiting for completion
        # The caller can use the chord_id to check status
        return {
            "success": True,
            "total_tests": len(test_names),
            "run_dir": run_dir,
            "chord_id": chord_result_id,
            "task_id": self.request.id,
            "status": "running"
        }
        
    except Exception as e:
        print(f"Error in test suite orchestration: {e}")
        import traceback
        traceback.print_exc()
        
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'error': str(e)
            }
        )
        
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name='regression_testing_framework.tasks.run_test_suite_async')
def run_test_suite_async_task(self, config_path, max_workers=None):
    """
    Async version of test suite runner that returns immediately with job IDs.
    
    This is ideal for web applications where you want to start tests
    and then poll for progress/completion.
    
    Args:
        config_path: Path to the configuration file
        max_workers: Maximum number of concurrent test tasks (optional)
        
    Returns:
        Dictionary with job IDs for tracking progress
    """
    try:
        # Load configuration and get test names
        config = load_config(config_path)
        test_names = get_all_test_names(config)
        
        if not test_names:
            return {
                "success": False,
                "error": "No tests found in configuration file",
                "total_tests": 0
            }
        
        # Create run directory
        run_dir = create_run_directory()
        
        # Copy config file to run directory
        config_filename = os.path.basename(config_path)
        try:
            shutil.copy2(config_path, os.path.join(run_dir, config_filename))
        except Exception as e:
            print(f"Warning: Failed to copy config file: {e}")
        
        print(f"Launching {len(test_names)} tests asynchronously")
        
        # Create and launch the chord job
        test_jobs = group(
            celery_app.signature('regression_testing_framework.tasks.run_single_test',
                                args=[config_path, test_name, run_dir])
            for test_name in test_names
        )
        
        chord_job = chord(test_jobs)(
            celery_app.signature('regression_testing_framework.tasks.finalize_test_suite',
                                args=[run_dir, config_path])
        )
        
        # Return immediately with tracking information
        return {
            "success": True,
            "total_tests": len(test_names),
            "run_dir": run_dir,
            "chord_id": chord_job.id,
            "test_names": test_names,
            "task_id": self.request.id,
            "status": "launched"
        }
        
    except Exception as e:
        print(f"Error launching async test suite: {e}")
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }
