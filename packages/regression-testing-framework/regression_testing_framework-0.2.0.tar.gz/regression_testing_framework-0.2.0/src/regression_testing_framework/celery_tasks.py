import os
import subprocess
import logging
import shlex
from datetime import datetime
import shutil
from pathlib import Path
import re
from .database import log_run
from .config_parser import (
    load_config,
    get_test_config,
    get_base_command,
    get_test_names,
    process_params,
    process_environment
)
import concurrent.futures

# Base logs directory
BASE_LOG_DIR = "test_runs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)


def create_run_directory():
    """Create a timestamped directory for this test run"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(BASE_LOG_DIR, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def build_command(base_command, params):
    """
    Build a command by splitting the base command and parameters.
    """
    # Start with splitting the base command
    cmd_parts = base_command.split()
    
    # Add each parameter after splitting it
    for param in params:
        cmd_parts.extend(param.split())
    
    # Join back to a string for shell execution
    return " ".join(cmd_parts)


def execute_command(cmd_to_run, env):
    """
    Execute a command and return the result.
    
    Args:
        cmd_to_run: Command string to run
        env: Environment dictionary
        
    Returns:
        CompletedProcess object with stdout, stderr, and returncode
    """
    # The success/failure determination is based solely on the exit code
    # Stderr output will not cause a test to fail
    return subprocess.run(
        cmd_to_run,
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )


def create_log_file(run_dir, test_name, start_time, cmd_to_run, env_vars, result):
    """
    Create a log file with test execution details.
    """
    success = result.returncode == 0
    status_str = "PASS" if success else "FAIL"
    start_time_formatted = start_time.strftime("%Y%m%d_%H%M%S")
    
    # Create a descriptive log filename
    log_filename = f"{start_time_formatted}_{test_name}_{status_str}.log"
    log_file = os.path.join(run_dir, log_filename)
    
    with open(log_file, "w") as log:
        log.write(f"Test: {test_name}\n")
        log.write(f"Status: {'SUCCESS' if success else 'FAILURE'}\n")
        
        # Write the command exactly as it will be executed
        log.write(f"Command: {cmd_to_run}\n")
        
        # Include environment variables in the log
        if env_vars:
            log.write("Environment:\n")
            for key, value in env_vars.items():
                log.write(f"  {key}={value}\n")
        
        log.write(f"Return code: {result.returncode}\n")
        log.write(f"Start time: {start_time}\n")
        log.write(f"End time: {datetime.utcnow()}\n\n")
        log.write(f"--- STDOUT ---\n")
        log.write(result.stdout)
        if result.stderr:
            log.write("\n\n--- STDERR ---\n")
            log.write(result.stderr)
    
    return log_file


def create_exception_log(run_dir, test_name, start_time, exception):
    """
    Create a log file for an exception during test execution.
    """
    start_time_formatted = start_time.strftime("%Y%m%d_%H%M%S")
    log_filename = f"{start_time_formatted}_{test_name}_EXCEPTION.log"
    log_file = os.path.join(run_dir, log_filename)
    
    with open(log_file, "w") as log:
        log.write(f"Test: {test_name}\n")
        log.write(f"Status: EXCEPTION\n")
        log.write(f"Start time: {start_time}\n")
        log.write(f"End time: {datetime.utcnow()}\n\n")
        log.write(f"--- ERROR ---\n")
        log.write(str(exception))
    
    return log_file


def process_test_result(result, success):
    """
    Process test result to extract error traces and failure information.
    """
    if success:
        return None, None
    
    stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    
    error_message = f"Command failed with return code {returncode}"
    error_trace = stderr.split("\n")[-3:] if stderr else None
    
    if not error_trace:
        error_trace = [error_message]
        
    failure = stderr if stderr else error_message
    
    return error_trace, failure


def run_single_test(config_path, test_name, run_dir):
    """
    Run a single test from a configuration file.
    """
    # Load configuration
    config = load_config(config_path)
    test_config = get_test_config(config, test_name)
    
    # Validate test configuration
    if not test_config or not isinstance(test_config, dict):
        return {
            "config": test_name,
            "success": False,
            "error_trace": ["Test configuration not found or invalid"],
            "log_file": None
        }
    
    # Start timing
    start_time = datetime.utcnow()
    
    try:
        # Get base command and parameters
        base_command = get_base_command(config, test_config)
        params = process_params(test_config, False)
        
        # Setup environment variables
        env = os.environ.copy()
        env_vars = process_environment(test_config)
        env.update(env_vars)
        
        # Simplified command building
        cmd_to_run = build_command(base_command, params)
        
        result = execute_command(cmd_to_run, env)
        
        # Determine success/failure based ONLY on return code, never on stderr content
        success = result.returncode == 0
        
        # Create log file
        log_file = create_log_file(run_dir, test_name, start_time, cmd_to_run, env_vars, result)
        
        # Process error information only if the test actually failed (non-zero exit code)
        if not success:
            error_trace, failure = process_test_result(result, success)
        else:
            error_trace, failure = None, None
        
    except Exception as e:
        success = False
        error_trace = str(e).split("\n")
        failure = str(e)
        log_file = create_exception_log(run_dir, test_name, start_time, e)
    
    # Record end time and log the run
    end_time = datetime.utcnow()
    log_run(test_name, test_name, cmd_to_run, success, start_time, end_time, log_file, error_trace, failure)
    
    # Return result information
    result_info = {
        "config": test_name, 
        "success": success, 
        "log_file": log_file, 
        "error_trace": error_trace if not success else None
    }
    
    return result_info

def run_tests(config_path, run_dir, max_workers=4):
    """
    Run multiple tests in parallel using ThreadPoolExecutor.
    """
    config = load_config(config_path)
    test_names = get_test_names(config)
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all test jobs to the thread pool
        future_to_test = {
            executor.submit(run_single_test, config_path, test_name, run_dir): test_name 
            for test_name in test_names
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_test):
            test_name = future_to_test[future]
            try:
                result = future.result()
                results.append(result)
                status = "Succeeded" if result["success"] else "Failed"
                print(f"Test '{test_name}' {status}")
            except Exception as e:
                print(f"Error running test '{test_name}': {e}")
                results.append({
                    "config": test_name,
                    "success": False,
                    "error_trace": [str(e)],
                    "log_file": None
                })
    
    return results


def calculate_summary(results):
    """
    Calculate test summary statistics.
    """
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    success_percent = (successful / total) * 100 if total > 0 else 0
    failing_tests = [r for r in results if not r["success"]]
    
    return successful, total, success_percent, failing_tests


def print_summary(successful, total, success_percent, failing_tests):
    """
    Print test summary to console.
    """
    print("\n=== TEST SUMMARY ===")
    print(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)")
    
    if failing_tests:
        print("\nFailing tests:")
        for test in failing_tests:
            print(f"- {test['config']}")
            if test.get("error_trace"):
                error = test["error_trace"] if isinstance(test["error_trace"], list) else [test["error_trace"]]
                for line in error:
                    if line:
                        print(f"  {line}")


def determine_output_path(output_path, run_dir):
    """
    Determine the final output path for the test report.
    """
    if not output_path:
        output_path = os.path.join(run_dir, "test_report.txt")
    elif os.path.dirname(output_path) == '':
        output_path = os.path.join(run_dir, output_path)
    
    return output_path


def write_report(output_path, successful, total, success_percent, results):
    """
    Write test report to file.
    """
    with open(output_path, "w") as f:
        f.write(f"Test Summary\n")
        f.write(f"============\n")
        f.write(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)\n\n")
        
        f.write("Test Results:\n")
        for result in results:
            status = "PASS" if result["success"] else "FAIL"
            f.write(f"{result['config']}: {status}\n")
            if not result["success"] and result.get("error_trace"):
                error = result["error_trace"] if isinstance(result["error_trace"], list) else [result["error_trace"]]
                for line in error:
                    if line:
                        f.write(f"  Error: {line}\n")
        
        f.write("\nLog Files:\n")
        for result in results:
            if result.get("log_file"):
                # Get the base filename only
                log_filename = os.path.basename(result["log_file"])
                f.write(f"{result['config']}: {log_filename}\n")


def create_latest_symlink(run_dir):
    """
    Create or update the 'latest' symlink to point to the most recent test run.
    """
    latest_link = os.path.join(BASE_LOG_DIR, "latest")
    
    # Remove existing link/directory
    if os.path.exists(latest_link):
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        else:
            shutil.rmtree(latest_link)
    
    try:
        # Create relative symlink on UNIX systems
        os.symlink(os.path.basename(run_dir), latest_link)
    except (OSError, AttributeError):
        # On Windows or if symlinks aren't supported, create a directory with copies
        os.makedirs(latest_link, exist_ok=True)
        for file in os.listdir(run_dir):
            src = os.path.join(run_dir, file)
            dst = os.path.join(latest_link, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)


def run_test_from_cli(config_path, output_path=None, max_workers=4):
    """
    Run tests from CLI using thread pool for parallelism.
    """
    # Create a unique directory for this test run
    run_dir = create_run_directory()
    print(f"Launching tests from {config_path}")
    print(f"Test run directory: {run_dir}")
    
    # Copy the config file to the run directory for reference
    config_filename = os.path.basename(config_path)
    shutil.copy2(config_path, os.path.join(run_dir, config_filename))
    
    # Run the tests
    results = run_tests(config_path, run_dir, max_workers=max_workers)
    
    # Calculate and print summary
    successful, total, success_percent, failing_tests = calculate_summary(results)
    print_summary(successful, total, success_percent, failing_tests)
    
    # Determine output path and write report
    final_output_path = determine_output_path(output_path, run_dir)
    write_report(final_output_path, successful, total, success_percent, results)
    print(f"Report written to {final_output_path}")
    
    # Create a symlink to the latest run for convenience
    create_latest_symlink(run_dir)
    
    return results, run_dir

