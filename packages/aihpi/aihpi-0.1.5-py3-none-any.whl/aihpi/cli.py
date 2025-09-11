"""Command-line interface for aihpi job submission and monitoring."""

import argparse
import sys
import importlib.util
from pathlib import Path
from typing import Optional, List
import traceback

from .core.executor import SlurmJobExecutor
from .core.config import JobConfig
from .monitoring.monitoring import JobMonitor, JobStatus


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message: str, color: str = Colors.ENDC) -> None:
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")


def print_status(message: str) -> None:
    """Print status message in blue."""
    print_colored(f"ℹ️  {message}", Colors.OKBLUE)


def print_success(message: str) -> None:
    """Print success message in green."""
    print_colored(f"✅ {message}", Colors.OKGREEN)


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print_colored(f"⚠️  {message}", Colors.WARNING)


def print_error(message: str) -> None:
    """Print error message in red."""
    print_colored(f"❌ {message}", Colors.FAIL)


def load_config(config_path: str) -> JobConfig:
    """
    Load JobConfig from a Python file.
    
    Args:
        config_path: Path to the config Python file
        
    Returns:
        JobConfig object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        AttributeError: If config file doesn't have 'config' variable
        Exception: Other config loading errors
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # Load the Python file as a module
    spec = importlib.util.spec_from_file_location("config_module", config_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load config file: {config_path}")
    
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    # Extract the JobConfig object
    if not hasattr(config_module, 'config'):
        raise AttributeError(
            f"Config file must contain a 'config' variable with JobConfig object. "
            f"Example:\n\nfrom aihpi import JobConfig\nconfig = JobConfig(...)\n"
        )
    
    config = config_module.config
    if not isinstance(config, JobConfig):
        raise TypeError(
            f"'config' variable must be a JobConfig object, got {type(config)}"
        )
    
    # Check for optional app config
    app_config = getattr(config_module, 'app_config', None)
    llamafactory_config_path = getattr(config_module, 'llamafactory_config_path', None)
    
    # Store additional configs as attributes
    if app_config:
        setattr(config, '_app_config', app_config)
    if llamafactory_config_path:
        setattr(config, '_llamafactory_config_path', llamafactory_config_path)
    
    return config


def validate_config(config: JobConfig) -> List[str]:
    """
    Validate JobConfig and return list of validation errors.
    
    Args:
        config: JobConfig to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Check required fields
    if not config.job_name or not config.job_name.strip():
        errors.append("job_name is required")
    
    if config.num_nodes < 1:
        errors.append("num_nodes must be >= 1")
    
    if config.gpus_per_node < 0:
        errors.append("gpus_per_node must be >= 0")
    
    if not config.walltime or not config.walltime.strip():
        errors.append("walltime is required")
    
    if not config.partition or not config.partition.strip():
        errors.append("partition is required")
    
    # Validate walltime format
    try:
        parts = config.walltime.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid format")
        hours, minutes, seconds = map(int, parts)
        if not (0 <= hours <= 999 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
            raise ValueError("Invalid time values")
    except ValueError:
        errors.append("walltime must be in format HH:MM:SS (e.g., '02:30:00')")
    
    # Check container config
    if config.container and config.container.name and not config.container.name.strip():
        errors.append("container name cannot be empty if specified")
    
    return errors


def create_python_wrapper(script_path: str, app_config: Optional[str] = None) -> callable:
    """
    Create a wrapper function that executes a Python script.
    
    Args:
        script_path: Path to the Python script to execute
        app_config: Optional application config path
        
    Returns:
        Callable wrapper function
    """
    def wrapper():
        import subprocess
        import sys
        import os
        
        # Set app config environment variable if provided
        if app_config:
            os.environ['APP_CONFIG_PATH'] = app_config
        
        # Execute the Python script
        result = subprocess.run([sys.executable, script_path], capture_output=False)
        return result.returncode
    
    return wrapper


def determine_submission_mode(config: JobConfig, command: List[str]) -> str:
    """
    Determine which submission method to use based on config and command.
    
    Args:
        config: JobConfig object
        command: Command to execute
        
    Returns:
        Submission mode: 'function', 'distributed', or 'cli'
    """
    # CLI commands (non-Python executables)
    if command and not command[0].endswith('.py'):
        return 'cli'
    
    # Python scripts
    if config.num_nodes > 1:
        return 'distributed'
    else:
        return 'function'


def format_job_status(status: JobStatus) -> str:
    """Format job status for display."""
    if status.state == "RUNNING":
        color = Colors.OKGREEN
        icon = "🏃"
    elif status.state == "PENDING":
        color = Colors.WARNING
        icon = "⏳"
    elif status.state == "COMPLETED":
        color = Colors.OKGREEN
        icon = "✅"
    elif status.state in ["FAILED", "CANCELLED", "TIMEOUT"]:
        color = Colors.FAIL
        icon = "❌"
    else:
        color = Colors.ENDC
        icon = "❓"
    
    return f"{icon} Job {status.job_id} ({color}{status.state}{Colors.ENDC}): {status.name}"


def cmd_run(args) -> int:
    """Handle 'aihpi run' command."""
    try:
        # Load and validate config
        print_status(f"Loading config from {args.config}")
        config = load_config(args.config)
        
        # Validate config
        validation_errors = validate_config(config)
        if validation_errors:
            print_error("Config validation failed:")
            for error in validation_errors:
                print_error(f"  • {error}")
            return 1
        
        print_success("Config loaded successfully")
        
        # Parse command
        command = args.command
        app_config_path = args.app_config
        
        # Check for embedded app config
        if hasattr(config, '_llamafactory_config_path') and not app_config_path:
            app_config_path = getattr(config, '_llamafactory_config_path')
        
        # Determine submission mode
        submission_mode = determine_submission_mode(config, command)
        print_status(f"Submission mode: {submission_mode}")
        
        # Create executor
        executor = SlurmJobExecutor(config)
        
        # Submit job based on mode
        if submission_mode == 'function':
            if len(command) != 1 or not command[0].endswith('.py'):
                print_error("Function mode requires exactly one Python script")
                return 1
            
            script_path = command[0]
            if not Path(script_path).exists():
                print_error(f"Python script not found: {script_path}")
                return 1
            
            wrapper_func = create_python_wrapper(script_path, app_config_path)
            print_status(f"Submitting single-node Python job: {script_path}")
            job = executor.submit_function(wrapper_func)
            
        elif submission_mode == 'distributed':
            if len(command) != 1 or not command[0].endswith('.py'):
                print_error("Distributed mode requires exactly one Python script")
                return 1
            
            script_path = command[0]
            if not Path(script_path).exists():
                print_error(f"Python script not found: {script_path}")
                return 1
            
            wrapper_func = create_python_wrapper(script_path, app_config_path)
            print_status(f"Submitting distributed Python job: {script_path} (nodes={config.num_nodes})")
            job = executor.submit_distributed_training(wrapper_func)
            
        elif submission_mode == 'cli':
            print_status(f"Submitting CLI job: {' '.join(command)}")
            job = executor.submit_cli_training(command, config_path=app_config_path)
        
        # Print job information
        print_success(f"Job submitted successfully!")
        print_status(f"Job ID: {job.job_id}")
        print_status(f"Job name: {config.job_name}")
        print_status(f"Logs: {job.paths.stdout}")
        
        # Start monitoring if requested
        if args.monitor:
            print_status("Starting job monitoring...")
            monitor = JobMonitor(login_node=config.login_node)
            
            try:
                # Wait for job completion
                final_status = monitor.wait_for_job(job.job_id, poll_interval=30)
                print_success(f"Job completed with status: {final_status.state}")
                
                if final_status.state == "COMPLETED":
                    return 0
                else:
                    return 1
                    
            except KeyboardInterrupt:
                print_warning("Monitoring interrupted by user")
                print_status(f"Job {job.job_id} is still running")
                return 0
        
        return 0
        
    except FileNotFoundError as e:
        print_error(str(e))
        return 1
    except (AttributeError, TypeError, ImportError) as e:
        print_error(f"Config error: {e}")
        return 1
    except Exception as e:
        print_error(f"Job submission failed: {e}")
        if args.debug:
            traceback.print_exc()
        return 1


def cmd_monitor(args) -> int:
    """Handle 'aihpi monitor' command."""
    try:
        job_id = args.job_id
        monitor = JobMonitor(login_node=args.login_node)
        
        if args.logs:
            # Stream logs
            print_status(f"Streaming logs for job {job_id}")
            # TODO: Implement log streaming
            print_warning("Log streaming not yet implemented")
            return 0
        
        if args.follow:
            # Follow job status
            print_status(f"Monitoring job {job_id} (press Ctrl+C to stop)")
            try:
                final_status = monitor.wait_for_job(job_id, poll_interval=30)
                print_success(f"Job completed: {format_job_status(final_status)}")
                return 0 if final_status.state == "COMPLETED" else 1
                
            except KeyboardInterrupt:
                print_warning("Monitoring stopped by user")
                return 0
        else:
            # One-time status check
            status = monitor.get_job_status(job_id)
            if status:
                print(format_job_status(status))
                return 0
            else:
                print_error(f"Job {job_id} not found")
                return 1
                
    except Exception as e:
        print_error(f"Monitoring failed: {e}")
        return 1


def cmd_status(args) -> int:
    """Handle 'aihpi status' command."""
    try:
        monitor = JobMonitor(login_node=args.login_node)
        jobs = monitor.get_user_jobs(user=args.user)
        
        if not jobs:
            print_status("No jobs found")
            return 0
        
        print_status(f"Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"  {format_job_status(job)}")
        
        return 0
        
    except Exception as e:
        print_error(f"Status check failed: {e}")
        return 1


def cmd_cancel(args) -> int:
    """Handle 'aihpi cancel' command."""
    try:
        job_id = args.job_id
        monitor = JobMonitor(login_node=args.login_node)
        
        success = monitor.cancel_job(job_id)
        if success:
            print_success(f"Job {job_id} cancelled successfully")
            return 0
        else:
            print_error(f"Failed to cancel job {job_id}")
            return 1
            
    except Exception as e:
        print_error(f"Cancel failed: {e}")
        return 1


def cmd_logs(args) -> int:
    """Handle 'aihpi logs' command."""
    print_warning("Log streaming not yet implemented")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="aihpi - AI High Performance Infrastructure CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Submit single-node Python job
  aihpi run train.py --config slurm_config.py

  # Submit distributed job with monitoring
  aihpi run train.py --config distributed_config.py --monitor

  # Submit LlamaFactory job
  aihpi run llamafactory-cli train --config job_config.py --app-config train.yaml

  # Monitor a job
  aihpi monitor 12345 --follow

  # List user jobs
  aihpi status

  # Cancel a job
  aihpi cancel 12345
        """
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Show debug information'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Submit a job')
    run_parser.add_argument('command', nargs='+', help='Command to execute (script.py or cli command)')
    run_parser.add_argument('--config', required=True, help='SLURM configuration file (Python)')
    run_parser.add_argument('--app-config', help='Application configuration file')
    run_parser.add_argument('--monitor', action='store_true', help='Monitor job until completion')
    run_parser.set_defaults(func=cmd_run)
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor a job')
    monitor_parser.add_argument('job_id', help='Job ID to monitor')
    monitor_parser.add_argument('--follow', action='store_true', help='Follow job status until completion')
    monitor_parser.add_argument('--logs', action='store_true', help='Show job logs')
    monitor_parser.add_argument('--login-node', help='SSH login node for remote monitoring')
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show job status')
    status_parser.add_argument('--user', help='Username to filter jobs')
    status_parser.add_argument('--login-node', help='SSH login node for remote monitoring')
    status_parser.set_defaults(func=cmd_status)
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a job')
    cancel_parser.add_argument('job_id', help='Job ID to cancel')
    cancel_parser.add_argument('--login-node', help='SSH login node for remote operations')
    cancel_parser.set_defaults(func=cmd_cancel)
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='Show job logs')
    logs_parser.add_argument('job_id', help='Job ID to show logs for')
    logs_parser.add_argument('--follow', action='store_true', help='Follow log output')
    logs_parser.add_argument('--login-node', help='SSH login node for remote operations')
    logs_parser.set_defaults(func=cmd_logs)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except Exception as e:
        print_error(f"Command failed: {e}")
        if args.debug:
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())