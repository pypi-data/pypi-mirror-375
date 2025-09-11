"""Tests for experiment tracking functionality."""

from unittest.mock import Mock, patch, call, mock_open
import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from aihpi.tracking.tracking import (
    ExperimentMetadata, ExperimentTracker, WandbTracker, 
    MLflowTracker, LocalTracker, ExperimentManager, create_tracker
)


class TestExperimentMetadata:
    """Tests for ExperimentMetadata dataclass."""

    def test_metadata_creation(self):
        """Test ExperimentMetadata creation with required fields."""
        metadata = ExperimentMetadata(
            run_id="test-run-123",
            experiment_name="test-experiment"
        )
        
        assert metadata.run_id == "test-run-123"
        assert metadata.experiment_name == "test-experiment"
        assert metadata.job_id is None
        assert metadata.start_time is not None  # Auto-generated
        assert metadata.end_time is None
        assert metadata.status == "running"
        assert metadata.tags == {}
        assert metadata.params == {}

    def test_metadata_with_optional_fields(self):
        """Test ExperimentMetadata with optional fields."""
        metadata = ExperimentMetadata(
            run_id="test-run-456",
            experiment_name="test-experiment-2",
            job_id="slurm-12345",
            start_time="2024-01-01T10:00:00",
            end_time="2024-01-01T11:00:00",
            status="completed",
            tags={"environment": "test", "version": "1.0"},
            params={"learning_rate": 0.001, "batch_size": 32}
        )
        
        assert metadata.job_id == "slurm-12345"
        assert metadata.start_time == "2024-01-01T10:00:00"
        assert metadata.end_time == "2024-01-01T11:00:00"
        assert metadata.status == "completed"
        assert metadata.tags["environment"] == "test"
        assert metadata.params["learning_rate"] == 0.001

    def test_metadata_post_init(self):
        """Test post_init behavior with None values."""
        metadata = ExperimentMetadata(
            run_id="test-run-789",
            experiment_name="test-experiment-3",
            tags=None,
            params=None,
            start_time=None
        )
        
        assert metadata.tags == {}
        assert metadata.params == {}
        assert metadata.start_time is not None
        assert isinstance(metadata.start_time, str)


