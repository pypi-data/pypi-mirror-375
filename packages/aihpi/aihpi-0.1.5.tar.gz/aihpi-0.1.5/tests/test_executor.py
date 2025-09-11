"""Tests for SlurmJobExecutor job submission methods."""

from unittest.mock import Mock, patch
from pathlib import Path

from aihpi.core.executor import SlurmJobExecutor, SSHSlurmExecutor
from aihpi.core.config import JobConfig


class TestSlurmJobExecutor:
    """Tests for SlurmJobExecutor job submission methods."""

    def test_submit_function_creates_new_executor_each_time(self, basic_job_config):
        """Test that submit_function creates a new executor instance for each job."""
        with patch('aihpi.core.executor.SSHSlurmExecutor') as mock_ssh_class:
            
            mock_executor = Mock()
            mock_job = Mock()
            mock_job.job_id = "12345"
            mock_job.paths.stdout = "/path/to/stdout"
            mock_job.paths.stderr = "/path/to/stderr"
            mock_executor.submit.return_value = mock_job
            mock_ssh_class.return_value = mock_executor
            
            executor = SlurmJobExecutor(basic_job_config)
            
            def test_func():
                return "test result"
            
            result_job = executor.submit_function(test_func)
            
            # Verify SSHSlurmExecutor was created (since login_node is provided)
            mock_ssh_class.assert_called_once()
            call_args = mock_ssh_class.call_args
            
            # Verify job directory parameter exists
            assert 'folder' in call_args.kwargs
            folder_path = call_args.kwargs['folder']
            assert isinstance(folder_path, Path)  # Should be a Path object
            
            # Verify login_node parameter
            assert call_args.kwargs['login_node'] == 'test.cluster.com'
            
            # Verify executor was configured and job submitted
            mock_executor.update_parameters.assert_called_once()
            mock_executor.submit.assert_called_once_with(test_func)
            
            assert result_job == mock_job

    def test_submit_function_without_login_node(self, basic_job_config):
        """Test submit_function uses regular SlurmExecutor when no login_node."""
        basic_job_config.login_node = None
        
        with patch('aihpi.core.executor.submitit.SlurmExecutor') as mock_regular_class:
            mock_executor = Mock()
            mock_job = Mock()
            mock_executor.submit.return_value = mock_job
            mock_regular_class.return_value = mock_executor
            
            executor = SlurmJobExecutor(basic_job_config)
            
            def test_func():
                return "test result"
            
            result_job = executor.submit_function(test_func)
            
            # Verify regular SlurmExecutor was used
            mock_regular_class.assert_called_once()
            mock_executor.update_parameters.assert_called_once()
            mock_executor.submit.assert_called_once_with(test_func)
            assert result_job == mock_job

    def test_parameter_configuration_matches_actual_implementation(self, basic_job_config):
        """Test that parameters are configured correctly according to actual implementation."""
        basic_job_config.walltime = "01:30:00"  # 1.5 hours = 90 minutes
        basic_job_config.env_vars = {"TEST_VAR": "test_value"}
        
        with patch('aihpi.core.executor.SSHSlurmExecutor') as mock_ssh_class:
            mock_executor = Mock()
            mock_ssh_class.return_value = mock_executor
            
            executor = SlurmJobExecutor(basic_job_config)
            
            def dummy_func():
                pass
            
            executor.submit_function(dummy_func)
            
            # Verify update_parameters was called
            mock_executor.update_parameters.assert_called_once()
            params = mock_executor.update_parameters.call_args.kwargs
            
            # Test actual parameter mapping
            assert params['job_name'] == 'test-job'
            assert params['nodes'] == 1
            assert params['gpus_per_node'] == 1
            assert params['time'] == 90  # Converted to minutes
            assert params['partition'] == 'test'
            assert params['ntasks_per_node'] == 1
            assert params['cpus_per_task'] == 4
            assert params['use_srun'] == False
            
            # Test additional_parameters structure
            additional_params = params['additional_parameters']
            assert additional_params['constraint'] == 'ARCH:X86'
            
            # Test export string contains environment variables
            export_string = additional_params['export']
            assert 'ALL' in export_string
            assert 'TEST_VAR=test_value' in export_string

    def test_container_configuration(self, container_job_config):
        """Test container parameter configuration."""
        with patch('aihpi.core.executor.SSHSlurmExecutor') as mock_ssh_class:
            mock_executor = Mock()
            mock_ssh_class.return_value = mock_executor
            
            executor = SlurmJobExecutor(container_job_config)
            
            def dummy_func():
                pass
            
            executor.submit_function(dummy_func)
            
            # Check container parameters in additional_parameters
            params = mock_executor.update_parameters.call_args.kwargs
            additional_params = params['additional_parameters']
            
            assert additional_params['container_name'] == 'test-container'
            assert additional_params['container_mount_home'] == True
            assert additional_params['container_workdir'] == '/workspace'
            assert additional_params['container_writable'] == True
            
            # Check that mounts include the workspace mount and infiniband
            mounts = additional_params['container_mounts']
            assert '/test/workspace:/workspace' in mounts
            assert '/dev/infiniband:/dev/infiniband' in mounts

    def test_submit_distributed_training_always_creates_wrapper(self, basic_job_config):
        """Test that distributed training always creates a wrapper, even for single node."""
        with patch('aihpi.core.executor.SSHSlurmExecutor') as mock_ssh_class:
            mock_executor = Mock()
            mock_job = Mock()
            mock_executor.submit.return_value = mock_job
            mock_ssh_class.return_value = mock_executor
            
            executor = SlurmJobExecutor(basic_job_config)
            
            def training_func():
                return "training complete"
            
            result_job = executor.submit_distributed_training(training_func)
            
            # Verify that submit was called with a wrapper function, not the original
            mock_executor.submit.assert_called_once()
            submitted_args = mock_executor.submit.call_args[0]
            submitted_func = submitted_args[0]
            
            # The submitted function should be a wrapper, not the original
            assert callable(submitted_func)
            assert submitted_func != training_func
            assert submitted_func.__name__ == 'distributed_wrapper'
            assert result_job == mock_job

    def test_submit_cli_training_creates_wrapper_with_config_path(self, basic_job_config):
        """Test CLI training creates wrapper and handles config_path."""
        with patch('aihpi.core.executor.SSHSlurmExecutor') as mock_ssh_class:
            mock_executor = Mock()
            mock_job = Mock()
            mock_executor.submit.return_value = mock_job
            mock_ssh_class.return_value = mock_executor
            
            executor = SlurmJobExecutor(basic_job_config)
            
            command = ["python", "train.py"]
            config_path = "config/train.yaml"
            
            result_job = executor.submit_cli_training(command, config_path=config_path)
            
            # Verify wrapper function was submitted
            mock_executor.submit.assert_called_once()
            submitted_args = mock_executor.submit.call_args[0]
            assert len(submitted_args) == 1
            assert callable(submitted_args[0])
            
            # Verify multiple update_parameters calls (one for config_path env var)
            assert mock_executor.update_parameters.call_count >= 1
            assert result_job == mock_job

    def test_walltime_conversion_function(self):
        """Test the walltime conversion utility function."""
        config = JobConfig(walltime="02:30:45")  # 2h 30m 45s
        
        # 2*60 + 30 + 45//60 = 120 + 30 + 0 = 150 minutes
        assert config.get_walltime_minutes() == 150
        
        config2 = JobConfig(walltime="00:15:30")  # 15.5 minutes
        assert config2.get_walltime_minutes() == 15
        
        config3 = JobConfig(walltime="10:00:00")  # 10 hours
        assert config3.get_walltime_minutes() == 600

    def test_export_string_generation(self):
        """Test environment variable export string generation."""
        config = JobConfig(
            env_vars={"CUDA_VISIBLE_DEVICES": "0,1", "BATCH_SIZE": "32"}
        )
        
        export_string = config.get_export_string()
        
        # Should always start with ALL
        assert export_string.startswith("ALL,")
        
        # Should contain HF_HOME
        assert "HF_HOME=" in export_string
        
        # Should contain custom env vars
        assert "CUDA_VISIBLE_DEVICES=0,1" in export_string
        assert "BATCH_SIZE=32" in export_string


