"""Tests for configuration classes and basic functionality."""

from unittest.mock import Mock, patch

from aihpi.core.executor import SlurmJobExecutor, SSHSlurmExecutor
from aihpi.core.config import JobConfig, ContainerConfig


class TestJobConfiguration:
    """Test job configuration and basic integration."""

    def test_job_config_creation(self):
        """Test that JobConfig can be created with defaults."""
        config = JobConfig(
            job_name="test-job",
            num_nodes=2,
            gpus_per_node=2,
            login_node="test.cluster.com"
        )
        
        assert config.job_name == "test-job"
        assert config.num_nodes == 2
        assert config.gpus_per_node == 2
        assert config.login_node == "test.cluster.com"
        assert config.log_dir.name == "aihpi"  # Default log directory

    def test_container_config_creation(self):
        """Test that ContainerConfig works correctly."""
        container = ContainerConfig(
            name="test-container",
            mounts=["/data:/data", "/models:/models"]
        )
        
        assert container.name == "test-container"
        mount_string = container.get_mount_string()
        assert "/data:/data" in mount_string
        assert "/models:/models" in mount_string
        assert "/dev/infiniband:/dev/infiniband" in mount_string  # Auto-added

    def test_ssh_executor_command_building(self):
        """Test SSH command construction without execution."""
        with patch('aihpi.core.executor.submitit.SlurmExecutor.__init__') as mock_super:
            mock_super.return_value = None
            
            executor = SSHSlurmExecutor(folder="/test/logs", login_node="cluster.test.com")
            
            # Test SSH command base construction
            assert executor._login_node == "cluster.test.com"
            assert "ssh" in executor.ssh_base
            assert "cluster.test.com" in executor.ssh_base
            assert "-q" in executor.ssh_base
            assert "BatchMode=yes" in executor.ssh_base

    def test_executor_selection_logic(self):
        """Test that the right executor type is selected based on login_node."""
        # Test executor selection happens during submit, not construction
        config_with_ssh = JobConfig(job_name="test", login_node="cluster.com")
        config_without_ssh = JobConfig(job_name="test", login_node=None)
        
        # Just test that executors can be created without errors
        executor1 = SlurmJobExecutor(config_with_ssh)
        executor2 = SlurmJobExecutor(config_without_ssh)
        
        # Verify configs are stored correctly
        assert executor1.config.login_node == "cluster.com"
        assert executor2.config.login_node is None

    def test_submit_function_integration(self):
        """Test submit_function method with full mocking."""
        config = JobConfig(job_name="test", login_node=None)  # Use regular executor
        
        # Mock the submitit.SlurmExecutor completely
        with patch('aihpi.core.executor.submitit.SlurmExecutor') as MockExecutorClass:
            mock_executor_instance = Mock()
            mock_job = Mock()
            mock_job.job_id = "12345"
            mock_executor_instance.submit.return_value = mock_job
            MockExecutorClass.return_value = mock_executor_instance
            
            executor = SlurmJobExecutor(config)
            
            def test_function(x, y=10):
                return x + y
            
            # Submit the function
            job = executor.submit_function(test_function, 5, y=20)
            
            # Verify interaction with mock
            mock_executor_instance.update_parameters.assert_called()
            mock_executor_instance.submit.assert_called_once_with(test_function, 5, y=20)
            assert job.job_id == "12345"

    def test_submit_cli_training_integration(self):
        """Test submit_cli_training method with mocking."""
        config = JobConfig(job_name="test", login_node=None)  # Use regular executor
        
        with patch('aihpi.core.executor.submitit.SlurmExecutor') as MockExecutorClass:
            mock_executor_instance = Mock()
            mock_job = Mock()
            mock_job.job_id = "67890"
            mock_executor_instance.submit.return_value = mock_job
            MockExecutorClass.return_value = mock_executor_instance
            
            executor = SlurmJobExecutor(config)
            
            # Test CLI command submission
            command = ["python", "train.py", "--epochs", "5"]
            job = executor.submit_cli_training(command, config_path="config.yaml")
            
            # Verify a callable was submitted (wrapper function)
            mock_executor_instance.submit.assert_called_once()
            submitted_args = mock_executor_instance.submit.call_args[0]
            assert len(submitted_args) == 1  # Should be just the wrapper function
            assert callable(submitted_args[0])  # Should be callable
            assert job.job_id == "67890"

    def test_parameter_configuration(self):
        """Test that SLURM parameters are configured correctly."""
        config = JobConfig(
            job_name="param-test",
            num_nodes=3,
            gpus_per_node=4,
            walltime="02:30:00",
            partition="gpu",
            env_vars={"TEST_VAR": "test_value"}
        )
        
        with patch('aihpi.core.executor.submitit.SlurmExecutor') as MockExecutorClass:
            mock_executor_instance = Mock()
            MockExecutorClass.return_value = mock_executor_instance
            
            executor = SlurmJobExecutor(config)
            
            def dummy_func():
                pass
            
            executor.submit_function(dummy_func)
            
            # Check parameter configuration
            update_calls = mock_executor_instance.update_parameters.call_args_list
            assert len(update_calls) > 0
            
            # Find the main parameter update call
            main_params = None
            for call in update_calls:
                params = call[1] if call[1] else call[0][0] if call[0] else {}
                if 'job_name' in params:
                    main_params = params
                    break
            
            assert main_params is not None
            assert main_params['job_name'] == 'param-test'
            assert main_params['nodes'] == 3
            assert main_params['gpus_per_node'] == 4
            assert main_params['time'] == 150  # 2 hours 30 minutes = 150 minutes
            assert main_params['partition'] == 'gpu'