class TestWandbTracker:
    """Tests for WandbTracker class."""

    def test_initialization_success(self):
        """Test successful WandbTracker initialization."""
        with patch('builtins.__import__', side_effect=lambda name, *args: Mock() if name == 'wandb' else __import__(name, *args)):
            tracker = WandbTracker(project="test-project", entity="test-team")
            
            assert tracker.project == "test-project"
            assert tracker.entity == "test-team"
            assert tracker.run is None

    def test_initialization_import_error(self):
        """Test WandbTracker initialization with missing wandb."""
        with patch('aihpi.tracking.tracking.wandb', side_effect=ImportError):
            with pytest.raises(ImportError, match="wandb not installed"):
                WandbTracker(project="test-project")

    @patch.dict(os.environ, {"SLURM_JOB_ID": "12345", "WORLD_SIZE": "2", "NODE_RANK": "0"})
    @patch('os.uname')
    def test_init_run_with_slurm(self, mock_uname):
        """Test initializing run with SLURM environment."""
        mock_uname.return_value = Mock(nodename="compute-node-01")
        
        with patch('aihpi.tracking.tracking.wandb') as mock_wandb_module:
            mock_run = Mock()
            mock_run.id = "wandb-run-123"
            mock_wandb_module.init.return_value = mock_run
            
            tracker = WandbTracker(project="test-project", entity="test-team")
            run_id = tracker.init_run("test-experiment", {"param1": "value1"})
            
            mock_wandb_module.init.assert_called_once_with(
                project="test-project",
                entity="test-team",
                name="test-experiment",
                config={"param1": "value1"},
                job_type="training"
            )
            
            assert run_id == "wandb-run-123"
            assert tracker.run == mock_run

    def test_log_params(self):
        """Test logging parameters to wandb."""
        with patch('aihpi.tracking.tracking.wandb') as mock_wandb_module:
            mock_run = Mock()
            mock_wandb_module.init.return_value = mock_run
            
            tracker = WandbTracker(project="test-project")
            tracker.init_run("test", {})
            
            params = {"learning_rate": 0.001, "batch_size": 32}
            tracker.log_params(params)
            
            mock_wandb_module.config.update.assert_called_once_with(params)

    def test_log_metrics(self):
        """Test logging metrics to wandb."""
        with patch('aihpi.tracking.tracking.wandb') as mock_wandb_module:
            mock_run = Mock()
            mock_wandb_module.init.return_value = mock_run
            
            tracker = WandbTracker(project="test-project")
            tracker.init_run("test", {})
            
            metrics = {"loss": 0.5, "accuracy": 0.85}
            tracker.log_metrics(metrics, step=10)
            
            mock_wandb_module.log.assert_called_once_with(metrics, step=10)

    def test_log_artifacts(self):
        """Test logging artifacts to wandb."""
        with patch('aihpi.tracking.tracking.wandb') as mock_wandb_module:
            mock_run = Mock()
            mock_run.id = "wandb-run-123"
            mock_artifact = Mock()
            mock_wandb_module.init.return_value = mock_run
            mock_wandb_module.Artifact.return_value = mock_artifact
            
            tracker = WandbTracker(project="test-project")
            tracker.init_run("test", {})
            
            tracker.log_artifacts("/path/to/model")
            
            mock_wandb_module.Artifact.assert_called_once_with(
                name="model-wandb-run-123",
                type="model"
            )
            mock_artifact.add_dir.assert_called_once_with("/path/to/model")
            mock_run.log_artifact.assert_called_once_with(mock_artifact)

    def test_finish_run(self):
        """Test finishing wandb run."""
        with patch('aihpi.tracking.tracking.wandb') as mock_wandb_module:
            mock_run = Mock()
            mock_wandb_module.init.return_value = mock_run
            
            tracker = WandbTracker(project="test-project")
            tracker.init_run("test", {})
            
            tracker.finish_run("completed")
            mock_wandb_module.finish.assert_called_once_with(exit_code=0)
            
            tracker.finish_run("failed")
            mock_wandb_module.finish.assert_called_with(exit_code=1)

    def test_no_run_methods(self):
        """Test methods when no run is initialized."""
        with patch('aihpi.tracking.tracking.wandb') as mock_wandb_module:
            tracker = WandbTracker(project="test-project")
            
            # These should not crash when run is None
            tracker.log_params({"param": "value"})
            tracker.log_metrics({"metric": 1.0})
            tracker.log_artifacts("/path")
            tracker.finish_run()
            
            # Verify wandb methods were not called
            mock_wandb_module.config.update.assert_not_called()
            mock_wandb_module.log.assert_not_called()
            mock_wandb_module.finish.assert_not_called()


