"""Integration tests for job submission, monitoring, and experiment tracking."""

from unittest.mock import Mock, patch, call
import pytest
import tempfile
import json
from pathlib import Path

from aihpi.core.executor import SlurmJobExecutor
from aihpi.core.config import JobConfig, ContainerConfig
from aihpi.monitoring.monitoring import JobMonitor, JobManager, JobStatus
from aihpi.tracking.tracking import LocalTracker, ExperimentManager, create_tracker


class TestJobSubmissionWithMonitoring:
    """Test integration of job submission with monitoring."""

    @patch('aihpi.core.executor.SSHSlurmExecutor')
    @patch.object(JobMonitor, '_run_command')
    def test_submit_and_monitor_workflow(self, mock_monitor_command, mock_ssh_executor):
        """Test complete workflow: submit job and monitor until completion."""
        # Setup mocks for job submission
        mock_executor_instance = Mock()
        mock_job = Mock()
        mock_job.job_id = "test-12345"
        mock_job.paths.stdout = "/path/to/stdout.log"
        mock_job.paths.stderr = "/path/to/stderr.log"
        mock_executor_instance.submit.return_value = mock_job
        mock_ssh_executor.return_value = mock_executor_instance
        
        # Setup mocks for monitoring
        monitor_responses = [
            "test-12345,test-job,PENDING,gpu,1,4,01:00:00,00:00:00,,,",  # Initial status
            "test-12345,test-job,RUNNING,gpu,1,4,01:00:00,00:15:30,,,",  # Running
            "",  # Job completed, not in squeue
        ]
        
        # Setup completed job response from sacct
        completed_response = "test-12345|test-job|COMPLETED|gpu|1|4|01:00:00|00:45:20|2024-01-01T10:00:00|2024-01-01T10:45:20|0:0"
        
        mock_monitor_command.side_effect = monitor_responses + [completed_response]
        
        # Create job config and executor
        config = JobConfig(
            job_name="integration-test",
            num_nodes=1,
            gpus_per_node=1,
            walltime="01:00:00",
            partition="gpu",
            login_node="test.cluster.com"
        )
        
        executor = SlurmJobExecutor(config)
        monitor = JobMonitor(login_node="test.cluster.com")
        manager = JobManager(monitor)
        
        # Define test function
        def test_training_function():
            return "Training completed"
        
        # Submit job
        job = manager.submit_and_monitor(executor, test_training_function)
        
        # Verify job submission
        assert job.job_id == "test-12345"
        mock_executor_instance.submit.assert_called_once()
        
        # Monitor job progression
        statuses = []
        for i in range(3):
            status = monitor.get_job_status("test-12345")
            if status:
                statuses.append(status.state)
        
        # Should show progression: PENDING -> RUNNING -> COMPLETED
        assert len(statuses) == 3
        assert statuses[0] == "PENDING"
        assert statuses[1] == "RUNNING"
        assert statuses[2] == "COMPLETED"

    @patch('aihpi.core.executor.submitit.SlurmExecutor')
    @patch.object(JobMonitor, '_run_command')
    def test_distributed_job_monitoring(self, mock_monitor_command, mock_regular_executor):
        """Test monitoring distributed training jobs."""
        # Setup job submission mock
        mock_executor_instance = Mock()
        mock_job = Mock()
        mock_job.job_id = "distributed-67890"
        mock_executor_instance.submit.return_value = mock_job
        mock_regular_executor.return_value = mock_executor_instance
        
        # Setup monitoring responses for distributed job
        mock_monitor_command.return_value = "distributed-67890,distributed-training,RUNNING,gpu,2,8,02:00:00,00:30:45,,,"
        
        # Create config for distributed job
        config = JobConfig(
            job_name="distributed-training",
            num_nodes=2,
            gpus_per_node=4,
            walltime="02:00:00",
            partition="gpu",
            login_node=None  # Local execution
        )
        
        executor = SlurmJobExecutor(config)
        monitor = JobMonitor()  # Local monitoring
        
        def distributed_training_func():
            import os
            print(f"Running on node rank: {os.getenv('NODE_RANK', '0')}")
            return "Distributed training completed"
        
        # Submit distributed job
        job = executor.submit_distributed_training(distributed_training_func)
        
        # Monitor the job
        status = monitor.get_job_status(job.job_id)
        
        assert status is not None
        assert status.job_id == "distributed-67890"
        assert status.state == "RUNNING"
        assert status.nodes == 2
        assert status.cpus == 8

    @patch.object(JobMonitor, '_run_command')
    def test_job_cancellation_integration(self, mock_monitor_command):
        """Test job cancellation through monitoring."""
        # Setup monitoring responses
        mock_monitor_command.side_effect = [
            "cancel-12345,cancel-test,RUNNING,gpu,1,4,01:00:00,00:10:15,,,",  # Before cancel
            "",  # After cancel - scancel command
            "cancel-12345|cancel-test|CANCELLED|gpu|1|4|01:00:00|00:10:30|2024-01-01T10:00:00|2024-01-01T10:10:30|15"  # From sacct
        ]
        
        monitor = JobMonitor()
        
        # Check initial status
        status = monitor.get_job_status("cancel-12345")
        assert status.state == "RUNNING"
        
        # Cancel the job
        success = monitor.cancel_job("cancel-12345")
        assert success is True
        
        # Check final status
        final_status = monitor.get_job_status("cancel-12345")
        assert final_status.state == "CANCELLED"


