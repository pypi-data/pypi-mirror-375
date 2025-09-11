"""Experiment tracking integrations."""

import os
import json
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExperimentMetadata:
    """Experiment metadata container."""
    run_id: str
    experiment_name: str
    job_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str = "running"
    tags: Dict[str, str] = None
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.params is None:
            self.params = {}
        if self.start_time is None:
            self.start_time = datetime.now().isoformat()


class ExperimentTracker(ABC):
    """Base class for experiment tracking integrations."""
    
    @abstractmethod
    def init_run(self, experiment_name: str, config: Dict[str, Any]) -> str:
        """Initialize a new experiment run."""
        pass
    
    @abstractmethod
    def log_params(self, params: Dict[str, Any]):
        """Log experiment parameters."""
        pass
    
    @abstractmethod
    def log_metrics(self, metrics: Dict[str, Union[int, float]], step: Optional[int] = None):
        """Log metrics at a given step."""
        pass
    
    @abstractmethod
    def log_artifacts(self, artifact_path: Union[str, Path]):
        """Log artifacts (models, plots, etc.)."""
        pass
    
    @abstractmethod
    def finish_run(self, status: str = "completed"):
        """Finish the experiment run."""
        pass
    
    def log_slurm_info(self, job_id: str, node_info: Dict[str, Any]):
        """Log SLURM job information."""
        slurm_info = {
            "job_id": job_id,
            "num_nodes": os.getenv("SLURM_JOB_NUM_NODES"),
            "gpus_per_node": os.getenv("SLURM_GPUS_PER_NODE"),
            "partition": os.getenv("SLURM_JOB_PARTITION"),
            **node_info
        }
        self.log_params({"slurm": slurm_info})