class TestMLflowTracker:
    """Tests for MLflowTracker class."""

    def test_initialization_success(self):
        """Test successful MLflowTracker initialization."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            
            assert tracker.experiment_name == "test-experiment"
            assert tracker.run_id is None
            assert tracker.experiment_id == "exp-123"

    def test_initialization_import_error(self):
        """Test MLflowTracker initialization with missing mlflow."""
        with patch('aihpi.tracking.tracking.mlflow', side_effect=ImportError):
            with pytest.raises(ImportError, match="mlflow not installed"):
                MLflowTracker(experiment_name="test-experiment")

    def test_initialization_create_experiment(self):
        """Test creating new experiment when it doesn't exist."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_mlflow.get_experiment_by_name.side_effect = Exception("Not found")
            mock_mlflow.create_experiment.return_value = "new-exp-456"
            
            tracker = MLflowTracker(experiment_name="new-experiment")
            
            mock_mlflow.create_experiment.assert_called_once_with("new-experiment")
            assert tracker.experiment_id == "new-exp-456"

    @patch.dict(os.environ, {"SLURM_JOB_ID": "67890"})
    @patch('os.uname')
    def test_init_run_with_slurm(self, mock_uname):
        """Test initializing MLflow run with SLURM environment."""
        mock_uname.return_value = Mock(nodename="compute-node-02")
        
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            mock_run_info = Mock()
            mock_run_info.run_id = "mlflow-run-456"
            mock_run = Mock()
            mock_run.info = mock_run_info
            mock_mlflow.start_run.return_value = mock_run
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            run_id = tracker.init_run("test-run", {"param1": "value1"})
            
            mock_mlflow.start_run.assert_called_once_with(
                experiment_id="exp-123",
                run_name="test-run"
            )
            
            assert run_id == "mlflow-run-456"
            assert tracker.run_id == "mlflow-run-456"

    def test_log_params_flat(self):
        """Test logging flat parameters to MLflow."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            
            params = {"learning_rate": 0.001, "batch_size": 32}
            tracker.log_params(params)
            
            expected_calls = [
                call("learning_rate", 0.001),
                call("batch_size", 32)
            ]
            mock_mlflow.log_param.assert_has_calls(expected_calls, any_order=True)

    def test_log_params_nested(self):
        """Test logging nested parameters to MLflow."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            
            params = {
                "model": {
                    "layers": 12,
                    "hidden_size": 768
                },
                "training": {
                    "learning_rate": 0.001
                }
            }
            tracker.log_params(params)
            
            expected_calls = [
                call("model.layers", "12"),
                call("model.hidden_size", "768"),
                call("training.learning_rate", "0.001")
            ]
            mock_mlflow.log_param.assert_has_calls(expected_calls, any_order=True)

    def test_log_metrics(self):
        """Test logging metrics to MLflow."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            
            metrics = {"loss": 0.5, "accuracy": 0.85}
            tracker.log_metrics(metrics, step=10)
            
            expected_calls = [
                call("loss", 0.5, step=10),
                call("accuracy", 0.85, step=10)
            ]
            mock_mlflow.log_metric.assert_has_calls(expected_calls, any_order=True)

    def test_log_artifacts(self):
        """Test logging artifacts to MLflow."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            
            tracker.log_artifacts("/path/to/artifacts")
            
            mock_mlflow.log_artifacts.assert_called_once_with("/path/to/artifacts")

    def test_finish_run(self):
        """Test finishing MLflow run."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = MLflowTracker(experiment_name="test-experiment")
            
            tracker.finish_run("completed")
            
            mock_mlflow.set_tag.assert_called_once_with("status", "completed")
            mock_mlflow.end_run.assert_called_once()


class TestLocalTracker:
    """Tests for LocalTracker class."""

    def test_initialization(self):
        """Test LocalTracker initialization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            
            assert tracker.log_dir == Path(tmp_dir)
            assert tracker.log_dir.exists()
            assert tracker.run_dir is None
            assert tracker.metadata is None

    @patch.dict(os.environ, {"SLURM_JOB_ID": "local-12345"})
    @patch('os.uname')
    @patch('uuid.uuid4')
    @patch('datetime.datetime')
    def test_init_run(self, mock_datetime, mock_uuid, mock_uname):
        """Test initializing local tracker run."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_uuid.return_value.hex = "abcdef123456"
        mock_uname.return_value = Mock(nodename="local-node")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            
            config = {"param1": "value1", "param2": 42}
            run_id = tracker.init_run("test-experiment", config)
            
            expected_run_id = "test-experiment_20240101_120000_abcdef12"
            assert run_id == expected_run_id
            
            # Check run directory was created
            assert tracker.run_dir is not None
            assert tracker.run_dir.exists()
            assert tracker.run_dir.name == expected_run_id
            
            # Check metadata was saved
            metadata_file = tracker.run_dir / "metadata.json"
            assert metadata_file.exists()
            
            with open(metadata_file) as f:
                saved_metadata = json.load(f)
            
            assert saved_metadata['run_id'] == expected_run_id
            assert saved_metadata['experiment_name'] == "test-experiment"
            assert saved_metadata['job_id'] == "local-12345"
            assert saved_metadata['params'] == config

    def test_log_params(self):
        """Test logging parameters to local tracker."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            tracker.init_run("test", {})
            
            new_params = {"new_param": "new_value"}
            tracker.log_params(new_params)
            
            # Check metadata was updated
            metadata_file = tracker.run_dir / "metadata.json"
            with open(metadata_file) as f:
                saved_metadata = json.load(f)
            
            assert saved_metadata['params']['new_param'] == "new_value"

    def test_log_metrics(self):
        """Test logging metrics to local tracker."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            tracker.init_run("test", {})
            
            # Log multiple metrics
            tracker.log_metrics({"loss": 0.5, "accuracy": 0.8}, step=1)
            tracker.log_metrics({"loss": 0.3, "accuracy": 0.9}, step=2)
            
            # Check metrics file
            metrics_file = tracker.run_dir / "metrics.jsonl"
            assert metrics_file.exists()
            
            with open(metrics_file) as f:
                lines = f.readlines()
            
            assert len(lines) == 2
            
            metric1 = json.loads(lines[0])
            assert metric1['step'] == 1
            assert metric1['loss'] == 0.5
            assert metric1['accuracy'] == 0.8
            
            metric2 = json.loads(lines[1])
            assert metric2['step'] == 2
            assert metric2['loss'] == 0.3
            assert metric2['accuracy'] == 0.9

    def test_log_artifacts_file(self):
        """Test logging file artifacts to local tracker."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            tracker.init_run("test", {})
            
            # Create a test artifact file
            test_file = Path(tmp_dir) / "test_artifact.txt"
            test_file.write_text("test content")
            
            tracker.log_artifacts(test_file)
            
            # Check artifact was copied
            artifacts_dir = tracker.run_dir / "artifacts"
            assert artifacts_dir.exists()
            
            copied_file = artifacts_dir / "test_artifact.txt"
            assert copied_file.exists()
            assert copied_file.read_text() == "test content"

    def test_log_artifacts_directory(self):
        """Test logging directory artifacts to local tracker."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            tracker.init_run("test", {})
            
            # Create a test artifact directory
            test_dir = Path(tmp_dir) / "test_model"
            test_dir.mkdir()
            (test_dir / "model.pt").write_text("model data")
            (test_dir / "config.json").write_text('{"layers": 12}')
            
            tracker.log_artifacts(test_dir)
            
            # Check directory was copied
            artifacts_dir = tracker.run_dir / "artifacts"
            copied_dir = artifacts_dir / "test_model"
            assert copied_dir.exists()
            assert (copied_dir / "model.pt").exists()
            assert (copied_dir / "config.json").exists()

    def test_finish_run(self):
        """Test finishing local tracker run."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            tracker.init_run("test", {})
            
            tracker.finish_run("completed")
            
            # Check metadata was updated
            metadata_file = tracker.run_dir / "metadata.json"
            with open(metadata_file) as f:
                saved_metadata = json.load(f)
            
            assert saved_metadata['status'] == "completed"
            assert saved_metadata['end_time'] is not None


