"""Tests for CLI functionality."""

from unittest.mock import Mock, patch, call, mock_open
import pytest
import tempfile
import json
from pathlib import Path
from argparse import Namespace

from aihpi.cli import (
    load_config, validate_config, create_python_wrapper,
    determine_submission_mode, cmd_run, cmd_monitor, 
    cmd_status, cmd_cancel, main
)
from aihpi.core.config import JobConfig, ContainerConfig
from aihpi.monitoring.monitoring import JobStatus


class TestConfigLoading:
    """Tests for config loading functionality."""

    def test_load_config_success(self):
        """Test successful config loading."""
        config_content = '''
from aihpi import JobConfig, ContainerConfig

config = JobConfig(
    job_name="test-job",
    num_nodes=1,
    gpus_per_node=2,
    walltime="01:00:00",
    partition="gpu"
)

app_config = {"learning_rate": 0.001}
llamafactory_config_path = "config.yaml"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(config_content)
            f.flush()
            
            config = load_config(f.name)
            
            assert isinstance(config, JobConfig)
            assert config.job_name == "test-job"
            assert config.num_nodes == 1
            assert config.gpus_per_node == 2
            
            # Check additional attributes
            assert hasattr(config, '_app_config')
            assert hasattr(config, '_llamafactory_config_path')
            assert config._app_config == {"learning_rate": 0.001}
            assert config._llamafactory_config_path == "config.yaml"

    def test_load_config_file_not_found(self):
        """Test config loading with missing file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config("nonexistent_config.py")

    def test_load_config_missing_config_variable(self):
        """Test config loading with missing config variable."""
        config_content = '''