class WandbTracker(ExperimentTracker):
    """Weights & Biases experiment tracker."""
    
    def __init__(self, project: str, entity: Optional[str] = None):
        self.project = project
        self.entity = entity
        self.run = None
        
        try:
            import wandb
            self.wandb = wandb
        except ImportError:
            raise ImportError("wandb not installed. Run: pip install wandb")
    
    def init_run(self, experiment_name: str, config: Dict[str, Any]) -> str:
        """Initialize wandb run."""
        self.run = self.wandb.init(
            project=self.project,
            entity=self.entity,
            name=experiment_name,
            config=config,
            job_type="training"
        )
        
        # Log SLURM environment info
        if "SLURM_JOB_ID" in os.environ:
            self.log_slurm_info(os.environ["SLURM_JOB_ID"], {
                "hostname": os.uname().nodename,
                "world_size": os.getenv("WORLD_SIZE"),
                "node_rank": os.getenv("NODE_RANK"),
            })
        
        return self.run.id
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to wandb."""
        if self.run:
            self.wandb.config.update(params)
    
    def log_metrics(self, metrics: Dict[str, Union[int, float]], step: Optional[int] = None):
        """Log metrics to wandb."""
        if self.run:
            self.wandb.log(metrics, step=step)
    
    def log_artifacts(self, artifact_path: Union[str, Path]):
        """Log artifacts to wandb."""
        if self.run:
            artifact = self.wandb.Artifact(
                name=f"model-{self.run.id}",
                type="model"
            )
            artifact.add_dir(str(artifact_path))
            self.run.log_artifact(artifact)
    
    def finish_run(self, status: str = "completed"):
        """Finish wandb run."""
        if self.run:
            self.wandb.finish(exit_code=0 if status == "completed" else 1)


class MLflowTracker(ExperimentTracker):
    """MLflow experiment tracker."""
    
    def __init__(self, experiment_name: str, tracking_uri: Optional[str] = None):
        self.experiment_name = experiment_name
        self.run_id = None
        
        try:
            import mlflow
            self.mlflow = mlflow
        except ImportError:
            raise ImportError("mlflow not installed. Run: pip install mlflow")
        
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        
        # Create experiment if it doesn't exist
        try:
            experiment_id = mlflow.create_experiment(experiment_name)
        except:
            experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
        
        self.experiment_id = experiment_id
    
    def init_run(self, experiment_name: str, config: Dict[str, Any]) -> str:
        """Initialize MLflow run."""
        run = self.mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=experiment_name
        )
        self.run_id = run.info.run_id
        
        # Log config as parameters
        self.log_params(config)
        
        # Log SLURM info
        if "SLURM_JOB_ID" in os.environ:
            self.log_slurm_info(os.environ["SLURM_JOB_ID"], {
                "hostname": os.uname().nodename,
                "world_size": os.getenv("WORLD_SIZE"),
                "node_rank": os.getenv("NODE_RANK"),
            })
        
        return self.run_id
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow."""
        # Flatten nested dictionaries
        flat_params = self._flatten_dict(params)
        for key, value in flat_params.items():
            self.mlflow.log_param(key, value)
    
    def log_metrics(self, metrics: Dict[str, Union[int, float]], step: Optional[int] = None):
        """Log metrics to MLflow."""
        for key, value in metrics.items():
            self.mlflow.log_metric(key, value, step=step)
    
    def log_artifacts(self, artifact_path: Union[str, Path]):
        """Log artifacts to MLflow."""
        self.mlflow.log_artifacts(str(artifact_path))
    
    def finish_run(self, status: str = "completed"):
        """Finish MLflow run."""
        self.mlflow.set_tag("status", status)
        self.mlflow.end_run()
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
        """Flatten nested dictionary for MLflow parameters."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)


class LocalTracker(ExperimentTracker):
    """Simple local file-based experiment tracker."""
    
    def __init__(self, log_dir: Union[str, Path] = "experiments"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = None
        self.metadata = None
    
    def init_run(self, experiment_name: str, config: Dict[str, Any]) -> str:
        """Initialize local experiment run."""
        run_id = f"{experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.run_dir = self.log_dir / run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata = ExperimentMetadata(
            run_id=run_id,
            experiment_name=experiment_name,
            job_id=os.getenv("SLURM_JOB_ID"),
            params=config.copy()
        )
        
        # Log SLURM info
        if "SLURM_JOB_ID" in os.environ:
            self.log_slurm_info(os.environ["SLURM_JOB_ID"], {
                "hostname": os.uname().nodename,
                "world_size": os.getenv("WORLD_SIZE"),
                "node_rank": os.getenv("NODE_RANK"),
            })
        
        self._save_metadata()
        return run_id
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to local file."""
        if self.metadata:
            self.metadata.params.update(params)
            self._save_metadata()
    
    def log_metrics(self, metrics: Dict[str, Union[int, float]], step: Optional[int] = None):
        """Log metrics to local file."""
        if not self.run_dir:
            return
            
        metrics_file = self.run_dir / "metrics.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            **metrics
        }
        
        with open(metrics_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_artifacts(self, artifact_path: Union[str, Path]):
        """Copy artifacts to local run directory."""
        import shutil
        
        if not self.run_dir:
            return
            
        artifacts_dir = self.run_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        src_path = Path(artifact_path)
        if src_path.is_file():
            shutil.copy2(src_path, artifacts_dir)
        elif src_path.is_dir():
            shutil.copytree(src_path, artifacts_dir / src_path.name, dirs_exist_ok=True)
    
    def finish_run(self, status: str = "completed"):
        """Finish local experiment run."""
        if self.metadata:
            self.metadata.status = status
            self.metadata.end_time = datetime.now().isoformat()
            self._save_metadata()
    
    def _save_metadata(self):
        """Save experiment metadata to JSON file."""
        if self.run_dir and self.metadata:
            metadata_file = self.run_dir / "metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(self.metadata.__dict__, f, indent=2)


def create_tracker(tracker_type: str, **kwargs) -> ExperimentTracker:
    """Factory function to create experiment trackers."""
    if tracker_type.lower() == "wandb":
        return WandbTracker(**kwargs)
    elif tracker_type.lower() == "mlflow":
        return MLflowTracker(**kwargs)
    elif tracker_type.lower() == "local":
        return LocalTracker(**kwargs)
    else:
        raise ValueError(f"Unknown tracker type: {tracker_type}")


class ExperimentManager:
    """High-level experiment management."""
    
    def __init__(self, tracker: ExperimentTracker):
        self.tracker = tracker
        self.run_id = None
    
    def start_experiment(self, name: str, config: Dict[str, Any]) -> str:
        """Start a new experiment."""
        self.run_id = self.tracker.init_run(name, config)
        print(f"🧪 Started experiment: {name} (ID: {self.run_id})")
        return self.run_id
    
    def log_training_metrics(self, epoch: int, **metrics):
        """Log training metrics with epoch as step."""
        self.tracker.log_metrics(metrics, step=epoch)
    
    def log_model_checkpoint(self, checkpoint_path: Union[str, Path]):
        """Log model checkpoint."""
        self.tracker.log_artifacts(checkpoint_path)
        print(f"💾 Logged checkpoint: {checkpoint_path}")
    
    def finish_experiment(self, status: str = "completed"):
        """Finish the experiment."""
        self.tracker.finish_run(status)
        print(f"✅ Experiment finished with status: {status}")