class TestCreateTracker:
    """Tests for tracker factory function."""

    def test_create_wandb_tracker(self):
        """Test creating wandb tracker."""
        with patch('aihpi.tracking.tracking.wandb'):
            tracker = create_tracker("wandb", project="test-project", entity="test-team")
            assert isinstance(tracker, WandbTracker)
            assert tracker.project == "test-project"
            assert tracker.entity == "test-team"

    def test_create_mlflow_tracker(self):
        """Test creating mlflow tracker."""
        with patch('aihpi.tracking.tracking.mlflow') as mock_mlflow:
            mock_experiment = Mock()
            mock_experiment.experiment_id = "exp-123"
            mock_mlflow.get_experiment_by_name.return_value = mock_experiment
            
            tracker = create_tracker("mlflow", experiment_name="test-exp")
            assert isinstance(tracker, MLflowTracker)
            assert tracker.experiment_name == "test-exp"

    def test_create_local_tracker(self):
        """Test creating local tracker."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = create_tracker("local", log_dir=tmp_dir)
            assert isinstance(tracker, LocalTracker)
            assert tracker.log_dir == Path(tmp_dir)

    def test_create_unknown_tracker(self):
        """Test creating unknown tracker type."""
        with pytest.raises(ValueError, match="Unknown tracker type: unknown"):
            create_tracker("unknown")

    def test_case_insensitive_tracker_creation(self):
        """Test case insensitive tracker creation."""
        with patch('aihpi.tracking.tracking.wandb'):
            tracker1 = create_tracker("WANDB", project="test")
            tracker2 = create_tracker("WaNdB", project="test")
            
            assert isinstance(tracker1, WandbTracker)
            assert isinstance(tracker2, WandbTracker)


class TestExperimentManager:
    """Tests for ExperimentManager class."""

    def test_initialization(self):
        """Test ExperimentManager initialization."""
        tracker = Mock(spec=ExperimentTracker)
        manager = ExperimentManager(tracker)
        
        assert manager.tracker == tracker
        assert manager.run_id is None

    def test_start_experiment(self):
        """Test starting experiment."""
        tracker = Mock(spec=ExperimentTracker)
        tracker.init_run.return_value = "exp-run-123"
        
        manager = ExperimentManager(tracker)
        
        config = {"param1": "value1", "param2": 42}
        run_id = manager.start_experiment("test-experiment", config)
        
        tracker.init_run.assert_called_once_with("test-experiment", config)
        assert run_id == "exp-run-123"
        assert manager.run_id == "exp-run-123"

    def test_log_training_metrics(self):
        """Test logging training metrics with epoch."""
        tracker = Mock(spec=ExperimentTracker)
        manager = ExperimentManager(tracker)
        
        manager.log_training_metrics(epoch=5, loss=0.3, accuracy=0.85, lr=0.001)
        
        tracker.log_metrics.assert_called_once_with(
            {"loss": 0.3, "accuracy": 0.85, "lr": 0.001},
            step=5
        )

    def test_log_model_checkpoint(self):
        """Test logging model checkpoint."""
        tracker = Mock(spec=ExperimentTracker)
        manager = ExperimentManager(tracker)
        
        checkpoint_path = "/path/to/checkpoint"
        manager.log_model_checkpoint(checkpoint_path)
        
        tracker.log_artifacts.assert_called_once_with(checkpoint_path)

    def test_finish_experiment(self):
        """Test finishing experiment."""
        tracker = Mock(spec=ExperimentTracker)
        manager = ExperimentManager(tracker)
        
        manager.finish_experiment("completed")
        
        tracker.finish_run.assert_called_once_with("completed")


class TestExperimentTrackerSlurmIntegration:
    """Test SLURM environment integration in trackers."""

    @patch.dict(os.environ, {
        "SLURM_JOB_ID": "test-12345",
        "SLURM_JOB_NUM_NODES": "2",
        "SLURM_GPUS_PER_NODE": "4",
        "SLURM_JOB_PARTITION": "gpu",
        "WORLD_SIZE": "8",
        "NODE_RANK": "0"
    })
    @patch('os.uname')
    def test_log_slurm_info_integration(self, mock_uname):
        """Test SLURM information logging integration."""
        mock_uname.return_value = Mock(nodename="gpu-node-01")
        
        # Test with LocalTracker
        with tempfile.TemporaryDirectory() as tmp_dir:
            tracker = LocalTracker(log_dir=tmp_dir)
            
            # Mock the log_params method to capture calls
            with patch.object(tracker, 'log_params') as mock_log_params:
                tracker.log_slurm_info("test-12345", {"custom": "info"})
                
                # Verify SLURM info was logged
                mock_log_params.assert_called_once()
                logged_params = mock_log_params.call_args[0][0]
                
                assert "slurm" in logged_params
                slurm_info = logged_params["slurm"]
                assert slurm_info["job_id"] == "test-12345"
                assert slurm_info["num_nodes"] == "2"
                assert slurm_info["gpus_per_node"] == "4"
                assert slurm_info["partition"] == "gpu"
                assert slurm_info["custom"] == "info"


class TestTrackerErrorHandling:
    """Test error handling in trackers."""

    def test_local_tracker_no_run_dir(self):
        """Test LocalTracker methods when run_dir is None."""
        tracker = LocalTracker()
        
        # These should not crash when run_dir is None
        tracker.log_metrics({"metric": 1.0}, step=1)
        tracker.log_artifacts("/some/path")
        
        # No files should be created
        assert tracker.run_dir is None

    def test_local_tracker_no_metadata(self):
        """Test LocalTracker methods when metadata is None."""
        tracker = LocalTracker()
        
        # This should not crash when metadata is None
        tracker.log_params({"param": "value"})
        tracker.finish_run("completed")
        
        assert tracker.metadata is None