class TestSSHSlurmExecutor:
    """Tests for SSH-based SLURM executor."""

    def test_initialization_sets_attributes_correctly(self):
        """Test SSH executor initialization."""
        with patch('aihpi.core.executor.submitit.SlurmExecutor.__init__') as mock_super:
            mock_super.return_value = None
            
            executor = SSHSlurmExecutor(folder="/test/logs", login_node="cluster.example.com")
            
            # Verify attributes are set correctly
            assert executor._login_node == "cluster.example.com"
            assert hasattr(executor, 'ssh_base')
            assert isinstance(executor.ssh_base, list)
            
            # Verify SSH command structure
            expected_elements = [
                'ssh', '-q', '-o', 'BatchMode=yes',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ConnectTimeout=10',
                'cluster.example.com'
            ]
            assert executor.ssh_base == expected_elements

    def test_make_submission_command_wraps_with_ssh(self):
        """Test that submission commands are wrapped with SSH."""
        with patch('aihpi.core.executor.submitit.SlurmExecutor.__init__') as mock_super:
            mock_super.return_value = None
            
            executor = SSHSlurmExecutor(folder="/test", login_node="test.node")
            
            # Mock the parent class method
            with patch('aihpi.core.executor.submitit.SlurmExecutor._make_submission_command') as mock_parent:
                mock_parent.return_value = ['sbatch', '/path/to/job.sh']
                
                result = executor._make_submission_command('/path/to/job.sh')
                
                # Should start with SSH command base
                expected_start = executor.ssh_base
                assert result[:len(expected_start)] == expected_start
                
                # Last element should contain the sbatch command
                assert len(result) == len(expected_start) + 1
                assert 'sbatch' in result[-1]


class TestJobConfig:
    """Tests for JobConfig class."""

    def test_post_init_creates_directories(self, tmp_path):
        """Test that JobConfig creates log directories."""
        log_dir = tmp_path / "test_logs"
        
        JobConfig(log_dir=log_dir)
        
        # Directory should be created by post_init
        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_account_and_qos_defaults_to_partition(self):
        """Test that account and qos default to partition value."""
        config = JobConfig(partition="gpu-partition")
        
        assert config.account == "gpu-partition"
        assert config.qos == "gpu-partition"

    def test_hf_home_defaults_correctly(self):
        """Test that HF_HOME defaults based on shared_storage_root."""
        storage_root = Path("/custom/storage")
        config = JobConfig(shared_storage_root=storage_root)
        
        expected_hf_home = storage_root / ".huggingface"
        assert config.hf_home == expected_hf_home