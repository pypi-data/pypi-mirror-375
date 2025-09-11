"""Example single-node SLURM configuration."""

from aihpi import JobConfig, ContainerConfig

# Single-node job configuration
config = JobConfig(
    job_name="single-node-training",
    num_nodes=1,  # Single node -> uses submit_function()
    gpus_per_node=2,
    cpus_per_task=8,
    walltime="01:30:00",
    partition="gpu",
    login_node="10.130.0.6",  # SSH to cluster
    env_vars={
        "PYTHONPATH": "/workspace",
        "CUDA_VISIBLE_DEVICES": "0,1"
    }
)

# Optional: Configure container
config.container = ContainerConfig(
    name="pytorch2.0",
    mount_home=True,
    workdir="/workspace",
    mounts=[
        "/data:/data",
        "/workspace:/workspace"
    ]
)

# Optional: Application-specific configuration
app_config = {
    "model_name": "resnet50",
    "batch_size": 64,
    "learning_rate": 1e-3,
    "num_epochs": 10,
    "output_dir": "/workspace/outputs"
}