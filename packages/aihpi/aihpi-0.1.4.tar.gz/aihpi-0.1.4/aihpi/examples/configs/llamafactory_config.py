"""Example LlamaFactory training SLURM configuration."""

from pathlib import Path
from aihpi import JobConfig, ContainerConfig

# LlamaFactory job configuration
config = JobConfig(
    job_name="llamafactory-lora",
    num_nodes=2,
    gpus_per_node=4,
    cpus_per_task=12,
    walltime="06:00:00",
    partition="gpu",
    login_node="10.130.0.6",
    workspace_mount=Path("/workspace/LLaMA-Factory"),
    setup_commands=[
        "cd /workspace",
        "uv sync --extra torch --extra metrics --prerelease=allow"
    ],
    env_vars={
        "WANDB_PROJECT": "llamafactory-experiments",
        "HF_TOKEN": "your_hf_token_here",
        "CUDA_VISIBLE_DEVICES": "0,1,2,3"
    }
)

# Container configuration for LlamaFactory
config.container = ContainerConfig(
    name="llamafactory",
    mount_home=False,
    workdir="/workspace",
    writable=True,
    mounts=[
        "/workspace/LLaMA-Factory:/workspace",
        "/data/models:/data/models",
        "/data/datasets:/data/datasets"
    ]
)

# LlamaFactory configuration file path
llamafactory_config_path = "examples/train_lora/llama3_lora_sft.yaml"

# Optional: Embedded LlamaFactory configuration
# (This could be used instead of separate YAML file)
llamafactory_config = {
    "stage": "sft",
    "do_train": True,
    "model_name": "meta-llama/Llama-2-7b-hf",
    "dataset": "alpaca_gpt4_en",
    "template": "llama2",
    "finetuning_type": "lora",
    "lora_target": "q_proj,v_proj",
    "output_dir": "/workspace/saves/llama2-7b/lora/sft",
    "overwrite_cache": True,
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 4,
    "lr_scheduler_type": "cosine",
    "logging_steps": 10,
    "save_steps": 1000,
    "learning_rate": 5e-5,
    "num_train_epochs": 3.0,
    "resume_lora_training": True,
    "lora_rank": 8,
    "lora_dropout": 0.1,
    "lora_alpha": 32.0,
    "target_modules": "q_proj,v_proj,k_proj,o_proj,gate_proj,up_proj,down_proj"
}