"""Job monitoring and management utilities."""

import os
import time
import subprocess
from typing import Dict, List, Optional, Union, Iterator
from dataclasses import dataclass
from datetime import datetime
import submitit
from submitit.core.utils import JobPaths
from pathlib import Path


@dataclass
class JobStatus:
    """Job status information."""
    job_id: str
    name: str
    state: str
    partition: str
    nodes: int
    cpus: int
    time_limit: str
    time_elapsed: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    exit_code: Optional[str] = None


class JobMonitor:
    """Monitor SLURM jobs with real-time status updates."""
    
    def __init__(self, login_node: Optional[str] = None):
        self.login_node = login_node
        self._ssh_base = None
        
        if login_node:
            self._ssh_base = [
                "ssh", "-q",
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=no", 
                "-o", "ConnectTimeout=10",
                login_node,
            ]
    
    def _run_command(self, cmd: List[str]) -> str:
        """Run command locally or via SSH."""
        if self._ssh_base:
            full_cmd = self._ssh_base + [" ".join(cmd)]
        else:
            full_cmd = cmd
            
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
        return result.stdout
    
    def get_job_status(self, job_id: Union[str, int]) -> Optional[JobStatus]:
        """Get detailed status of a specific job."""
        try:
            output = self._run_command([
                "squeue", "-j", str(job_id), 
                "--format=%A,%j,%T,%P,%D,%C,%l,%M,%S,%e,%r", 
                "--noheader"
            ])
            
            if not output.strip():
                # Job might be completed, check sacct
                return self._get_completed_job_status(job_id)
            
            fields = output.strip().split(',')
            if len(fields) >= 7:
                return JobStatus(
                    job_id=fields[0],
                    name=fields[1],
                    state=fields[2],
                    partition=fields[3], 
                    nodes=int(fields[4]),
                    cpus=int(fields[5]),
                    time_limit=fields[6],
                    time_elapsed=fields[7],
                    start_time=fields[8] if len(fields) > 8 else None,
                    end_time=fields[9] if len(fields) > 9 else None,
                )
            return None
            
        except Exception:
            return None
    
    def _get_completed_job_status(self, job_id: Union[str, int]) -> Optional[JobStatus]:
        """Get status of completed job from accounting database."""
        try:
            output = self._run_command([
                "sacct", "-j", str(job_id), 
                "--format=JobID,JobName,State,Partition,NNodes,NCPUS,Timelimit,Elapsed,Start,End,ExitCode",
                "--noheader", "--parsable2"
            ])
            
            for line in output.strip().split('\n'):
                if line and not line.endswith('.batch'):
                    fields = line.split('|')
                    if len(fields) >= 8:
                        return JobStatus(
                            job_id=fields[0],
                            name=fields[1],
                            state=fields[2],
                            partition=fields[3],
                            nodes=int(fields[4]) if fields[4] else 0,
                            cpus=int(fields[5]) if fields[5] else 0,
                            time_limit=fields[6],
                            time_elapsed=fields[7],
                            start_time=fields[8] if len(fields) > 8 else None,
                            end_time=fields[9] if len(fields) > 9 else None,
                            exit_code=fields[10] if len(fields) > 10 else None,
                        )
            return None
            
        except Exception:
            return None
    
    def get_user_jobs(self, user: Optional[str] = None) -> List[JobStatus]:
        """Get all jobs for a user."""
        if user is None:
            user = os.getenv('USER', '$USER')
            
        try:
            output = self._run_command([
                "squeue", "-u", user,
                "--format=%A,%j,%T,%P,%D,%C,%l,%M", 
                "--noheader"
            ])
            
            jobs = []
            for line in output.strip().split('\n'):
                if line:
                    fields = line.split(',')
                    if len(fields) >= 7:
                        jobs.append(JobStatus(
                            job_id=fields[0],
                            name=fields[1],
                            state=fields[2],
                            partition=fields[3],
                            nodes=int(fields[4]),
                            cpus=int(fields[5]),
                            time_limit=fields[6],
                            time_elapsed=fields[7],
                        ))
            return jobs
            
        except Exception:
            return []
    
    def wait_for_job(self, job_id: Union[str, int], 
                     poll_interval: int = 30,
                     timeout: Optional[int] = None) -> JobStatus:
        """Wait for job to complete and return final status."""
        start_time = time.time()
        
        while True:
            status = self.get_job_status(job_id)
            if status is None:
                raise RuntimeError(f"Job {job_id} not found")
                
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Job {job_id}: {status.state} (elapsed: {status.time_elapsed})")
            
            if status.state in ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT']:
                return status
                
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Timeout waiting for job {job_id}")
                
            time.sleep(poll_interval)
    
    def cancel_job(self, job_id: Union[str, int]) -> bool:
        """Cancel a job."""
        try:
            self._run_command(["scancel", str(job_id)])
            print(f"Cancelled job {job_id}")
            return True
        except Exception as e:
            print(f"Failed to cancel job {job_id}: {e}")
            return False
    
    def stream_logs(self, job_paths: JobPaths, 
                    follow: bool = True,
                    lines: int = 50) -> Iterator[str]:
        """Stream job logs in real-time."""
        stdout_path = Path(job_paths.stdout)
        stderr_path = Path(job_paths.stderr)
        
        # Start with recent lines
        for path in [stdout_path, stderr_path]:
            if path.exists():
                try:
                    cmd = ["tail", f"-n{lines}"]
                    if follow:
                        cmd.append("-f")
                    cmd.append(str(path))
                    
                    if self._ssh_base:
                        cmd = self._ssh_base + [" ".join(cmd)]
                    
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE, text=True)
                    
                    for line in iter(process.stdout.readline, ''):
                        yield f"[{path.name}] {line.rstrip()}"
                        
                except Exception as e:
                    yield f"Error reading {path}: {e}"


class JobManager:
    """High-level job management utilities."""
    
    def __init__(self, monitor: JobMonitor):
        self.monitor = monitor
    
    def submit_and_monitor(self, executor, 
                          func, *args, **kwargs) -> submitit.Job:
        """Submit job and start monitoring."""
        job = executor.submit_function(func, *args, **kwargs)
        
        print(f"🚀 Submitted job {job.job_id}")
        print(f"📊 Monitor with: aihpi monitor {job.job_id}")
        print(f"📝 Logs: {job.paths.stdout}")
        
        return job
    
    def get_resource_usage(self, job_id: Union[str, int]) -> Dict:
        """Get resource usage statistics for completed job."""
        try:
            output = self.monitor._run_command([
                "sacct", "-j", str(job_id),
                "--format=JobID,MaxRSS,MaxVMSize,AveCPU,TotalCPU,CPUTime,ReqMem",
                "--noheader", "--parsable2"
            ])
            
            for line in output.strip().split('\n'):
                if line and not line.endswith('.batch'):
                    fields = line.split('|')
                    return {
                        'max_rss': fields[1],
                        'max_vmsize': fields[2], 
                        'avg_cpu': fields[3],
                        'total_cpu': fields[4],
                        'cpu_time': fields[5],
                        'req_mem': fields[6],
                    }
            return {}
            
        except Exception:
            return {}
    
    def list_running_jobs(self) -> List[JobStatus]:
        """List all running jobs for current user."""
        all_jobs = self.monitor.get_user_jobs()
        return [job for job in all_jobs if job.state == 'RUNNING']
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """Cancel old pending jobs (optional utility)."""
        # Implementation would depend on your cluster policies
        pass