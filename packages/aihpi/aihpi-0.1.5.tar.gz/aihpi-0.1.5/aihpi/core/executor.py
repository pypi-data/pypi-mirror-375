"""SLURM job executor with SSH and container support."""

import os
import random
import socket
import subprocess
import time
from pathlib import Path
from typing import Optional, Callable, Any, List
import shlex

import submitit
from submitit import JobEnvironment

from .config import JobConfig


def _shlex_join(argv):
    """Join arguments with proper shell escaping."""
    try:
        return shlex.join(argv)
    except AttributeError:
        # Fallback for Python < 3.8
        return " ".join(shlex.quote(a) for a in argv)


class SSHSlurmExecutor(submitit.SlurmExecutor):
    """SLURM executor that submits jobs via SSH."""
    
    def __init__(self, *args, login_node: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._login_node = login_node
        self.ssh_base = [
            "ssh", "-q",
            "-o", "BatchMode=yes", 
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            login_node,
        ]
    
    def _make_submission_command(self, submission_file_path: str):
        """Wrap sbatch command with SSH."""
        sbatch_cmd = super()._make_submission_command(submission_file_path)
        return self.ssh_base + [_shlex_join(sbatch_cmd)]


class SlurmJobExecutor:
    """Main job executor class for distributed training."""
    
    def __init__(self, config: JobConfig):
        self.config = config
        self._executor = None
        
    def _get_executor(self, job_specific_folder: Optional[Path] = None):
        """Get the appropriate submitit executor."""
        if self._executor is None:
            # Use job-specific folder if provided, otherwise use default
            log_folder = job_specific_folder or self.config.log_dir
            
            if self.config.login_node:
                self._executor = SSHSlurmExecutor(
                    folder=log_folder,
                    login_node=self.config.login_node
                )
            else:
                self._executor = submitit.SlurmExecutor(folder=log_folder)
            
            # Configure executor parameters
            additional_params = {
                "constraint": "ARCH:X86",
                "export": self.config.get_export_string(),
            }
            
            # Add container parameters if using containers
            if self.config.container:
                additional_params.update({
                    "container_name": self.config.container.name,
                    "container_mount_home": self.config.container.mount_home,
                    "container_workdir": self.config.container.workdir,
                    "container_writable": self.config.container.writable,
                    "container_mounts": self.config.container.get_mount_string(),
                })
            
            self._executor.update_parameters(
                job_name=self.config.job_name,
                partition=self.config.partition,
                nodes=self.config.num_nodes,
                ntasks_per_node=1,
                gpus_per_node=self.config.gpus_per_node,
                cpus_per_task=self.config.cpus_per_task,
                time=self.config.get_walltime_minutes(),
                use_srun=False,
                setup=self.config.setup_commands,
                additional_parameters=additional_params,
                account=self.config.account,
                qos=self.config.qos,
            )
            
        return self._executor
    
    def submit_function(self, func: Callable, *args, **kwargs) -> submitit.Job:
        """Submit a Python function as a job."""
        # Create job-specific directory with timestamp (no renaming)
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        job_folder_name = f"job_{timestamp}_{unique_id}"
        job_dir = self.config.log_dir / job_folder_name
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Create executor with job-specific directory
        if self.config.login_node:
            executor = SSHSlurmExecutor(
                folder=job_dir,
                login_node=self.config.login_node
            )
        else:
            executor = submitit.SlurmExecutor(folder=job_dir)
        
        # Configure executor parameters
        self._configure_executor(executor)
        
        # Submit job (no renaming - keep original folder)
        job = executor.submit(func, *args, **kwargs)
        
        print(f"🎉 Submitted SLURM job id: {job.job_id}")
        print(f"📁 Job directory: {job_dir}")
        print(f"  Stdout: {job.paths.stdout}")
        print(f"  Stderr: {job.paths.stderr}")
        
        return job
    
    def _configure_executor(self, executor):
        """Configure executor with job parameters."""
        additional_params = {
            "constraint": "ARCH:X86",
            "export": self.config.get_export_string(),
        }
        
        if self.config.container:
            additional_params.update({
                "container_name": self.config.container.name,
                "container_mount_home": self.config.container.mount_home,
                "container_workdir": self.config.container.workdir,
                "container_writable": self.config.container.writable,
                "container_mounts": self.config.container.get_mount_string(),
            })
        
        executor.update_parameters(
            job_name=self.config.job_name,
            partition=self.config.partition,
            nodes=self.config.num_nodes,
            ntasks_per_node=1,
            gpus_per_node=self.config.gpus_per_node,
            cpus_per_task=self.config.cpus_per_task,
            time=self.config.get_walltime_minutes(),
            use_srun=False,
            setup=self.config.setup_commands,
            additional_parameters=additional_params,
            account=self.config.account,
            qos=self.config.qos,
        )
    
    
    def submit_distributed_training(
        self, 
        training_function: Callable,
        config_path: Optional[str] = None,
        **kwargs
    ) -> submitit.Job:
        """
        Submit a distributed training job.
        
        Args:
            training_function: Function to run on each node
            config_path: Path to training configuration file
            **kwargs: Additional arguments to pass to training function
        """
        def distributed_wrapper():
            return self._distributed_training_wrapper(
                training_function, 
                config_path, 
                **kwargs
            )
        
        return self.submit_function(distributed_wrapper)
    
    def _distributed_training_wrapper(
        self, 
        training_function: Callable,
        config_path: Optional[str] = None,
        **kwargs
    ):
        """Wrapper function that sets up distributed training environment."""
        env = JobEnvironment()
        master_addr = env.hostnames[0]
        node_rank = env.node
        world_size = env.num_tasks
        
        # Set up distributed environment variables
        os.environ["MASTER_ADDR"] = master_addr
        os.environ["NODE_RANK"] = str(node_rank)
        os.environ["RANK"] = str(node_rank)
        os.environ["WORLD_SIZE"] = str(world_size)
        os.environ["FORCE_TORCHRUN"] = "1"
        
        # Set master port
        master_port = os.getenv("MASTER_PORT")
        if master_port is None:
            master_port = str(random.randint(30000, 50000))
            os.environ["MASTER_PORT"] = master_port
        
        if config_path:
            os.environ["CONFIG_PATH"] = config_path
        
        # Handle HuggingFace authentication on rank 0
        if node_rank == 0:
            self._setup_huggingface_auth()
        
        # Workers wait for master to be ready
        if node_rank != 0:
            self._wait_for_master(master_addr, int(master_port))
        
        # Run the actual training function
        return training_function(**kwargs)
    
    def _setup_huggingface_auth(self):
        """Set up HuggingFace authentication."""
        token = os.getenv("HUGGING_FACE_HUB_TOKEN")
        if token is None and self.config.hf_token_file.exists():
            token = self.config.hf_token_file.read_text().strip()
        
        if token:
            subprocess.run(
                ["huggingface-cli", "login", "--token", token],
                check=True,
            )
    
    def _wait_for_master(self, master_addr: str, master_port: int):
        """Wait for master node to be ready."""
        while True:
            try:
                s = socket.socket()
                s.connect((master_addr, master_port))
                s.close()
                break
            except OSError:
                time.sleep(1)
    
    def submit_cli_training(self, command: List[str], config_path: Optional[str] = None) -> submitit.Job:
        """
        Submit a CLI-based training job with distributed support.
        
        Args:
            command: Command to execute (e.g., ["llamafactory-cli", "train"])
            config_path: Optional path to configuration file
        """
        def cli_train():
            # Add config path if provided and not already in command
            cmd = command.copy()
            if config_path and config_path not in cmd:
                cmd.append(os.getenv("CONFIG_PATH", config_path))
            
            print(f"[{socket.gethostname()}|rank {os.getenv('NODE_RANK', 0)}] "
                  f"Launching: {' '.join(cmd)}", flush=True)
            
            subprocess.run(cmd, check=True)
        
        return self.submit_distributed_training(cli_train, config_path)
    