class TestJobSubmissionWithTracking:
    """Test integration of job submission with experiment tracking."""

    @patch('aihpi.core.executor.submitit.SlurmExecutor')
    def test_local_tracking_integration(self, mock_regular_executor):
        """Test job submission with local experiment tracking."""
        # Setup job submission
        mock_executor_instance = Mock()
        mock_job = Mock()
        mock_job.job_id = "tracking-12345"
        mock_executor_instance.submit.return_value = mock_job
        mock_regular_executor.return_value = mock_executor_instance
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create local tracker and experiment manager
            tracker = LocalTracker(log_dir=tmp_dir)
            exp_manager = ExperimentManager(tracker)
            
            # Create job config
            config = JobConfig(
                job_name="tracked-training",
                num_nodes=1,
                gpus_per_node=1,
                walltime="01:00:00",
                partition="gpu",
                login_node=None
            )
            
            executor = SlurmJobExecutor(config)
            
            def training_with_tracking():
                # Start experiment tracking
                run_id = exp_manager.start_experiment("integration-test", {
                    "model": "test-model",
                    "batch_size": 32,
                    "learning_rate": 0.001
                })
                
                # Simulate training loop with metrics
                for epoch in range(3):
                    loss = 1.0 - (epoch * 0.2)
                    accuracy = 0.5 + (epoch * 0.15)
                    
                    exp_manager.log_training_metrics(
                        epoch=epoch,
                        loss=loss,
                        accuracy=accuracy
                    )
                
                exp_manager.finish_experiment("completed")
                return f"Training completed: {run_id}"
            
            # Submit job with tracking
            job = executor.submit_function(training_with_tracking)
            
            # Verify job submission
            assert job.job_id == "tracking-12345"
            mock_executor_instance.submit.assert_called_once()
            
            # The tracking functionality would be tested by actually calling the function
            # Here we just verify the integration setup is correct
            assert exp_manager.tracker == tracker
            assert tracker.log_dir == Path(tmp_dir)

    @patch('aihpi.tracking.tracking.wandb')
    @patch('aihpi.core.executor.SSHSlurmExecutor')
    @patch.dict('os.environ', {"SLURM_JOB_ID": "wandb-12345", "WORLD_SIZE": "2", "NODE_RANK": "0"})
    def test_wandb_tracking_integration(self, mock_ssh_executor, mock_wandb):
        """Test job submission with WandB experiment tracking."""
        # Setup WandB mocks
        mock_run = Mock()
        mock_run.id = "wandb-run-abc123"
        mock_wandb.init.return_value = mock_run
        
        # Setup job submission
        mock_executor_instance = Mock()
        mock_job = Mock()
        mock_job.job_id = "wandb-12345"
        mock_executor_instance.submit.return_value = mock_job
        mock_ssh_executor.return_value = mock_executor_instance
        
        # Create WandB tracker
        tracker = create_tracker("wandb", project="integration-test", entity="test-team")
        exp_manager = ExperimentManager(tracker)
        
        # Create job config with environment variables for WandB
        config = JobConfig(
            job_name="wandb-training",
            num_nodes=2,
            gpus_per_node=1,
            walltime="02:00:00",
            partition="gpu",
            login_node="test.cluster.com",
            env_vars={
                "WANDB_PROJECT": "integration-test",
                "WANDB_ENTITY": "test-team"
            }
        )
        
        executor = SlurmJobExecutor(config)
        
        def distributed_training_with_wandb():
            # This would be the actual training function
            run_id = exp_manager.start_experiment("distributed-training", {
                "nodes": 2,
                "gpus_per_node": 1,
                "model": "transformer"
            })
            
            # Simulate distributed training
            for step in range(5):
                exp_manager.log_training_metrics(
                    step=step,
                    loss=2.0 - (step * 0.3),
                    throughput=100 + step * 10
                )
            
            exp_manager.finish_experiment("completed")
            return run_id
        
        # Submit distributed job with WandB tracking
        job = executor.submit_distributed_training(distributed_training_with_wandb)
        
        # Verify job submission
        assert job.job_id == "wandb-12345"
        
        # Verify WandB integration setup
        assert isinstance(tracker, type(create_tracker("wandb", project="test")))
        assert tracker.project == "integration-test"
        assert tracker.entity == "test-team"


