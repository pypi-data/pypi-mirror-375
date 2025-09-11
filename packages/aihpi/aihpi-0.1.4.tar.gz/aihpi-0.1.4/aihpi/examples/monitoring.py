"""Examples for job monitoring and experiment tracking."""

import time
from pathlib import Path
from aihpi import (
    SlurmJobExecutor, JobConfig, ContainerConfig,
    JobMonitor, JobManager, 
    ExperimentManager, create_tracker
)


def example_job_monitoring():
    """Example: Monitor a running job."""
    # Setup job monitoring
    monitor = JobMonitor(login_node="10.130.0.6")  # Optional SSH
    
    # Submit a job first
    config = JobConfig(
        job_name="monitored-job",
        num_nodes=1,
        gpus_per_node=1,
        walltime="00:30:00"
    )
    
    executor = SlurmJobExecutor(config)
    
    def long_running_task():
        import time
        for i in range(10):
            print(f"Training step {i}")
            time.sleep(30)  # Simulate training
        return "Training completed"
    
    job = executor.submit_function(long_running_task)
    print(f"Submitted job: {job.job_id}")
    
    # Monitor job status
    while True:
        status = monitor.get_job_status(job.job_id)
        if status:
            print(f"Job {job.job_id}: {status.state} (elapsed: {status.time_elapsed})")
            
            if status.state in ['COMPLETED', 'FAILED', 'CANCELLED']:
                break
        
        time.sleep(30)
    
    # Get final resource usage
    manager = JobManager(monitor)
    usage = manager.get_resource_usage(job.job_id)
    print(f"Resource usage: {usage}")


def example_log_streaming():
    """Example: Stream job logs in real-time."""
    config = JobConfig(job_name="log-streaming-example")
    executor = SlurmJobExecutor(config)
    
    def chatty_job():
        import time
        for i in range(20):
            print(f"Log message {i}: Processing data...")
            if i % 5 == 0:
                print(f"Checkpoint at step {i}", flush=True)
            time.sleep(10)
        return "Job completed"
    
    job = executor.submit_function(chatty_job)
    
    # Stream logs
    monitor = JobMonitor()
    try:
        for log_line in monitor.stream_logs(job.paths, follow=True):
            print(log_line)
    except KeyboardInterrupt:
        print("Stopped log streaming")


def example_experiment_tracking_wandb():
    """Example: Job with Weights & Biases tracking."""
    
    # Create WandB tracker
    tracker = create_tracker("wandb", project="aihpi-demo", entity="your-team")
    exp_manager = ExperimentManager(tracker)
    
    # Job configuration
    config = JobConfig(
        job_name="wandb-experiment",
        num_nodes=2,
        gpus_per_node=1,
        walltime="01:00:00",
        env_vars={"WANDB_PROJECT": "aihpi-demo"}
    )
    
    executor = SlurmJobExecutor(config)
    
    def training_with_wandb():
        import os
        import random
        
        # Start experiment (this would typically be in your training script)
        run_id = exp_manager.start_experiment("llama-finetuning", {
            "model": "llama-3-8b",
            "batch_size": 32,
            "learning_rate": 1e-4,
            "num_epochs": 10,
            "nodes": os.getenv("WORLD_SIZE", "1")
        })
        
        try:
            # Simulate training loop
            for epoch in range(10):
                # Simulate metrics
                train_loss = 2.5 * (0.9 ** epoch) + random.uniform(-0.1, 0.1)
                val_loss = train_loss + random.uniform(0, 0.3)
                accuracy = min(0.95, 0.3 + 0.07 * epoch + random.uniform(-0.02, 0.02))
                
                exp_manager.log_training_metrics(
                    epoch=epoch,
                    train_loss=train_loss,
                    val_loss=val_loss,
                    accuracy=accuracy,
                    learning_rate=1e-4 * (0.95 ** epoch)
                )
                
                print(f"Epoch {epoch}: train_loss={train_loss:.3f}, val_loss={val_loss:.3f}, acc={accuracy:.3f}")
                
                # Simulate checkpoint saving
                if epoch % 3 == 0:
                    checkpoint_path = f"/tmp/checkpoint_epoch_{epoch}"
                    Path(checkpoint_path).mkdir(exist_ok=True)
                    Path(checkpoint_path + "/model.pt").touch()
                    exp_manager.log_model_checkpoint(checkpoint_path)
            
            exp_manager.finish_experiment("completed")
            return "Training completed successfully"
            
        except Exception as e:
            exp_manager.finish_experiment("failed")
            raise e
    
    job = executor.submit_distributed_training(training_with_wandb)
    return job


