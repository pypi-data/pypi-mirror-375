"""
aihpi - AI High Performance Infrastructure Package

A Python package for distributed job submission on SLURM clusters with container support.
Based on submitit with additional features for AI/ML workloads.
"""

from .core import JobConfig, ContainerConfig, SlurmJobExecutor
from .monitoring import JobMonitor, JobManager, JobStatus
from .tracking import ExperimentTracker, ExperimentManager, create_tracker

__version__ = "0.1.0"
__all__ = [
    "SlurmJobExecutor", 
    "JobConfig", 
    "ContainerConfig",
    "JobMonitor",
    "JobManager", 
    "JobStatus",
    "ExperimentTracker",
    "ExperimentManager",
    "create_tracker"
]