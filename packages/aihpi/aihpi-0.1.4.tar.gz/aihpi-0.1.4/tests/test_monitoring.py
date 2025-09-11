"""Tests for job monitoring functionality."""

from unittest.mock import Mock, patch, call
import pytest
import subprocess
from pathlib import Path

from aihpi.monitoring.monitoring import JobMonitor, JobManager, JobStatus


class TestJobStatus:
    """Tests for JobStatus dataclass."""

    def test_job_status_creation(self):
        """Test JobStatus can be created with required fields."""
        status = JobStatus(
            job_id="12345",
            name="test-job",
            state="RUNNING",
            partition="gpu",
            nodes=2,
            cpus=8,
            time_limit="01:00:00",
            time_elapsed="00:15:30"
        )
        
        assert status.job_id == "12345"
        assert status.name == "test-job"
        assert status.state == "RUNNING"
        assert status.partition == "gpu"
        assert status.nodes == 2
        assert status.cpus == 8
        assert status.time_limit == "01:00:00"
        assert status.time_elapsed == "00:15:30"
        assert status.start_time is None
        assert status.end_time is None
        assert status.exit_code is None

    def test_job_status_with_optional_fields(self):
        """Test JobStatus with optional fields."""
        status = JobStatus(
            job_id="67890",
            name="completed-job",
            state="COMPLETED",
            partition="cpu",
            nodes=1,
            cpus=4,
            time_limit="02:00:00",
            time_elapsed="01:45:20",
            start_time="2024-01-01T10:00:00",
            end_time="2024-01-01T11:45:20",
            exit_code="0"
        )
        
        assert status.start_time == "2024-01-01T10:00:00"
        assert status.end_time == "2024-01-01T11:45:20"
        assert status.exit_code == "0"