def example_experiment_tracking_mlflow():
    """Example: Job with MLflow tracking."""
    
    # Create MLflow tracker
    tracker = create_tracker("mlflow", 
                           experiment_name="aihpi-experiments",
                           tracking_uri="http://mlflow-server:5000")  # Optional remote server
    exp_manager = ExperimentManager(tracker)
    
    config = JobConfig(
        job_name="mlflow-experiment", 
        num_nodes=1,
        gpus_per_node=2,
        walltime="02:00:00"
    )
    
    executor = SlurmJobExecutor(config)
    
    def training_with_mlflow():
        import random
        import json
        from pathlib import Path
        
        # Start experiment
        run_id = exp_manager.start_experiment("distributed-training", {
            "architecture": "transformer",
            "model_size": "7B",
            "dataset": "custom-data",
            "batch_size": 64,
            "gradient_accumulation": 4,
            "optimizer": "AdamW",
            "scheduler": "cosine"
        })
        
        # Simulate training
        best_val_loss = float('inf')
        
        for epoch in range(15):
            # Training metrics
            train_loss = 3.2 * (0.88 ** epoch) + random.uniform(-0.15, 0.15)
            val_loss = train_loss + random.uniform(0, 0.4)
            perplexity = 2 ** val_loss
            
            exp_manager.log_training_metrics(
                epoch=epoch,
                train_loss=train_loss,
                val_loss=val_loss,
                perplexity=perplexity,
                gpu_memory_gb=random.uniform(12, 16)
            )
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                model_dir = Path("/tmp/best_model")
                model_dir.mkdir(exist_ok=True)
                
                # Create dummy model files
                (model_dir / "pytorch_model.bin").touch()
                (model_dir / "config.json").write_text(json.dumps({"model_type": "llama"}))
                
                exp_manager.log_model_checkpoint(model_dir)
                print(f"New best model at epoch {epoch}: val_loss={val_loss:.3f}")
        
        exp_manager.finish_experiment("completed")
        return f"Training completed. Best val_loss: {best_val_loss:.3f}"
    
    job = executor.submit_function(training_with_mlflow)
    return job


def example_local_experiment_tracking():
    """Example: Simple local experiment tracking."""
    
    # Create local tracker
    tracker = create_tracker("local", log_dir="./experiments")
    exp_manager = ExperimentManager(tracker)
    
    config = JobConfig(job_name="local-experiment")
    executor = SlurmJobExecutor(config)
    
    def training_with_local_tracking():
        import random
        import json
        from pathlib import Path
        
        # Start experiment
        run_id = exp_manager.start_experiment("local-test", {
            "model": "small-transformer",
            "layers": 12,
            "heads": 8,
            "embedding_dim": 512
        })
        
        print(f"Started local experiment: {run_id}")
        
        # Simulate training
        for step in range(100):
            loss = 4.0 * (0.98 ** step) + random.uniform(-0.1, 0.1)
            
            if step % 10 == 0:  # Log every 10 steps
                exp_manager.log_training_metrics(
                    step=step,
                    loss=loss,
                    learning_rate=1e-3 * (0.99 ** (step // 50))
                )
                print(f"Step {step}: loss={loss:.3f}")
        
        # Save final model
        model_path = Path("/tmp/final_model")
        model_path.mkdir(exist_ok=True)
        (model_path / "model.json").write_text(json.dumps({"final_loss": loss}))
        
        exp_manager.log_model_checkpoint(model_path)
        exp_manager.finish_experiment("completed")
        
        return f"Local experiment completed: {run_id}"
    
    job = executor.submit_function(training_with_local_tracking)
    return job


def example_comprehensive_monitoring():
    """Example: Comprehensive job monitoring with experiment tracking."""
    
    # Setup both monitoring and tracking
    monitor = JobMonitor()
    tracker = create_tracker("local", log_dir="monitored_experiments")
    exp_manager = ExperimentManager(tracker)
    
    config = JobConfig(
        job_name="comprehensive-example",
        num_nodes=2,
        gpus_per_node=1,
        walltime="01:00:00"
    )
    
    executor = SlurmJobExecutor(config)
    
    def comprehensive_job():
        import random
        import time
        
        # Start experiment tracking
        run_id = exp_manager.start_experiment("comprehensive-training", {
            "nodes": 2,
            "gpus_per_node": 1,
            "total_gpus": 2
        })
        
        try:
            for epoch in range(20):
                # Simulate training
                loss = 2.8 * (0.9 ** epoch) + random.uniform(-0.1, 0.1)
                
                exp_manager.log_training_metrics(
                    epoch=epoch,
                    loss=loss,
                    throughput=random.uniform(1000, 1200)
                )
                
                print(f"Epoch {epoch}: loss={loss:.3f}")
                time.sleep(10)  # Simulate training time
            
            exp_manager.finish_experiment("completed")
            return "Comprehensive training completed"
            
        except Exception as e:
            exp_manager.finish_experiment("failed")
            raise e
    
    # Submit and monitor
    job = executor.submit_distributed_training(comprehensive_job)
    print(f"Submitted comprehensive job: {job.job_id}")
    
    # Monitor in background (you could run this in a separate script)
    final_status = monitor.wait_for_job(job.job_id, poll_interval=60)
    print(f"Job finished with status: {final_status.state}")
    
    return job


if __name__ == "__main__":
    print("aihpi Monitoring & Tracking Examples")
    print("====================================")
    
    examples = {
        "1": ("Job monitoring", example_job_monitoring),
        "2": ("Log streaming", example_log_streaming), 
        "3": ("Weights & Biases tracking", example_experiment_tracking_wandb),
        "4": ("MLflow tracking", example_experiment_tracking_mlflow),
        "5": ("Local tracking", example_local_experiment_tracking),
        "6": ("Comprehensive monitoring", example_comprehensive_monitoring),
    }
    
    for key, (name, func) in examples.items():
        print(f"{key}. {name}")
    
    print("\nImport and run examples:")
    print("from aihpi.examples_monitoring import example_job_monitoring")
    print("job = example_job_monitoring()")