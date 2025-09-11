<div align="center">
<img src="https://raw.githubusercontent.com/aihpi/aihpi-cluster/main/00_aisc/img/logo_aisc_bmftr.jpg" alt="AI Service Centre Logo" width="400">
<h1>aihpi - AI High Performance Infrastructure</h1>
</div>

A Python package for simplified distributed job submission on SLURM clusters with container support. Built on top of submitit with additional features specifically designed for AI/ML workloads.

## Installation

```bash
# Basic installation
pip install aihpi

# With experiment tracking support
pip install aihpi[tracking]

# With all optional dependencies
pip install aihpi[all]
```

## Quick Start

```python
from aihpi import SlurmJobExecutor, JobConfig

config = JobConfig(
    job_name="my-training",
    num_nodes=1,
    gpus_per_node=2,
    walltime="01:00:00",
    partition="gpu",
    login_node="10.130.0.6"  # Your SLURM login node IP
)

executor = SlurmJobExecutor(config)
job = executor.submit_function(my_training_function)
```

## Features

- **Simple API**: Configure and submit jobs with minimal code
- **Command Line Interface**: `aihpi` CLI for easy job submission and management
- **Distributed Training**: Automatic setup for multi-node distributed training
- **Container Support**: First-class support for Pyxis/Enroot containers
- **Container Submission**: Submit jobs from within containers via SSH to login nodes
- **LlamaFactory Integration**: Built-in support for LlamaFactory training
- **Job Monitoring**: Real-time job status tracking and log streaming
- **Experiment Tracking**: Integration with Weights & Biases, MLflow, and local tracking

## Command Line Usage

```bash
# Submit a Python job
aihpi run train.py --config config.py

# Submit with monitoring
aihpi run train.py --config config.py --monitor

# Submit distributed job
aihpi run train.py --config distributed_config.py

# Monitor a running job
aihpi monitor 12345 --follow
```

## Documentation & Examples

For detailed documentation, examples, and setup instructions, visit:
- **GitHub Repository**: [aihpi/aihpi-cluster](https://github.com/aihpi/aihpi-cluster)
- **Full Documentation**: [README.md](https://github.com/aihpi/aihpi-cluster#readme)

## Requirements

- Python ≥ 3.8
- Access to SLURM cluster
- submitit ≥ 1.4.0

## License

MIT License

---

## Acknowledgements
<div align="center">
<img src="https://raw.githubusercontent.com/aihpi/aihpi-cluster/main/00_aisc/img/logo_bmftr_de.png" alt="BMBF Logo" width="170"/>
</div>

The [AI Service Centre Berlin Brandenburg](http://hpi.de/kisz) is funded by the [Federal Ministry of Research, Technology and Space](https://www.bmbf.de/) under the funding code 01IS22092.