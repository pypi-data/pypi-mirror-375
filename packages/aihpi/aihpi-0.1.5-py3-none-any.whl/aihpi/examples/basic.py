"""Example usage of aihpi package."""

from pathlib import Path
from aihpi import SlurmJobExecutor, JobConfig, ContainerConfig


def example_single_node():
    """Example: Single-node job submission."""
    config = JobConfig(
        job_name="single-node-example",
        num_nodes=1,
        gpus_per_node=2,
        walltime="00:30:00",
        partition="aisc",
        login_node="10.130.0.6",
    )
    
    executor = SlurmJobExecutor(config)
    
    def my_training_function():
        print("Running single-node training...")
        # Your training code here
        return "Training completed"
    
    job = executor.submit_function(my_training_function)
    return job


def example_multi_node():
    """Example: Multi-node distributed training."""
    config = JobConfig(
        job_name="multi-node-example", 
        num_nodes=2,
        gpus_per_node=2,
        walltime="02:00:00",
        partition="aisc",
        shared_storage_root=Path("/sc/home/your_username"),
        login_node="10.130.0.6",
    )
    
    # Configure container
    config.container = ContainerConfig(
        name="torch2412"
    )
    
    executor = SlurmJobExecutor(config)
    
    def distributed_training():
        import os
        print(f"Node rank: {os.getenv('NODE_RANK')}")
        print(f"World size: {os.getenv('WORLD_SIZE')}")
        print(f"Master addr: {os.getenv('MASTER_ADDR')}")
        # Your distributed training code here
        return "Distributed training completed"
    
    job = executor.submit_distributed_training(distributed_training)
    return job


def example_llamafactory():
    """Example: LlamaFactory training job."""
    config = JobConfig(
        job_name="llama-training",
        num_nodes=2, 
        gpus_per_node=1,
        walltime="04:00:00",
        partition="aisc",
        workspace_mount=Path("/sc/home/your_username/LLaMA-Factory"),
        setup_commands=["source /workspace/vnv/bin/activate"],
        login_node="10.130.0.6",
    )
    
    # Add workspace mount to container
    config.container.mounts.append(f"{config.workspace_mount}:/workspace")
    
    executor = SlurmJobExecutor(config)
    
    # Submit LlamaFactory training using CLI
    job = executor.submit_cli_training(
        command=["llamafactory-cli", "train"],
        config_path="examples/train_lora/llama3_lora_sft.yaml"
    )
    return job


def example_llamafactory_uv():
    """Example: LlamaFactory training job with UV."""
    config = JobConfig(
        job_name="llama-training-uv",
        num_nodes=2, 
        gpus_per_node=1,
        walltime="04:00:00",
        partition="aisc",
        workspace_mount=Path("/sc/home/your_username/LLaMA-Factory"),
        setup_commands=[
            "cd /workspace",
            "uv sync --extra torch --extra metrics --prerelease=allow"
        ],
        login_node="10.130.0.6",
    )
    
    # Add workspace mount to container
    config.container.mounts.append(f"{config.workspace_mount}:/workspace")
    
    executor = SlurmJobExecutor(config)
    
    # Submit LlamaFactory training using UV
    job = executor.submit_cli_training(
        command=["uv", "run", "--prerelease=allow", "llamafactory-cli", "train"],
        config_path="examples/train_lora/llama3_lora_pretrain.yaml"
    )
    return job


def example_remote_submission():
    """Example: Submit jobs from remote machine via SSH."""
    config = JobConfig(
        job_name="remote-job",
        num_nodes=1,
        gpus_per_node=1, 
        walltime="01:00:00",
        partition="aisc",
        login_node="10.130.0.6",  # SSH to this login node
    )
    
    executor = SlurmJobExecutor(config)
    
    def remote_task():
        print("Running task via remote submission")
        return "Remote task completed"
    
    job = executor.submit_function(remote_task)
    return job


def example_custom_environment():
    """Example: Job with custom environment variables."""
    config = JobConfig(
        job_name="custom-env-job",
        num_nodes=1,
        gpus_per_node=1,
        walltime="00:45:00",
        partition="aisc",
        login_node="10.130.0.6",
        env_vars={
            "CUSTOM_VAR": "custom_value",
            "MODEL_NAME": "llama-3-8b",
            "BATCH_SIZE": "32",
        },
        setup_commands=[
            "echo 'Setting up environment...'",
            "module load cuda/12.1",
        ]
    )
    
    executor = SlurmJobExecutor(config)
    
    def training_with_env():
        import os
        print(f"Custom var: {os.getenv('CUSTOM_VAR')}")
        print(f"Model name: {os.getenv('MODEL_NAME')}")
        print(f"Batch size: {os.getenv('BATCH_SIZE')}")
        # Your training code here
        return "Training with custom environment completed"
    
    job = executor.submit_function(training_with_env)
    return job


if __name__ == "__main__":
    print("aihpi examples")
    print("==============")
    print("1. Single-node job")
    example_single_node()
    print("2. Multi-node distributed training") 
    example_multi_node()
    print("3. LlamaFactory training")
    print("4. Remote submission via SSH")
    print("5. Custom environment variables")
    print()
    print("Import these examples and modify for your use case:")
    print("from aihpi.examples import example_single_node, example_multi_node, ...")