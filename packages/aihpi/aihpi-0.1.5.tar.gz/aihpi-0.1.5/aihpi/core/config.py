"""Configuration classes for aihpi job submission."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class ContainerConfig:
    """Container configuration for jobs."""
    name: str = "torch2412"
    mount_home: bool = True
    workdir: str = "/workspace"
    writable: bool = True
    mounts: List[str] = field(default_factory=list)
    
    def get_mount_string(self) -> str:
        """Get container mounts as SLURM parameter string."""
        mounts = self.mounts.copy()
        mounts.append("/dev/infiniband:/dev/infiniband")
        return ",".join(mounts)


@dataclass
class JobConfig:
    """Configuration for SLURM job submission."""
    
    # Job identification
    job_name: str = "aihpi-job"
    
    # Resource allocation
    num_nodes: int = 1
    gpus_per_node: int = 1
    cpus_per_task: int = 4
    walltime: str = "01:00:00"  # HH:MM:SS
    
    # SLURM configuration
    partition: str = "aisc"
    account: Optional[str] = None
    qos: Optional[str] = None
    
    # Paths and directories
    log_dir: Path = field(default_factory=lambda: Path("logs/aihpi"))
    shared_storage_root: Path = field(default_factory=lambda: Path("/sc/home"))
    workspace_mount: Optional[Path] = None
    
    # Container configuration
    container: ContainerConfig = field(default_factory=ContainerConfig)
    
    # Environment
    hf_token_file: Path = field(default_factory=lambda: Path.home() / ".huggingface" / "token")
    hf_home: Optional[Path] = None
    setup_commands: List[str] = field(default_factory=list)
    env_vars: dict = field(default_factory=dict)
    
    # SSH configuration (for remote submission)
    login_node: Optional[str] = None
    
    def __post_init__(self):
        """Set default values that depend on other fields."""
        if self.hf_home is None:
            self.hf_home = self.shared_storage_root / ".huggingface"
        
        if self.account is None:
            self.account = self.partition
            
        if self.qos is None:
            self.qos = self.partition
            
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_walltime_minutes(self) -> int:
        """Convert walltime string to minutes."""
        h, m, s = map(int, self.walltime.split(":"))
        return h * 60 + m + s // 60
    
    def get_export_string(self) -> str:
        """Get environment variables as SLURM export string."""
        exports = ["ALL"]  # Keep existing environment
        
        if self.hf_home:
            exports.append(f"HF_HOME={self.hf_home}")
            
        # Add custom environment variables
        for key, value in self.env_vars.items():
            exports.append(f"{key}={value}")
            
        return ",".join(exports)