"""Example local execution SLURM configuration (no SSH)."""

from pathlib import Path
from aihpi import JobConfig, ContainerConfig

# Local cluster configuration (no SSH)
config = JobConfig(
    job_name="local-training",
    num_nodes=1,
    gpus_per_node=1,
    cpus_per_task=4,
    walltime="02:00:00",
    partition="debug",
    login_node=None,  # No SSH - direct local execution
    log_dir=Path("./logs"),
    env_vars={
        "OMP_NUM_THREADS": "4",
        "CUDA_VISIBLE_DEVICES": "0"
    }
)

# Simple container setup
config.container = ContainerConfig(
    name="pytorch-local",
    mount_home=True,
    workdir="/workspace"
)

# Local training configuration
app_config = {
    "model_name": "small-bert",
    "dataset": "local-data",
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_epochs": 5,
    "output_dir": "./outputs"
}