import click
import os
import sys
from multiprocessing import cpu_count
from regression_testing_framework.test_runner import run_test_from_cli
from regression_testing_framework.command_generator import generate_commands


def run_with_celery(config_path, mode='sync'):
    """Run tests using Celery for task execution."""
    try:
        from regression_testing_framework.celery_app import celery_app
        from celery.result import AsyncResult
        
        if mode == 'sync':
            # Synchronous execution - wait for completion
            print("Running tests synchronously with Celery...")
            result = celery_app.send_task(
                'regression_testing_framework.tasks.run_test_suite',
                args=[config_path]
            )
            orchestration_result = result.get()  # Get orchestration result
            
            if orchestration_result.get('success'):
                chord_id = orchestration_result.get('chord_id')
                print(f"Tests launched successfully! Waiting for completion...")
                print(f"Run directory: {orchestration_result.get('run_dir')}")
                
                # Wait for the chord (all tests) to complete
                chord_result = AsyncResult(chord_id, app=celery_app)
                final_summary = chord_result.get()  # Wait for final summary
                
                print(f"\nTest Suite Completed!")
                if final_summary and isinstance(final_summary, dict):
                    print(f"Results: {final_summary.get('successful', 0)}/{final_summary.get('total', 0)} tests passed")
                    print(f"Report: {final_summary.get('report_path', 'N/A')}")
                else:
                    print("Summary not available")
            else:
                print(f"Test suite failed: {orchestration_result.get('error', 'Unknown error')}")
                
        elif mode == 'async':
            # Asynchronous execution - return job ID
            print("Launching tests asynchronously with Celery...")
            result = celery_app.send_task(
                'regression_testing_framework.tasks.run_test_suite_async',
                args=[config_path]
            )
            job_info = result.get()
            
            if job_info.get('success'):
                print(f"Test suite launched successfully!")
                print(f"Total tests: {job_info.get('total_tests', 0)}")
                print(f"Chord ID: {job_info.get('chord_id')}")
                print(f"Run directory: {job_info.get('run_dir')}")
                print(f"\nUse 'reggie status {job_info.get('chord_id')}' to check progress")
            else:
                print(f"Failed to launch test suite: {job_info.get('error', 'Unknown error')}")
                
    except ImportError:
        print("Error: Celery tasks not available. Make sure Redis is running and Celery is installed.")
        return False
    except Exception as e:
        print(f"Error running tests with Celery: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


@click.group()
def cli():
    """Reggie - Regression Testing Framework"""
    pass


@cli.command()
@click.option('-i', '--input', 'config_path', required=True, type=click.Path(exists=True), 
              help='Path to the YAML configuration file.')
@click.option('-o', '--output', 'output_path', required=False, type=click.Path(), 
              help='Path to save the test run report.')
@click.option('--dry-run', is_flag=True, 
              help='List the commands that will run without executing them.')
@click.option('-p', '--parallel', 'max_workers', default=None, type=int, 
              help=f'Maximum number of parallel test executions. Default: {cpu_count()} (all CPUs)')
@click.option('--mode', type=click.Choice(['multiprocessing', 'celery-sync', 'celery-async']), 
              default='celery-sync',
              help='Execution mode: multiprocessing (legacy), celery-sync (wait for completion), or celery-async (return immediately)')
def run(config_path, output_path, dry_run, max_workers, mode):
    """Run regression tests defined in a YAML configuration file."""
    
    if dry_run:
        commands = generate_commands(config_path)
        click.echo(f"Commands to be run ({len(commands)}):")
        for command in commands:
            click.echo(command)
        if output_path:
            click.echo(f"Output report will be saved to: {output_path}")
        return
    
    # Set default max_workers if not specified
    if max_workers is None:
        max_workers = cpu_count()
    
    if mode == 'multiprocessing':
        # Legacy multiprocessing approach
        click.echo(f"Running tests with multiprocessing ({max_workers} workers)...")
        results, run_dir = run_test_from_cli(config_path, output_path, max_workers=max_workers)
        click.echo(f"Test run completed. All logs saved in: {run_dir}")
        
    elif mode in ['celery-sync', 'celery-async']:
        # New Celery approach
        celery_mode = 'sync' if mode == 'celery-sync' else 'async'
        success = run_with_celery(config_path, celery_mode)
        if not success:
            click.echo("Falling back to multiprocessing mode...")
            results, run_dir = run_test_from_cli(config_path, output_path, max_workers=max_workers)
            click.echo(f"Test run completed. All logs saved in: {run_dir}")


@cli.command()
@click.argument('task_id')
def status(task_id):
    """Check the status of a Celery task by ID."""
    try:
        from celery.result import AsyncResult
        from regression_testing_framework.celery_app import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        click.echo(f"Task ID: {task_id}")
        click.echo(f"Status: {result.status}")
        
        if result.info:
            if isinstance(result.info, dict):
                for key, value in result.info.items():
                    click.echo(f"{key}: {value}")
            else:
                click.echo(f"Info: {result.info}")
                
        if result.successful():
            click.echo(f"Result: {result.result}")
            
    except ImportError:
        click.echo("Error: Celery not available. Install celery to use status checking.")
    except Exception as e:
        click.echo(f"Error checking task status: {e}")


@cli.command()
def worker():
    """Start a Celery worker process."""
    try:
        import subprocess
        import sys
        
        # Determine optimal worker concurrency (one per CPU)
        concurrency = cpu_count()
        
        click.echo(f"Starting Celery worker with {concurrency} processes...")
        click.echo("Press Ctrl+C to stop the worker")
        
        # Start Celery worker
        cmd = [
            sys.executable, '-m', 'celery', 
            '-A', 'regression_testing_framework.celery_app',
            'worker',
            '--concurrency', str(concurrency),
            '--loglevel', 'info',
            '--queues', 'test_execution,celery'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        click.echo("\nWorker stopped.")
    except Exception as e:
        click.echo(f"Error starting worker: {e}")


@cli.command()
def flower():
    """Start Flower monitoring for Celery workers."""
    try:
        import subprocess
        import sys
        
        click.echo("Starting Flower monitoring on http://localhost:5555")
        click.echo("Press Ctrl+C to stop Flower")
        
        cmd = [
            sys.executable, '-m', 'celery', 
            '-A', 'regression_testing_framework.celery_app',
            'flower',
            '--port=5555'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        click.echo("\nFlower stopped.")
    except ImportError:
        click.echo("Error: Flower not installed. Install with: pip install flower")
    except Exception as e:
        click.echo(f"Error starting Flower: {e}")


@cli.command()
@click.option('--host', '-h', default='0.0.0.0', help='Host to bind to')
@click.option('--port', '-p', type=int, default=8000, help='Port to bind to')
@click.option('--reload', '-r', is_flag=True, help='Enable auto-reload for development')
def web(host, port, reload):
    """Start the web interface (requires reggie[web] installation)."""
    try:
        from regression_testing_framework.web.main import run_web
        click.echo(f"Starting web interface at http://{host}:{port}")
        run_web(host=host, port=port, reload=reload)
        
    except ImportError:
        click.echo("Web interface not available. Install with: pip install reggie[web]", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nWeb server stopped by user")


if __name__ == '__main__':
    cli()
