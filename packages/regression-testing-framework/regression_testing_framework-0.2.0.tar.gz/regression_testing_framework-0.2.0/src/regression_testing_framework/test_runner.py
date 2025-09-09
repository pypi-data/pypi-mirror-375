import os
import subprocess
import logging
from datetime import datetime
import shutil
from pathlib import Path
import signal
import sys
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from .database import log_run
from .config_parser import (
    load_config,
    get_test_config,
    get_base_command,
    get_test_names,
    process_params,
    process_environment
)

# Base logs directory
BASE_LOG_DIR = "test_runs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# Default timeout for commands (in seconds)
DEFAULT_TIMEOUT = 1800  # 30 minutes


def setup_signal_handlers():
    """Set up signal handlers to ensure clean exit."""
    def signal_handler(sig, frame):
        print(f"\nCaught signal {sig}. Exiting gracefully...")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def create_run_directory():
    """Create a timestamped directory for this test run"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(BASE_LOG_DIR, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


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
    
    Args:
        config: Global configuration dictionary
        test_config: Test-specific configuration dictionary
        
    Returns:
        Command string to execute
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


def get_test_timeout(config, test_config):
    """
    Get the timeout value for a test, handling defaults.
    
    Args:
        config: Global configuration dictionary
        test_config: Test-specific configuration dictionary
        
    Returns:
        Timeout value in seconds
    """
    timeout = test_config.get('timeout', config.get('timeout', DEFAULT_TIMEOUT))
    try:
        return int(timeout)
    except (ValueError, TypeError):
        return DEFAULT_TIMEOUT


def find_test_config(config, test_name):
    """
    Find the configuration for a test, handling both top-level and nested configurations.
    
    Args:
        config: Configuration dictionary
        test_name: Name of the test
        
    Returns:
        Test configuration dictionary or None if not found
    """
    # First check top-level
    test_config = get_test_config(config, test_name)
    
    # If not found, check under 'tests' key
    if not test_config and "tests" in config and test_name in config["tests"]:
        test_config = config["tests"][test_name]
        
    return test_config


def get_all_test_names(config):
    """
    Get all test names from the configuration, handling both top-level and nested tests.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of test names
    """
    # Get top-level tests first
    test_names = get_test_names(config)
    
    # If empty, check if tests are under 'tests' key
    if len(test_names) == 0 and "tests" in config and isinstance(config["tests"], dict):
        test_names = list(config["tests"].keys())
        print(f"Found {len(test_names)} tests under 'tests' section")
    
    return test_names


def run_single_test(config_path, test_name, run_dir):
    """
    Run a single test as a subprocess.
    
    Args:
        config_path: Path to the configuration file
        test_name: Name of the test to run
        run_dir: Directory to store test results
        
    Returns:
        Dictionary with test results
    """
    # Load configuration
    try:
        config = load_config(config_path)
        test_config = find_test_config(config, test_name)
        
        if not test_config:
            return {
                "config": test_name,
                "success": False,
                "error_trace": ["Test configuration not found"],
                "log_file": None
            }
        
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
        error_trace = None if success else [f"Command failed with return code {returncode}"]
        
        # Record to database
        end_time = datetime.utcnow()
        log_run(test_name, test_name, cmd, success, start_time, end_time, log_file, error_trace, None)
        
        print(f"Test '{test_name}' {'Succeeded' if success else 'Failed'}")
        
        return {
            "config": test_name,
            "success": success,
            "error_trace": error_trace,
            "log_file": log_file
        }
        
    except Exception as e:
        print(f"Error running test '{test_name}': {e}")
        import traceback
        traceback.print_exc()
        return {
            "config": test_name,
            "success": False,
            "error_trace": [str(e)],
            "log_file": None
        }


def run_tests(config_path, run_dir, max_workers=None):
    """
    Run multiple tests in parallel using ProcessPoolExecutor.
    
    Args:
        config_path: Path to the configuration file
        run_dir: Directory to store test results
        max_workers: Number of worker processes to use
        
    Returns:
        List of test results
    """
    config = load_config(config_path)
    test_names = get_all_test_names(config)
    
    if not test_names:
        print("No tests found in the configuration file.")
        return []
    
    # Determine the number of worker processes
    if max_workers is None:
        from multiprocessing import cpu_count
        max_workers = min(cpu_count(), len(test_names))
    else:
        max_workers = min(max_workers, len(test_names), os.cpu_count() or 1)
    
    print(f"Starting {len(test_names)} tests with {max_workers} parallel processes")
    
    # Run tests in parallel
    results = run_tests_parallel(config_path, test_names, run_dir, max_workers)
    
    print(f"All {len(test_names)} tests completed execution")
    return results


def run_tests_parallel(config_path, test_names, run_dir, max_workers):
    """
    Run tests in parallel using a process pool.
    
    Args:
        config_path: Path to the configuration file
        test_names: List of test names to run
        run_dir: Directory to store test results
        max_workers: Number of worker processes to use
        
    Returns:
        List of test results
    """
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to the executor
        future_to_test = {
            executor.submit(run_single_test, config_path, test_name, run_dir): test_name
            for test_name in test_names
        }
        
        # Collect results as they complete
        completed = 0
        total_tests = len(test_names)
        for future in concurrent.futures.as_completed(future_to_test):
            test_name = future_to_test[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Test '{test_name}' raised an exception: {e}")
                results.append({
                    "config": test_name,
                    "success": False,
                    "error_trace": [f"Exception: {str(e)}"],
                    "log_file": None
                })
            
            # Simple progress output
            completed += 1
            print(f"Progress: {completed}/{total_tests} tests completed")
    
    return results


def calculate_summary(results):
    """Calculate test summary statistics."""
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    success_percent = (successful / total) * 100 if total > 0 else 0
    failing_tests = [r for r in results if not r["success"]]
    
    return successful, total, success_percent, failing_tests


def print_summary(successful, total, success_percent, failing_tests):
    """Print test summary to console."""
    print("\n=== TEST SUMMARY ===")
    print(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)")
    
    if failing_tests:
        print("\nFailing tests:")
        for test in failing_tests:
            print(f"- {test['config']}")
            if test.get("error_trace"):
                for line in test["error_trace"]:
                    print(f"  {line}")


def write_report(output_path, successful, total, success_percent, results):
    """Write test report to file."""
    with open(output_path, "w") as f:
        f.write(f"Test Summary\n")
        f.write(f"============\n")
        f.write(f"Tests passed: {successful}/{total} ({success_percent:.1f}%)\n\n")
        
        f.write("Test Results:\n")
        for result in results:
            status = "PASS" if result["success"] else "FAIL"
            f.write(f"{result['config']}: {status}\n")
            if not result["success"] and result.get("error_trace"):
                for line in result["error_trace"]:
                    f.write(f"  Error: {line}\n")
        
        f.write("\nLog Files:\n")
        for result in results:
            if result.get("log_file"):
                log_filename = os.path.basename(result["log_file"])
                f.write(f"{result['config']}: {log_filename}\n")


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


def run_test_from_cli(config_path, output_path=None, max_workers=None):
    """
    Run tests from CLI using ProcessPoolExecutor.
    
    Args:
        config_path: Path to the configuration file
        output_path: Path to write the output report
        max_workers: Number of worker processes
        
    Returns:
        Tuple of (results, run_dir)
    """
    setup_signal_handlers()
    
    run_dir = create_run_directory()
    print(f"Launching tests from {config_path}")
    print(f"Test run directory: {run_dir}")
    
    # Copy the config file to the run directory (outside try/except to ensure it happens)
    config_filename = os.path.basename(config_path)
    try:
        shutil.copy2(config_path, os.path.join(run_dir, config_filename))
        print(f"Config file copied to {run_dir}/{config_filename}")
    except Exception as e:
        print(f"Warning: Failed to copy config file: {e}")
    
    results = []
    try:
        # Run the tests
        results = run_tests(config_path, run_dir, max_workers=max_workers)
    except Exception as e:
        print(f"Error during test execution: {e}")
        import traceback
        traceback.print_exc()
    
    # Always try to generate the report, even if tests had errors
    try:
        # Calculate and print summary
        successful, total, success_percent, failing_tests = calculate_summary(results)
        print_summary(successful, total, success_percent, failing_tests)
        
        # Determine output path and write report
        if not output_path:
            output_path = os.path.join(run_dir, "test_report.txt")
        elif os.path.dirname(output_path) == '':
            output_path = os.path.join(run_dir, output_path)
        
        write_report(output_path, successful, total, success_percent, results)
        print(f"Report written to {output_path}")
        
        # Create a symlink to the latest run
        create_latest_symlink(run_dir)
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
    
    return results, run_dir
