"""
Basic usage examples for DecentralService
"""

import time
import json
from decentral_service import DecentralService, DecentralServiceClient


def example_library_usage():
    """Example using DecentralService as a library"""
    print("=== Library Usage Example ===")
    
    # Create service with 2 workers
    service = DecentralService(max_workers=2, enable_api=False)
    
    with service:
        # Storage operations
        print("1. Storage Operations:")
        service.set("config", {"debug": True, "version": "1.0"})
        service.set("user:1", {"name": "Alice", "email": "alice@example.com"}, ttl=300)
        
        config = service.get("config")
        print(f"   Config: {config}")
        
        exists = service.exists("user:1")
        print(f"   User 1 exists: {exists}")
        
        # Task processing
        print("\n2. Task Processing:")
        task_id = service.submit_task("echo", {"message": "Hello from library!"})
        print(f"   Submitted task: {task_id}")
        
        # Wait for completion
        time.sleep(1)
        status = service.get_task_status(task_id)
        print(f"   Task status: {status['status']}")
        print(f"   Task result: {status.get('result')}")
        
        # Statistics
        print("\n3. Statistics:")
        stats = service.get_stats()
        print(f"   Queue size: {stats['queue_size']}")
        print(f"   Storage size: {stats['storage_size']}")


def example_client_usage():
    """Example using DecentralServiceClient"""
    print("\n=== Client Usage Example ===")
    
    # First, start a service with API enabled
    print("Starting service with API...")
    service = DecentralService(max_workers=2, enable_api=True, port=6380)
    service.start()
    
    try:
        # Wait a moment for service to start
        time.sleep(2)
        
        # Create client
        client = DecentralServiceClient("localhost", 6380)
        
        # Test connection
        health = client.health_check()
        print(f"1. Service health: {health['status']}")
        
        # Storage operations via API
        print("\n2. Storage Operations via API:")
        client.set("api_config", {"mode": "production", "port": 6380})
        client.set("temp_data", "This will expire", ttl=60)
        
        config = client.get("api_config")
        print(f"   API Config: {config}")
        
        # Task processing via API
        print("\n3. Task Processing via API:")
        task_id = client.submit_task("math", {
            "operation": "add",
            "values": [10, 20, 30, 40]
        })
        print(f"   Submitted task: {task_id}")
        
        # Wait and check result
        time.sleep(1)
        status = client.get_task_status(task_id)
        print(f"   Task status: {status['status']}")
        print(f"   Task result: {status.get('result')}")
        
        # Get statistics
        print("\n4. Statistics via API:")
        stats = client.get_stats()
        print(f"   Service running: {stats['running']}")
        print(f"   Queue size: {stats['queue_size']}")
        
    finally:
        # Stop the service
        service.stop()
        print("\nService stopped.")


def example_custom_handlers():
    """Example with custom task handlers"""
    print("\n=== Custom Handlers Example ===")
    
    def data_processor(data, task):
        """Custom data processing handler"""
        result = {
            "original": data,
            "processed_at": time.time(),
            "task_id": task.id,
            "processed_by": "custom_handler"
        }
        
        # Simulate some processing time
        time.sleep(0.5)
        
        return result
    
    def file_processor(data, task):
        """Custom file processing handler"""
        filename = data.get("filename", "unknown")
        content = data.get("content", "")
        
        return {
            "filename": filename,
            "size": len(content),
            "lines": len(content.split('\n')),
            "processed_at": time.time()
        }
    
    service = DecentralService(max_workers=2, enable_api=False)
    
    with service:
        # Add custom handlers
        service.worker_pool.add_task_handler("data_processor", data_processor)
        service.worker_pool.add_task_handler("file_processor", file_processor)
        
        # Submit tasks with custom handlers
        print("1. Data Processing Task:")
        task1_id = service.submit_task("data_processor", {
            "user_id": 123,
            "action": "update_profile",
            "data": {"name": "John Doe", "age": 30}
        })
        
        print("2. File Processing Task:")
        task2_id = service.submit_task("file_processor", {
            "filename": "example.txt",
            "content": "Line 1\nLine 2\nLine 3\nLine 4"
        })
        
        # Wait for completion
        time.sleep(2)
        
        # Check results
        status1 = service.get_task_status(task1_id)
        status2 = service.get_task_status(task2_id)
        
        print(f"   Data processor result: {json.dumps(status1.get('result'), indent=2)}")
        print(f"   File processor result: {json.dumps(status2.get('result'), indent=2)}")


if __name__ == "__main__":
    print("DecentralService Basic Usage Examples")
    print("=" * 50)
    
    try:
        example_library_usage()
        example_client_usage()
        example_custom_handlers()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