# Missing config variable
other_var = "test"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(config_content)
            f.flush()
            
            with pytest.raises(AttributeError, match="Config file must contain a 'config' variable"):
                load_config(f.name)

    def test_load_config_wrong_type(self):
        """Test config loading with wrong config type."""
        config_content = '''
config = "not a JobConfig object"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(config_content)
            f.flush()
            
            with pytest.raises(TypeError, match="'config' variable must be a JobConfig object"):
                load_config(f.name)


class TestConfigValidation:
    """Tests for config validation."""

    def test_validate_config_success(self):
        """Test successful config validation."""
        config = JobConfig(
            job_name="valid-job",
            num_nodes=2,
            gpus_per_node=4,
            walltime="02:30:00",
            partition="gpu"
        )
        
        errors = validate_config(config)
        assert errors == []

    def test_validate_config_missing_required_fields(self):
        """Test validation with missing required fields."""
        config = JobConfig(
            job_name="",  # Empty job name
            num_nodes=0,  # Invalid num_nodes
            gpus_per_node=-1,  # Invalid gpus_per_node
            walltime="",  # Empty walltime
            partition=""  # Empty partition
        )
        
        errors = validate_config(config)
        
        assert "job_name is required" in errors
        assert "num_nodes must be >= 1" in errors
        assert "gpus_per_node must be >= 0" in errors
        assert "walltime is required" in errors
        assert "partition is required" in errors

    def test_validate_config_invalid_walltime_format(self):
        """Test validation with invalid walltime format."""
        config = JobConfig(
            job_name="test-job",
            walltime="invalid-time",
            partition="gpu"
        )
        
        errors = validate_config(config)
        assert any("walltime must be in format HH:MM:SS" in error for error in errors)

    def test_validate_config_invalid_time_values(self):
        """Test validation with invalid time values."""
        config = JobConfig(
            job_name="test-job",
            walltime="25:61:61",  # Invalid hours, minutes, seconds
            partition="gpu"
        )
        
        errors = validate_config(config)
        assert any("walltime must be in format HH:MM:SS" in error for error in errors)

    def test_validate_config_empty_container_name(self):
        """Test validation with empty container name."""
        config = JobConfig(
            job_name="test-job",
            walltime="01:00:00",
            partition="gpu"
        )
        config.container = ContainerConfig(name="")
        
        errors = validate_config(config)
        assert "container name cannot be empty if specified" in errors


class TestPythonWrapper:
    """Tests for Python script wrapper functionality."""

    def test_create_python_wrapper_without_app_config(self):
        """Test creating wrapper without app config."""
        wrapper = create_python_wrapper("script.py")
        
        assert callable(wrapper)
        # The wrapper function would execute subprocess.run in real scenario

    def test_create_python_wrapper_with_app_config(self):
        """Test creating wrapper with app config."""
        wrapper = create_python_wrapper("script.py", "config.yaml")
        
        assert callable(wrapper)
        # The wrapper would set APP_CONFIG_PATH environment variable


class TestSubmissionModeDetection:
    """Tests for submission mode detection."""

    def test_determine_submission_mode_cli_command(self):
        """Test CLI command detection."""
        config = JobConfig(num_nodes=1)
        command = ["llamafactory-cli", "train"]
        
        mode = determine_submission_mode(config, command)
        assert mode == "cli"

    def test_determine_submission_mode_single_node_python(self):
        """Test single-node Python script detection."""
        config = JobConfig(num_nodes=1)
        command = ["train.py"]
        
        mode = determine_submission_mode(config, command)
        assert mode == "function"

    def test_determine_submission_mode_distributed_python(self):
        """Test distributed Python script detection."""
        config = JobConfig(num_nodes=4)
        command = ["train.py"]
        
        mode = determine_submission_mode(config, command)
        assert mode == "distributed"

    def test_determine_submission_mode_distributed_cli(self):
        """Test distributed CLI command (should still be CLI)."""
        config = JobConfig(num_nodes=4)
        command = ["python", "-m", "torch.distributed.launch"]
        
        mode = determine_submission_mode(config, command)
        assert mode == "cli"


class TestCLICommands:
    """Tests for CLI command functions."""

    @patch('aihpi.cli.load_config')
    @patch('aihpi.cli.SlurmJobExecutor')
    @patch('pathlib.Path.exists')
    def test_cmd_run_single_node_success(self, mock_exists, mock_executor_class, mock_load_config):
        """Test successful single-node job submission."""
        # Setup mocks
        mock_config = JobConfig(
            job_name="test-job",
            num_nodes=1,
            walltime="01:00:00",
            partition="gpu"
        )
        mock_load_config.return_value = mock_config
        mock_exists.return_value = True
        
        mock_executor = Mock()
        mock_job = Mock()
        mock_job.job_id = "12345"
        mock_job.paths.stdout = "/path/to/stdout"
        mock_executor.submit_function.return_value = mock_job
        mock_executor_class.return_value = mock_executor
        
        # Setup args
        args = Namespace(
            config="test_config.py",
            command=["train.py"],
            app_config=None,
            monitor=False,
            debug=False
        )
        
        result = cmd_run(args)
        
        assert result == 0
        mock_load_config.assert_called_once_with("test_config.py")
        mock_executor.submit_function.assert_called_once()

    @patch('aihpi.cli.load_config')
    @patch('aihpi.cli.SlurmJobExecutor')
    def test_cmd_run_distributed_success(self, mock_executor_class, mock_load_config):
        """Test successful distributed job submission."""
        # Setup mocks
        mock_config = JobConfig(
            job_name="test-job",
            num_nodes=4,
            walltime="02:00:00",
            partition="gpu"
        )
        mock_load_config.return_value = mock_config
        
        mock_executor = Mock()
        mock_job = Mock()
        mock_job.job_id = "67890"
        mock_job.paths.stdout = "/path/to/stdout"
        mock_executor.submit_distributed_training.return_value = mock_job
        mock_executor_class.return_value = mock_executor
        
        # Setup args
        args = Namespace(
            config="distributed_config.py",
            command=["train.py"],
            app_config=None,
            monitor=False,
            debug=False
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            result = cmd_run(args)
        
        assert result == 0
        mock_executor.submit_distributed_training.assert_called_once()

    @patch('aihpi.cli.load_config')
    @patch('aihpi.cli.SlurmJobExecutor')
    def test_cmd_run_cli_success(self, mock_executor_class, mock_load_config):
        """Test successful CLI job submission."""
        mock_config = JobConfig(
            job_name="cli-job",
            num_nodes=2,
            walltime="04:00:00",
            partition="gpu"
        )
        mock_load_config.return_value = mock_config
        
        mock_executor = Mock()
        mock_job = Mock()
        mock_job.job_id = "cli-123"
        mock_job.paths.stdout = "/path/to/stdout"
        mock_executor.submit_cli_training.return_value = mock_job
        mock_executor_class.return_value = mock_executor
        
        args = Namespace(
            config="cli_config.py",
            command=["llamafactory-cli", "train"],
            app_config="train.yaml",
            monitor=False,
            debug=False
        )
        
        result = cmd_run(args)
        
        assert result == 0
        mock_executor.submit_cli_training.assert_called_once_with(
            ["llamafactory-cli", "train"],
            config_path="train.yaml"
        )

    @patch('aihpi.cli.load_config')
    def test_cmd_run_config_validation_error(self, mock_load_config):
        """Test job submission with config validation error."""
        mock_config = JobConfig(
            job_name="",  # Invalid empty job name
            walltime="invalid",  # Invalid walltime
            partition="gpu"
        )
        mock_load_config.return_value = mock_config
        
        args = Namespace(
            config="invalid_config.py",
            command=["train.py"],
            app_config=None,
            monitor=False,
            debug=False
        )
        
        result = cmd_run(args)
        assert result == 1  # Should return error code

    def test_cmd_run_config_file_not_found(self):
        """Test job submission with missing config file."""
        args = Namespace(
            config="nonexistent_config.py",
            command=["train.py"],
            app_config=None,
            monitor=False,
            debug=False
        )
        
        result = cmd_run(args)
        assert result == 1  # Should return error code

    @patch('aihpi.cli.JobMonitor')
    def test_cmd_monitor_success(self, mock_monitor_class):
        """Test successful job monitoring."""
        mock_monitor = Mock()
        mock_status = JobStatus(
            job_id="12345",
            name="test-job",
            state="RUNNING",
            partition="gpu",
            nodes=1,
            cpus=4,
            time_limit="01:00:00",
            time_elapsed="00:15:30"
        )
        mock_monitor.get_job_status.return_value = mock_status
        mock_monitor_class.return_value = mock_monitor
        
        args = Namespace(
            job_id="12345",
            login_node=None,
            logs=False,
            follow=False
        )
        
        result = cmd_monitor(args)
        
        assert result == 0
        mock_monitor.get_job_status.assert_called_once_with("12345")

    @patch('aihpi.cli.JobMonitor')
    def test_cmd_monitor_job_not_found(self, mock_monitor_class):
        """Test monitoring non-existent job."""
        mock_monitor = Mock()
        mock_monitor.get_job_status.return_value = None
        mock_monitor_class.return_value = mock_monitor
        
        args = Namespace(
            job_id="nonexistent",
            login_node=None,
            logs=False,
            follow=False
        )
        
        result = cmd_monitor(args)
        assert result == 1  # Should return error code

    @patch('aihpi.cli.JobMonitor')
    def test_cmd_status_success(self, mock_monitor_class):
        """Test successful status command."""
        mock_monitor = Mock()
        mock_jobs = [
            JobStatus("12345", "job1", "RUNNING", "gpu", 1, 4, "01:00:00", "00:15:30"),
            JobStatus("12346", "job2", "PENDING", "cpu", 2, 8, "02:00:00", "00:00:00")
        ]
        mock_monitor.get_user_jobs.return_value = mock_jobs
        mock_monitor_class.return_value = mock_monitor
        
        args = Namespace(
            user=None,
            login_node=None
        )
        
        result = cmd_status(args)
        
        assert result == 0
        mock_monitor.get_user_jobs.assert_called_once_with(user=None)

    @patch('aihpi.cli.JobMonitor')
    def test_cmd_cancel_success(self, mock_monitor_class):
        """Test successful job cancellation."""
        mock_monitor = Mock()
        mock_monitor.cancel_job.return_value = True
        mock_monitor_class.return_value = mock_monitor
        
        args = Namespace(
            job_id="12345",
            login_node=None
        )
        
        result = cmd_cancel(args)
        
        assert result == 0
        mock_monitor.cancel_job.assert_called_once_with("12345")

    @patch('aihpi.cli.JobMonitor')
    def test_cmd_cancel_failure(self, mock_monitor_class):
        """Test failed job cancellation."""
        mock_monitor = Mock()
        mock_monitor.cancel_job.return_value = False
        mock_monitor_class.return_value = mock_monitor
        
        args = Namespace(
            job_id="12345",
            login_node=None
        )
        
        result = cmd_cancel(args)
        assert result == 1  # Should return error code


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @patch('sys.argv')
    @patch('aihpi.cli.load_config')
    @patch('aihpi.cli.SlurmJobExecutor')
    @patch('pathlib.Path.exists')
    def test_main_run_command(self, mock_exists, mock_executor_class, mock_load_config, mock_argv):
        """Test main function with run command."""
        mock_argv.__getitem__.side_effect = lambda i: [
            'aihpi', 'run', 'train.py', '--config', 'test_config.py'
        ][i]
        mock_argv.__len__.return_value = 5
        
        mock_config = JobConfig(
            job_name="test-job",
            num_nodes=1,
            walltime="01:00:00",
            partition="gpu"
        )
        mock_load_config.return_value = mock_config
        mock_exists.return_value = True
        
        mock_executor = Mock()
        mock_job = Mock()
        mock_job.job_id = "12345"
        mock_job.paths.stdout = "/path/to/stdout"
        mock_executor.submit_function.return_value = mock_job
        mock_executor_class.return_value = mock_executor
        
        with patch('sys.argv', ['aihpi', 'run', 'train.py', '--config', 'test_config.py']):
            result = main()
        
        assert result == 0

    def test_main_no_command(self):
        """Test main function with no command."""
        with patch('sys.argv', ['aihpi']):
            result = main()
        
        assert result == 1  # Should return error code

    @patch('sys.argv')
    def test_main_help_command(self, mock_argv):
        """Test main function with help command."""
        with patch('sys.argv', ['aihpi', '--help']):
            with pytest.raises(SystemExit):  # argparse exits on help
                main()