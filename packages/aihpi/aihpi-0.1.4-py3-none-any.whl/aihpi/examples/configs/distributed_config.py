"""Example distributed training SLURM configuration."""

from pathlib import Path
from aihpi import JobConfig, ContainerConfig

# Multi-node distributed job configuration
config = JobConfig(
    job_name="distributed-training",
    num_nodes=4,  # Multi-node -> uses submit_distributed_training()
    gpus_per_node=8,
    cpus_per_task=16,
    walltime="08:00:00",
    partition="gpu-large",
    login_node="10.130.0.6",
    shared_storage_root=Path("/shared/storage"),
    env_vars={
        "NCCL_DEBUG": "INFO",
        "NCCL_IB_DISABLE": "0",
        "MASTER_PORT": "29500"
    }
)

# Container for distributed training
config.container = ContainerConfig(
    name="pytorch-distributed",
    mount_home=True,
    workdir="/workspace",
    mounts=[
        "/shared/storage:/workspace",
        "/data:/data",
        "/dev/infiniband:/dev/infiniband"  # InfiniBand for fast inter-node communication
    ]
)

# Distributed training configuration
app_config = {
    "model_name": "llama-7b",
    "batch_size": 32,  # Per GPU batch size
    "gradient_accumulation": 4,
    "learning_rate": 5e-5,
    "num_epochs": 3,
    "save_strategy": "epoch",
    "output_dir": "/workspace/outputs",
    "logging_dir": "/workspace/logs"
}