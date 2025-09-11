<div style="background-color: #ffffff; color: #000000; padding: 10px;">
<img src="00_aisc/img/logo_aisc_bmftr.jpg">
<h1>aihpi - AI High Performance Infrastructure
</div>

A Python package for simplified distributed job submission on SLURM clusters with container support. Built on top of submitit with additional features specifically designed for AI/ML workloads.

## Features

- **Simple API**: Configure and submit jobs with minimal code
- **Command Line Interface**: `aihpi` CLI for easy job submission and management
- **Distributed Training**: Automatic setup for multi-node distributed training
- **Container Support**: First-class support for Pyxis/Enroot containers
- **Remote Submission**: Submit jobs via SSH from remote machines
- **LlamaFactory Integration**: Built-in support for LlamaFactory training
- **Job Monitoring**: Real-time job status tracking and log streaming
- **Experiment Tracking**: Integration with Weights & Biases, MLflow, and local tracking
- **Flexible Configuration**: Dataclass-based configuration system

## Setup and Installation

### Prerequisites

- Python ≥ 3.8
- submitit ≥ 1.4.0
- Access to SLURM cluster with Pyxis/Enroot (for container jobs)

<details>
<summary><strong>Installation with pip</strong></summary>

1. Clone the repository:
   ```bash
   git clone https://github.com/aihpi/aihpi-cluster.git
   cd aihpi-cluster
   ```

2. Install the package:
   ```bash
   # Basic installation
   pip install -e .
   
   # With experiment tracking support
   pip install -e ".[tracking]"
   
   # With all optional dependencies
   pip install -e ".[all]"
   ```
</details>

<details>
<summary><strong>Installation with UV (Recommended)</strong></summary>

[UV](https://docs.astral.sh/uv/) is a fast Python package manager that provides better dependency resolution and faster installs:

1. Install UV (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or
   pip install uv
   ```

2. Clone and setup:
   ```bash
   git clone https://github.com/aihpi/aihpi-cluster.git
   cd aihpi-cluster
   ```

3. Install with UV:
   ```bash
   # Basic installation
   uv pip install -e .
   
   # With experiment tracking support
   uv pip install -e ".[tracking]"
   
   # With all optional dependencies (recommended)
   uv pip install -e ".[all]"
   ```
</details>

### Quick Start

After installation, start using aihpi:
   ```python
   from aihpi import SlurmJobExecutor, JobConfig
   
   config = JobConfig(
       job_name="my-training",
       num_nodes=1,
       gpus_per_node=2,
       walltime="01:00:00",
       partition="aisc",
       login_node="10.130.0.6"  # Your SLURM login node IP
   )
   
   executor = SlurmJobExecutor(config)
   job = executor.submit_function(my_training_function)
   ```

## User Guide

### Using the Tool

1. **Configure your job** using `JobConfig` with resource requirements and SLURM parameters
   - **Important**: Set `login_node` to your SLURM login node IP for remote job submission
2. **Create an executor** with `SlurmJobExecutor(config)`
3. **Submit your function** with `executor.submit_function(func)` or `executor.submit_distributed_training(func)`
4. **Monitor progress** using `JobMonitor` for real-time status updates
5. **Track experiments** with Weights & Biases, MLflow, or local tracking

### Basic Example

```python
from aihpi import SlurmJobExecutor, JobConfig, ContainerConfig

# Configure multi-node distributed training
config = JobConfig(
    job_name="distributed-training",
    num_nodes=4,
    gpus_per_node=2,
    walltime="04:00:00",
    partition="aisc",
    login_node="10.130.0.6",  # Your SLURM login node IP
)

# Configure container
config.container = ContainerConfig(
    name="torch2412",
    mounts=["/data:/workspace/data"]
)

executor = SlurmJobExecutor(config)

def distributed_training():
    import os
    print(f"Node rank: {os.getenv('NODE_RANK')}")
    print(f"World size: {os.getenv('WORLD_SIZE')}")
    # Your distributed training code here

job = executor.submit_distributed_training(distributed_training)
```

### Command Line Interface

The `aihpi` CLI provides a convenient command-line interface for job submission and management:

```bash
# Submit a single-node Python job
aihpi run train.py --config slurm_config.py

# Submit with monitoring
aihpi run train.py --config slurm_config.py --monitor

# Submit distributed job (automatically detected from config)
aihpi run train.py --config distributed_config.py

# Submit LlamaFactory job with app config
aihpi run llamafactory-cli train --config job_config.py --app-config train.yaml

# Monitor a running job
aihpi monitor 12345 --follow

# Check job status
aihpi status

# Cancel a job
aihpi cancel 12345
```

#### CLI Configuration Files

The CLI uses Python configuration files containing a `JobConfig` object:

```python
# config.py
from aihpi import JobConfig
from pathlib import Path

config = JobConfig(
    job_name="my_job",
    num_nodes=1,
    gpus_per_node=2,
    walltime="02:00:00",
    partition="gpu",
    log_dir=Path("./logs"),
    login_node="10.130.0.6"
)
```

The CLI automatically determines the submission mode:
- **Function mode**: Single-node Python scripts
- **Distributed mode**: Multi-node Python scripts (when `num_nodes > 1`) 
- **CLI mode**: Non-Python executables

### Advanced Features

- **Job Monitoring**: Real-time status tracking and log streaming
- **Experiment Tracking**: Automatic logging of metrics, parameters, and artifacts
- **Remote Submission**: Submit jobs via SSH from any machine
- **LlamaFactory Integration**: Built-in support for LLM fine-tuning

See `aihpi/examples/` for comprehensive usage examples.

### Recommendations

- Use containerized jobs for reproducible environments
- Enable experiment tracking for better ML workflow management  
- Monitor long-running jobs with the built-in monitoring utilities
- Configure SSH keys for seamless remote job submission

## Package Structure

```
aihpi/
├── cli.py              # Command-line interface
├── core/               # Core job submission functionality
│   ├── config.py      # Configuration classes
│   └── executor.py    # Job executors
├── monitoring/        # Job monitoring utilities
│   └── monitoring.py  # Real-time job status and log streaming
├── tracking/          # Experiment tracking integrations
│   └── tracking.py    # W&B, MLflow, and local tracking
└── examples/          # Usage examples
    ├── basic.py       # Basic job submission examples
    └── monitoring.py  # Monitoring and tracking examples
```

## Limitations

- **SLURM Dependency**: Requires access to a SLURM cluster environment
- **Container Runtime**: Container features require Pyxis/Enroot setup
- **Network Access**: Remote submission requires SSH connectivity to login nodes

## References

- [submitit Documentation](https://github.com/facebookincubator/submitit)
- [SLURM Workload Manager](https://slurm.schedmd.com/)
- [Weights & Biases](https://wandb.ai/)
- [MLflow](https://mlflow.org/)

## Author
- [Felix Boelter](https://hpi.de/kisz)

## License

MIT License - see LICENSE file for details.

---

## Acknowledgements
<img src="00_aisc/img/logo_bmftr_de.png" alt="drawing" style="width:170px;"/>

The [AI Service Centre Berlin Brandenburg](http://hpi.de/kisz) is funded by the [Federal Ministry of Research, Technology and Space](https://www.bmbf.de/) under the funding code 01IS22092.