class TestJobMonitor:
    """Tests for JobMonitor class."""

    def test_initialization_without_ssh(self):
        """Test JobMonitor initialization without SSH."""
        monitor = JobMonitor()
        
        assert monitor.login_node is None
        assert monitor._ssh_base is None

    def test_initialization_with_ssh(self):
        """Test JobMonitor initialization with SSH."""
        monitor = JobMonitor(login_node="cluster.test.com")
        
        assert monitor.login_node == "cluster.test.com"
        assert monitor._ssh_base is not None
        
        expected_ssh_base = [
            "ssh", "-q",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            "cluster.test.com"
        ]
        assert monitor._ssh_base == expected_ssh_base

    @patch('subprocess.run')
    def test_run_command_local(self, mock_subprocess):
        """Test running command locally (no SSH)."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "command output"
        mock_subprocess.return_value = mock_result
        
        monitor = JobMonitor()
        result = monitor._run_command(["squeue", "-j", "12345"])
        
        mock_subprocess.assert_called_once_with(
            ["squeue", "-j", "12345"],
            capture_output=True,
            text=True
        )
        assert result == "command output"

    @patch('subprocess.run')
    def test_run_command_ssh(self, mock_subprocess):
        """Test running command via SSH."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "ssh command output"
        mock_subprocess.return_value = mock_result
        
        monitor = JobMonitor(login_node="test.cluster.com")
        result = monitor._run_command(["squeue", "-j", "12345"])
        
        expected_cmd = [
            "ssh", "-q", "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
            "test.cluster.com", "squeue -j 12345"
        ]
        mock_subprocess.assert_called_once_with(
            expected_cmd,
            capture_output=True,
            text=True
        )
        assert result == "ssh command output"

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_subprocess):
        """Test command failure handling."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Command failed"
        mock_subprocess.return_value = mock_result
        
        monitor = JobMonitor()
        
        with pytest.raises(RuntimeError, match="Command failed"):
            monitor._run_command(["invalid", "command"])

    @patch.object(JobMonitor, '_run_command')
    def test_get_job_status_running_job(self, mock_run_command):
        """Test getting status of a running job."""
        mock_run_command.return_value = "12345,test-job,RUNNING,gpu,2,8,01:00:00,00:15:30,2024-01-01T10:00:00,,NONE"
        
        monitor = JobMonitor()
        status = monitor.get_job_status("12345")
        
        mock_run_command.assert_called_once_with([
            "squeue", "-j", "12345",
            "--format=%A,%j,%T,%P,%D,%C,%l,%M,%S,%e,%r",
            "--noheader"
        ])
        
        assert status is not None
        assert status.job_id == "12345"
        assert status.name == "test-job"
        assert status.state == "RUNNING"
        assert status.partition == "gpu"
        assert status.nodes == 2
        assert status.cpus == 8
        assert status.time_limit == "01:00:00"
        assert status.time_elapsed == "00:15:30"

    @patch.object(JobMonitor, '_run_command')
    @patch.object(JobMonitor, '_get_completed_job_status')
    def test_get_job_status_completed_job(self, mock_get_completed, mock_run_command):
        """Test getting status of completed job (not in squeue)."""
        mock_run_command.return_value = ""  # Empty response from squeue
        mock_completed_status = JobStatus(
            job_id="12345",
            name="completed-job",
            state="COMPLETED",
            partition="gpu",
            nodes=2,
            cpus=8,
            time_limit="01:00:00",
            time_elapsed="00:45:20"
        )
        mock_get_completed.return_value = mock_completed_status
        
        monitor = JobMonitor()
        status = monitor.get_job_status("12345")
        
        assert status == mock_completed_status
        mock_get_completed.assert_called_once_with("12345")

    @patch.object(JobMonitor, '_run_command')
    def test_get_completed_job_status(self, mock_run_command):
        """Test getting completed job status from sacct."""
        mock_run_command.return_value = "12345|completed-job|COMPLETED|gpu|2|8|01:00:00|00:45:20|2024-01-01T10:00:00|2024-01-01T10:45:20|0:0"
        
        monitor = JobMonitor()
        status = monitor._get_completed_job_status("12345")
        
        mock_run_command.assert_called_once_with([
            "sacct", "-j", "12345",
            "--format=JobID,JobName,State,Partition,NNodes,NCPUS,Timelimit,Elapsed,Start,End,ExitCode",
            "--noheader", "--parsable2"
        ])
        
        assert status is not None
        assert status.job_id == "12345"
        assert status.name == "completed-job"
        assert status.state == "COMPLETED"
        assert status.exit_code == "0:0"

    @patch.object(JobMonitor, '_run_command')
    def test_get_user_jobs(self, mock_run_command):
        """Test getting all jobs for a user."""
        mock_run_command.return_value = (
            "12345,job1,RUNNING,gpu,1,4,01:00:00,00:15:30\n"
            "12346,job2,PENDING,cpu,2,8,02:00:00,00:00:00\n"
            "12347,job3,COMPLETED,gpu,1,4,00:30:00,00:25:45"
        )
        
        monitor = JobMonitor()
        
        with patch('os.getenv', return_value='testuser'):
            jobs = monitor.get_user_jobs()
        
        mock_run_command.assert_called_once_with([
            "squeue", "-u", "testuser",
            "--format=%A,%j,%T,%P,%D,%C,%l,%M",
            "--noheader"
        ])
        
        assert len(jobs) == 3
        assert jobs[0].job_id == "12345"
        assert jobs[0].state == "RUNNING"
        assert jobs[1].job_id == "12346"
        assert jobs[1].state == "PENDING"
        assert jobs[2].job_id == "12347"
        assert jobs[2].state == "COMPLETED"

    @patch.object(JobMonitor, '_run_command')
    def test_cancel_job_success(self, mock_run_command):
        """Test successful job cancellation."""
        mock_run_command.return_value = ""  # scancel typically returns empty on success
        
        monitor = JobMonitor()
        result = monitor.cancel_job("12345")
        
        mock_run_command.assert_called_once_with(["scancel", "12345"])
        assert result is True

    @patch.object(JobMonitor, '_run_command')
    def test_cancel_job_failure(self, mock_run_command):
        """Test job cancellation failure."""
        mock_run_command.side_effect = RuntimeError("Permission denied")
        
        monitor = JobMonitor()
        result = monitor.cancel_job("12345")
        
        assert result is False

    @patch('time.sleep')
    @patch('time.time')
    @patch.object(JobMonitor, 'get_job_status')
    def test_wait_for_job_completion(self, mock_get_status, mock_time, mock_sleep):
        """Test waiting for job completion."""
        # Mock time progression
        mock_time.side_effect = [0, 30, 60, 90]  # 30 second intervals
        
        # Mock job status progression
        running_status = JobStatus("12345", "test", "RUNNING", "gpu", 1, 4, "01:00:00", "00:00:30")
        completed_status = JobStatus("12345", "test", "COMPLETED", "gpu", 1, 4, "01:00:00", "00:02:15")
        
        mock_get_status.side_effect = [running_status, running_status, completed_status]
        
        monitor = JobMonitor()
        final_status = monitor.wait_for_job("12345", poll_interval=30)
        
        assert final_status.state == "COMPLETED"
        assert mock_get_status.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('time.sleep')
    @patch('time.time')
    @patch.object(JobMonitor, 'get_job_status')
    def test_wait_for_job_timeout(self, mock_get_status, mock_time, mock_sleep):
        """Test waiting for job with timeout."""
        # Mock time progression beyond timeout
        mock_time.side_effect = [0, 30, 60, 90, 120, 150]
        
        running_status = JobStatus("12345", "test", "RUNNING", "gpu", 1, 4, "01:00:00", "00:00:30")
        mock_get_status.return_value = running_status
        
        monitor = JobMonitor()
        
        with pytest.raises(TimeoutError, match="Timeout waiting for job 12345"):
            monitor.wait_for_job("12345", poll_interval=30, timeout=100)

    @patch('subprocess.Popen')
    def test_stream_logs(self, mock_popen):
        """Test log streaming functionality."""
        from submitit.core.utils import JobPaths
        
        # Mock JobPaths
        job_paths = Mock(spec=JobPaths)
        job_paths.stdout = "/path/to/stdout.log"
        job_paths.stderr = "/path/to/stderr.log"
        
        # Mock process
        mock_process = Mock()
        mock_process.stdout.readline.side_effect = [
            "Log line 1\n",
            "Log line 2\n", 
            "Log line 3\n",
            ""  # EOF
        ]
        mock_popen.return_value = mock_process
        
        monitor = JobMonitor()
        
        with patch('pathlib.Path.exists', return_value=True):
            log_lines = list(monitor.stream_logs(job_paths, follow=False, lines=10))
        
        # Should process both stdout and stderr files
        assert len(log_lines) >= 3
        assert "Log line 1" in log_lines[0]
        assert mock_popen.call_count == 2  # Once for stdout, once for stderr


class TestJobManager:
    """Tests for JobManager class."""

    def test_initialization(self):
        """Test JobManager initialization."""
        monitor = Mock(spec=JobMonitor)
        manager = JobManager(monitor)
        
        assert manager.monitor == monitor

    def test_submit_and_monitor(self):
        """Test submit and monitor functionality."""
        monitor = Mock(spec=JobMonitor)
        manager = JobManager(monitor)
        
        # Mock executor and job
        executor = Mock()
        mock_job = Mock()
        mock_job.job_id = "12345"
        mock_job.paths.stdout = "/path/to/stdout"
        executor.submit_function.return_value = mock_job
        
        def test_func():
            return "test result"
        
        job = manager.submit_and_monitor(executor, test_func, "arg1", kwarg1="value1")
        
        executor.submit_function.assert_called_once_with(test_func, "arg1", kwarg1="value1")
        assert job == mock_job

    @patch.object(JobMonitor, '_run_command')
    def test_get_resource_usage(self, mock_run_command):
        """Test getting resource usage statistics."""
        mock_run_command.return_value = "12345|1024K|2048K|50%|01:30:00|02:00:00|4G"
        
        monitor = JobMonitor()
        manager = JobManager(monitor)
        
        usage = manager.get_resource_usage("12345")
        
        mock_run_command.assert_called_once_with([
            "sacct", "-j", "12345",
            "--format=JobID,MaxRSS,MaxVMSize,AveCPU,TotalCPU,CPUTime,ReqMem",
            "--noheader", "--parsable2"
        ])
        
        assert usage['max_rss'] == "1024K"
        assert usage['max_vmsize'] == "2048K"
        assert usage['avg_cpu'] == "50%"
        assert usage['total_cpu'] == "01:30:00"
        assert usage['cpu_time'] == "02:00:00"
        assert usage['req_mem'] == "4G"

    def test_list_running_jobs(self):
        """Test listing running jobs."""
        monitor = Mock(spec=JobMonitor)
        
        all_jobs = [
            JobStatus("12345", "job1", "RUNNING", "gpu", 1, 4, "01:00:00", "00:15:30"),
            JobStatus("12346", "job2", "PENDING", "cpu", 2, 8, "02:00:00", "00:00:00"),
            JobStatus("12347", "job3", "RUNNING", "gpu", 1, 4, "00:30:00", "00:10:20"),
            JobStatus("12348", "job4", "COMPLETED", "gpu", 1, 4, "00:45:00", "00:42:15")
        ]
        
        monitor.get_user_jobs.return_value = all_jobs
        manager = JobManager(monitor)
        
        running_jobs = manager.list_running_jobs()
        
        assert len(running_jobs) == 2
        assert running_jobs[0].job_id == "12345"
        assert running_jobs[1].job_id == "12347"
        assert all(job.state == "RUNNING" for job in running_jobs)

    def test_cleanup_old_jobs_placeholder(self):
        """Test cleanup old jobs method (placeholder implementation)."""
        monitor = Mock(spec=JobMonitor)
        manager = JobManager(monitor)
        
        # This method is not implemented yet, should return None
        result = manager.cleanup_old_jobs(days=7)
        assert result is None


class TestJobMonitorErrorHandling:
    """Test error handling in JobMonitor."""

    @patch.object(JobMonitor, '_run_command')
    def test_get_job_status_exception(self, mock_run_command):
        """Test exception handling in get_job_status."""
        mock_run_command.side_effect = Exception("Network error")
        
        monitor = JobMonitor()
        status = monitor.get_job_status("12345")
        
        assert status is None

    @patch.object(JobMonitor, '_run_command')
    def test_get_completed_job_status_exception(self, mock_run_command):
        """Test exception handling in get_completed_job_status."""
        mock_run_command.side_effect = Exception("Network error")
        
        monitor = JobMonitor()
        status = monitor._get_completed_job_status("12345")
        
        assert status is None

    @patch.object(JobMonitor, '_run_command')
    def test_get_user_jobs_exception(self, mock_run_command):
        """Test exception handling in get_user_jobs."""
        mock_run_command.side_effect = Exception("Network error")
        
        monitor = JobMonitor()
        jobs = monitor.get_user_jobs()
        
        assert jobs == []

    @patch.object(JobMonitor, '_run_command')
    def test_get_resource_usage_exception(self, mock_run_command):
        """Test exception handling in get_resource_usage."""
        mock_run_command.side_effect = Exception("Network error")
        
        monitor = JobMonitor()
        manager = JobManager(monitor)
        usage = manager.get_resource_usage("12345")
        
        assert usage == {}

    @patch.object(JobMonitor, 'get_job_status')
    def test_wait_for_job_not_found(self, mock_get_status):
        """Test waiting for non-existent job."""
        mock_get_status.return_value = None
        
        monitor = JobMonitor()
        
        with pytest.raises(RuntimeError, match="Job 12345 not found"):
            monitor.wait_for_job("12345")