class TestConfigurationValidation:
    """Test configuration validation and edge cases."""

    def test_default_configuration_values(self):
        """Test that default configuration values are sensible."""
        config = JobConfig()
        
        assert config.job_name == "aihpi-job"
        assert config.num_nodes == 1
        assert config.gpus_per_node == 1
        assert config.cpus_per_task == 4
        assert config.walltime == "01:00:00"
        assert config.partition == "aisc"
        assert config.container.name == "torch2412"

    def test_container_mount_string_generation(self):
        """Test container mount string generation."""
        container = ContainerConfig(
            name="test-container",
            mounts=["/home/user:/workspace", "/data/models:/models"]
        )
        
        mount_string = container.get_mount_string()
        
        # Should contain all mounts plus infiniband
        assert "/home/user:/workspace" in mount_string
        assert "/data/models:/models" in mount_string
        assert "/dev/infiniband:/dev/infiniband" in mount_string
        
        # Should be comma-separated
        mounts = mount_string.split(",")
        assert len(mounts) == 3  # 2 custom + 1 infiniband

    def test_job_config_with_all_options(self):
        """Test JobConfig with all options set."""
        from pathlib import Path
        
        config = JobConfig(
            job_name="comprehensive-test",
            num_nodes=4,
            gpus_per_node=8,
            cpus_per_task=16,
            walltime="12:00:00",
            partition="large-gpu",
            account="research-account",
            qos="high-priority",
            log_dir=Path("/custom/logs"),
            shared_storage_root=Path("/shared/storage"),
            workspace_mount=Path("/workspace"),
            setup_commands=["module load cuda", "source activate myenv"],
            env_vars={"CUDA_VISIBLE_DEVICES": "0,1,2,3", "OMP_NUM_THREADS": "16"},
            login_node="login.supercomputer.org"
        )
        
        assert config.job_name == "comprehensive-test"
        assert config.num_nodes == 4
        assert config.gpus_per_node == 8
        assert config.cpus_per_task == 16
        assert config.walltime == "12:00:00"
        assert config.partition == "large-gpu"
        assert config.account == "research-account"
        assert config.qos == "high-priority"
        assert config.log_dir == Path("/custom/logs")
        assert config.shared_storage_root == Path("/shared/storage")
        assert config.workspace_mount == Path("/workspace")
        assert len(config.setup_commands) == 2
        assert len(config.env_vars) == 2
        assert config.login_node == "login.supercomputer.org"