class TestComprehensiveIntegration:
    """Test comprehensive integration of all components."""

    @patch('aihpi.core.executor.SSHSlurmExecutor')
    @patch.object(JobMonitor, '_run_command')
    @patch('time.sleep')  # Speed up wait_for_job
    def test_end_to_end_workflow(self, mock_sleep, mock_monitor_command, mock_ssh_executor):
        """Test end-to-end workflow: submit, track, monitor, and complete."""
        # Setup job submission
        mock_executor_instance = Mock()
        mock_job = Mock()
        mock_job.job_id = "e2e-12345"
        mock_job.paths.stdout = "/logs/e2e-12345.out"
        mock_job.paths.stderr = "/logs/e2e-12345.err"
        mock_executor_instance.submit.return_value = mock_job
        mock_ssh_executor.return_value = mock_executor_instance
        
        # Setup monitoring progression
        monitor_responses = [
            "e2e-12345,e2e-test,PENDING,gpu,1,4,01:00:00,00:00:00,,,",  # Pending
            "e2e-12345,e2e-test,RUNNING,gpu,1,4,01:00:00,00:30:15,,,",  # Running
            "",  # Completed, check sacct
            "e2e-12345|e2e-test|COMPLETED|gpu|1|4|01:00:00|00:45:30|2024-01-01T10:00:00|2024-01-01T10:45:30|0:0",  # sacct
            "e2e-12345|2048K|4096K|75%|00:40:00|00:45:30|8G"  # Resource usage
        ]
        mock_monitor_command.side_effect = monitor_responses
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup all components
            config = JobConfig(
                job_name="e2e-test",
                num_nodes=1,
                gpus_per_node=4,
                walltime="01:00:00",
                partition="gpu",
                login_node="cluster.test.com",
                env_vars={"EXPERIMENT_NAME": "e2e-integration"}
            )
            
            executor = SlurmJobExecutor(config)
            monitor = JobMonitor(login_node="cluster.test.com")
            manager = JobManager(monitor)
            
            tracker = LocalTracker(log_dir=tmp_dir)
            exp_manager = ExperimentManager(tracker)
            
            def comprehensive_training():
                # Start experiment tracking
                run_id = exp_manager.start_experiment("e2e-integration", {
                    "model": "large-transformer",
                    "dataset": "custom-data",
                    "batch_size": 64,
                    "learning_rate": 2e-5,
                    "num_epochs": 10
                })
                
                # Simulate training with metrics
                for epoch in range(3):
                    loss = 3.0 * (0.8 ** epoch)
                    accuracy = min(0.95, 0.4 + epoch * 0.2)
                    perplexity = 2 ** loss
                    
                    exp_manager.log_training_metrics(
                        epoch=epoch,
                        train_loss=loss,
                        accuracy=accuracy,
                        perplexity=perplexity,
                        learning_rate=2e-5 * (0.9 ** epoch)
                    )
                    
                    # Log checkpoint every 2 epochs
                    if epoch % 2 == 0:
                        checkpoint_dir = Path(tmp_dir) / f"checkpoint_epoch_{epoch}"
                        checkpoint_dir.mkdir(exist_ok=True)
                        (checkpoint_dir / "model.pt").write_text("model checkpoint")
                        (checkpoint_dir / "optimizer.pt").write_text("optimizer state")
                        exp_manager.log_model_checkpoint(checkpoint_dir)
                
                exp_manager.finish_experiment("completed")
                return f"E2E training completed: {run_id}"
            
            # 1. Submit job with monitoring
            job = manager.submit_and_monitor(executor, comprehensive_training)
            
            # 2. Monitor job progression
            initial_status = monitor.get_job_status(job.job_id)
            assert initial_status.state == "PENDING"
            
            running_status = monitor.get_job_status(job.job_id)
            assert running_status.state == "RUNNING"
            
            # 3. Wait for completion (mocked to be fast)
            final_status = monitor.get_job_status(job.job_id)
            assert final_status.state == "COMPLETED"
            
            # 4. Get resource usage
            usage = manager.get_resource_usage(job.job_id)
            assert usage['max_rss'] == "2048K"
            assert usage['avg_cpu'] == "75%"
            
            # 5. Verify experiment tracking artifacts
            experiments_dir = Path(tmp_dir)
            experiment_dirs = list(experiments_dir.glob("e2e-integration_*"))
            assert len(experiment_dirs) >= 1
            
            # Check metadata was saved
            metadata_files = list(experiments_dir.glob("*/metadata.json"))
            assert len(metadata_files) >= 1
            
            with open(metadata_files[0]) as f:
                metadata = json.load(f)
            
            assert metadata['experiment_name'] == "e2e-integration"
            assert metadata['status'] == "completed"
            assert 'model' in metadata['params']
            assert metadata['params']['model'] == "large-transformer"
            
            # Check metrics were logged
            metrics_files = list(experiments_dir.glob("*/metrics.jsonl"))
            assert len(metrics_files) >= 1
            
            with open(metrics_files[0]) as f:
                metrics_lines = f.readlines()
            
            assert len(metrics_lines) == 3  # 3 epochs
            
            # Check checkpoints were saved
            checkpoint_dirs = list(experiments_dir.glob("*/artifacts/checkpoint_*"))
            assert len(checkpoint_dirs) >= 1

    @patch('aihpi.core.executor.submitit.SlurmExecutor')
    def test_cli_training_with_tracking(self, mock_regular_executor):
        """Test CLI training integration with experiment tracking."""
        # Setup job submission
        mock_executor_instance = Mock()
        mock_job = Mock()
        mock_job.job_id = "cli-track-12345"
        mock_executor_instance.submit.return_value = mock_job
        mock_regular_executor.return_value = mock_executor_instance
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup tracking
            tracker = LocalTracker(log_dir=tmp_dir)
            exp_manager = ExperimentManager(tracker)
            
            # Create container config for LlamaFactory
            config = JobConfig(
                job_name="cli-llamafactory",
                num_nodes=1,
                gpus_per_node=2,
                walltime="04:00:00",
                partition="gpu",
                workspace_mount=Path("/workspace"),
                setup_commands=["uv sync --extra torch --extra metrics"],
                env_vars={
                    "EXPERIMENT_NAME": "llamafactory-lora",
                    "TRACKER_LOG_DIR": tmp_dir
                },
                login_node=None
            )
            
            config.container = ContainerConfig(name="llama-factory")
            config.container.mounts.append("/workspace:/workspace")
            
            executor = SlurmJobExecutor(config)
            
            # Submit LlamaFactory training with UV
            command = ["uv", "run", "--prerelease=allow", "llamafactory-cli", "train"]
            config_path = "examples/train_lora/llama3_lora_sft.yaml"
            
            job = executor.submit_cli_training(command, config_path=config_path)
            
            # Verify job submission
            assert job.job_id == "cli-track-12345"
            mock_executor_instance.submit.assert_called_once()
            
            # Verify config path was set as environment variable
            update_calls = mock_executor_instance.update_parameters.call_args_list
            env_found = False
            for call_obj in update_calls:
                if 'env' in call_obj.kwargs and 'CONFIG_PATH' in call_obj.kwargs['env']:
                    env_found = True
                    assert call_obj.kwargs['env']['CONFIG_PATH'] == config_path
                    break
            
            # The CLI command would handle its own tracking, but we verify the setup
            assert exp_manager.tracker == tracker

    @patch.object(JobMonitor, '_run_command')
    def test_error_handling_integration(self, mock_monitor_command):
        """Test error handling across integrated components."""
        # Test network failure in monitoring
        mock_monitor_command.side_effect = RuntimeError("SSH connection failed")
        
        monitor = JobMonitor(login_node="unreachable.cluster.com")
        
        # Should handle errors gracefully
        status = monitor.get_job_status("12345")
        assert status is None
        
        jobs = monitor.get_user_jobs()
        assert jobs == []
        
        cancel_result = monitor.cancel_job("12345")
        assert cancel_result is False
        
        # Test with JobManager
        manager = JobManager(monitor)
        usage = manager.get_resource_usage("12345")
        assert usage == {}
        
        running_jobs = manager.list_running_jobs()
        assert running_jobs == []