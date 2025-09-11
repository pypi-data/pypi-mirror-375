"""
DecentralService Server Example for FastAPI Integration

This example shows how to set up a DecentralService server with custom task handlers
that can be called from a FastAPI client application.

Run this server first, then run the client.py example.
"""

from decentral_service import DecentralService
import time
import json
import os
from datetime import datetime

def sleep_then_create_json_file_handler(data, task):
    """
    Custom task handler that sleeps then creates JSON file
    
    This handler demonstrates:
    - Long-running background tasks
    - File I/O operations
    - Task metadata and results
    """
    message = data.get("message", "default")
    task_id = task.id
    
    print(f"[Worker] Starting task {task_id} with message: {message}")
    
    # This sleep happens in the DecentralService worker, not your API
    # This simulates a long-running background task
    time.sleep(10)
    
    # Create the JSON file with timestamp and task info
    result_data = {
        "message": message,
        "task_id": task_id,
        "created_at": datetime.now().isoformat(),
        "processed_by": "DecentralService Worker",
        "status": "completed"
    }
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the JSON file
    filename = f"{output_dir}/task_{task_id}.json"
    with open(filename, "w") as f:
        json.dump(result_data, f, indent=2)
    
    print(f"[Worker] Task {task_id} completed. File created: {filename}")
    
    return {
        "status": "completed",
        "message": f"File created with message: {message}",
        "task_id": task_id,
        "filename": filename,
        "created_at": result_data["created_at"]
    }

def process_data_handler(data, task):
    """
    Another example handler for data processing tasks
    """
    input_data = data.get("data", {})
    operation = data.get("operation", "process")
    
    print(f"[Worker] Processing data for task {task.id}")
    
    # Simulate some processing time
    time.sleep(2)
    
    # Process the data
    processed_data = {
        "original": input_data,
        "operation": operation,
        "processed_at": datetime.now().isoformat(),
        "task_id": task.id,
        "result": f"Processed {len(str(input_data))} characters of data"
    }
    
    return processed_data

def main():
    """Start the DecentralService server"""
    print("Starting DecentralService Server...")
    print("=" * 50)
    
    # Create and configure the service
    service = DecentralService(
        max_workers=4,          # Number of worker threads
        enable_api=True,        # Enable HTTP API
        port=6380,             # API port
        host="localhost"        # API host
    )
    
    # Add custom task handlers
    service.worker_pool.add_task_handler("sleep_and_create_file", sleep_then_create_json_file_handler)
    service.worker_pool.add_task_handler("process_data", process_data_handler)
    
    # Start the service
    service.start()
    
    print("DecentralService started successfully!")
    print(f"API available at: http://localhost:6380")
    print("Available endpoints:")
    print("  GET  /health")
    print("  GET  /stats")
    print("  POST /tasks")
    print("  GET  /queue/stats")
    print("\nRegistered task handlers:")
    print("  - sleep_and_create_file")
    print("  - process_data")
    print("\nPress Ctrl+C to stop...")
    print("=" * 50)
    
    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down DecentralService...")
        service.stop()
        print("Service stopped.")

if __name__ == "__main__":
    main()
