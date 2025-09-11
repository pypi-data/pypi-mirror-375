"""Example training script for CLI demonstration."""

import os
import time
import json
from pathlib import Path


def main():
    """Main training function."""
    print("🚀 Starting training job...")
    
    # Get configuration from environment or app config
    app_config_path = os.getenv('APP_CONFIG_PATH')
    
    if app_config_path:
        print(f"📋 Loading app config from: {app_config_path}")
        # In a real script, you'd load your training config here
    
    # Simulate distributed training environment
    world_size = os.getenv('WORLD_SIZE', '1')
    node_rank = os.getenv('NODE_RANK', '0')
    local_rank = os.getenv('LOCAL_RANK', '0')
    master_addr = os.getenv('MASTER_ADDR', 'localhost')
    
    print(f"🌍 Distributed training setup:")
    print(f"  World size: {world_size}")
    print(f"  Node rank: {node_rank}")
    print(f"  Local rank: {local_rank}")
    print(f"  Master addr: {master_addr}")
    
    # Simulate training loop
    num_epochs = 5
    for epoch in range(num_epochs):
        print(f"📈 Epoch {epoch + 1}/{num_epochs}")
        
        # Simulate training steps
        for step in range(10):
            # Simulate training time
            time.sleep(2)
            
            loss = 2.5 * (0.9 ** (epoch * 10 + step))
            accuracy = min(0.95, 0.3 + (epoch * 10 + step) * 0.01)
            
            if step % 3 == 0:  # Log every 3 steps
                print(f"  Step {step}: loss={loss:.4f}, accuracy={accuracy:.4f}")
        
        print(f"✅ Epoch {epoch + 1} completed")
        
        # Simulate checkpoint saving
        if epoch % 2 == 0:
            checkpoint_dir = Path("./checkpoints")
            checkpoint_dir.mkdir(exist_ok=True)
            
            checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.json"
            checkpoint_data = {
                "epoch": epoch,
                "loss": loss,
                "accuracy": accuracy,
                "model_state": "saved"
            }
            
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            print(f"💾 Checkpoint saved: {checkpoint_path}")
    
    print("🎉 Training completed successfully!")
    
    # Save final results
    results = {
        "final_loss": loss,
        "final_accuracy": accuracy,
        "num_epochs": num_epochs,
        "distributed": world_size != '1'
    }
    
    with open("training_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Final results: loss={loss:.4f}, accuracy={accuracy:.4f}")
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)