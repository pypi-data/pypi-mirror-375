"""
FastAPI Client Example for DecentralService Integration

This example shows how to integrate DecentralService with a FastAPI application
to handle background tasks asynchronously.

Make sure to run the server.py first before running this client.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import asyncio
from decentral_service import DecentralServiceClient

# Initialize FastAPI app
app = FastAPI(
    title="DecentralService FastAPI Client",
    description="Example FastAPI application that uses DecentralService for background tasks",
    version="1.0.0"
)

# Initialize DecentralService client
client = DecentralServiceClient("localhost", 6380)

# Pydantic models for request/response
class TaskRequest(BaseModel):
    message: str
    priority: Optional[int] = 0

class TaskResponse(BaseModel):
    status: str
    message: str
    task_id: str
    api_response_time: float
    note: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "DecentralService FastAPI Client",
        "version": "1.0.0",
        "endpoints": {
            "test_hidden_tasks": "/test-hidden-tasks",
            "test_custom_task_id": "/test-custom-task-id",
            "test_duplicate_id": "/test-duplicate-id",
            "process_data": "/process-data",
            "check_task": "/check-task/{task_id}",
            "task_detail": "/task-detail/{task_id}",
            "check_task_id": "/check-task-id/{task_id}",
            "search_tasks": "/search-tasks",
            "list_tasks": "/list-tasks",
            "health": "/health",
            "service_stats": "/service-stats",
            "queue_info": "/queue-info"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if DecentralService is running
        health = client.health_check()
        return {
            "status": "healthy",
            "decentral_service": health,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DecentralService not available: {str(e)}")

@app.post("/test-hidden-tasks", response_model=TaskResponse)
async def test_hidden_tasks(request: TaskRequest):
    """
    Test endpoint for hidden tasks.
    
    This endpoint demonstrates how to submit a background task to DecentralService
    and return immediately without waiting for the task to complete.
    """
    start_time = time.time()
    
    try:
        # Submit task - this returns immediately!
        task_id = client.submit_task(
            "sleep_and_create_file",  # Use the registered handler name
            {"message": request.message},  # Just the data, no function call
            priority=request.priority
        )
        
        end_time = time.time()
        
        print(f"Task submitted: {task_id}")
        
        return TaskResponse(
            status="success",
            message="Task submitted successfully",
            task_id=task_id,
            api_response_time=end_time - start_time,  # Should be < 1 second
            note="Task is processing in background"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@app.post("/test-custom-task-id", response_model=TaskResponse)
async def test_custom_task_id(request: TaskRequest, custom_id: str = None, overwrite: bool = True):
    """
    Test endpoint for custom task IDs with overwrite control.
    
    This endpoint demonstrates how to submit a task with a custom ID and control overwrite behavior.
    """
    start_time = time.time()
    
    try:
        # Generate custom task ID if not provided
        if custom_id is None:
            custom_id = f"custom_task_{int(time.time() * 1000)}"
        
        # Submit task with custom ID and overwrite control
        task_id = client.submit_task(
            "sleep_and_create_file",
            {"message": request.message},
            priority=request.priority,
            task_id=custom_id,
            overwrite=overwrite
        )
        
        end_time = time.time()
        
        print(f"Task submitted with custom ID: {task_id} (overwrite={overwrite})")
        
        return TaskResponse(
            status="success",
            message="Task submitted successfully with custom ID",
            task_id=task_id,
            api_response_time=end_time - start_time,
            note=f"Custom task ID: {custom_id}, Overwrite: {overwrite}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@app.post("/process-data", response_model=TaskResponse)
async def process_data(data: Dict[str, Any], operation: str = "process"):
    """
    Example endpoint for data processing tasks
    """
    start_time = time.time()
    
    try:
        task_id = client.submit_task(
            "process_data",
            {"data": data, "operation": operation}
        )
        
        end_time = time.time()
        
        return TaskResponse(
            status="success",
            message="Data processing task submitted",
            task_id=task_id,
            api_response_time=end_time - start_time,
            note="Data is being processed in background"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit data processing task: {str(e)}")

@app.get("/check-task/{task_id}", response_model=TaskStatusResponse)
async def check_task_status(task_id: str):
    """Check the status of a submitted task"""
    try:
        status = client.get_task_status(task_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskStatusResponse(
            task_id=task_id,
            status=status.get("status", "unknown"),
            result=status.get("result"),
            created_at=status.get("created_at")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@app.get("/task-detail/{task_id}")
async def get_task_detail(task_id: str):
    """Get detailed information about a specific task"""
    try:
        detail = client.get_task_detail(task_id)
        
        if detail is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return detail
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task detail: {str(e)}")

@app.get("/search-tasks")
async def search_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Search tasks with filters"""
    try:
        result = client.search_tasks(
            status=status,
            task_type=task_type,
            limit=limit,
            offset=offset
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search tasks: {str(e)}")

@app.get("/list-tasks")
async def list_tasks(
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """List tasks with pagination and sorting"""
    try:
        result = client.list_tasks(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")

@app.get("/check-task-id/{task_id}")
async def check_task_id_availability(task_id: str):
    """Check if a task ID is available for use"""
    try:
        status = client.get_task_id_status(task_id)
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check task ID: {str(e)}")

@app.post("/test-duplicate-id")
async def test_duplicate_id(request: TaskRequest, task_id: str, overwrite: bool = True):
    """Test endpoint to demonstrate duplicate ID handling with overwrite control"""
    try:
        # First, check if ID is available
        id_status = client.get_task_id_status(task_id)
        
        if not id_status.get("available", True) and not overwrite:
            return {
                "error": "Task ID conflict",
                "message": f"Task ID '{task_id}' is already in use and overwrite is disabled",
                "existing_status": id_status.get("status"),
                "created_at": id_status.get("created_at"),
                "overwrite": overwrite
            }
        
        # Submit task with the ID and overwrite control
        submitted_id = client.submit_task(
            "sleep_and_create_file",
            {"message": request.message},
            priority=request.priority,
            task_id=task_id,
            overwrite=overwrite
        )
        
        return {
            "status": "success",
            "message": "Task submitted successfully",
            "task_id": submitted_id,
            "overwrite": overwrite,
            "note": "Overwrite mode" if overwrite else "Block mode"
        }
        
    except Exception as e:
        return {
            "error": "Failed to submit task",
            "message": str(e),
            "task_id": task_id,
            "overwrite": overwrite
        }

@app.get("/service-stats")
async def get_service_stats():
    """Get DecentralService statistics"""
    try:
        stats = client.get_stats()
        queue_stats = client.get_queue_stats()
        worker_stats = client.get_worker_stats()
        
        return {
            "service_stats": stats,
            "queue_stats": queue_stats,
            "worker_stats": worker_stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get service stats: {str(e)}")

@app.get("/queue-info")
async def get_queue_info():
    """Get queue information"""
    try:
        queue_size = client.get_queue_size()
        queue_stats = client.get_queue_stats()
        
        return {
            "queue_size": queue_size,
            "queue_stats": queue_stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue info: {str(e)}")

# Background task to monitor service health
@app.on_event("startup")
async def startup_event():
    """Startup event to check service connection"""
    print("FastAPI Client starting...")
    try:
        health = client.health_check()
        print(f"Connected to DecentralService: {health['status']}")
    except Exception as e:
        print(f"Warning: Could not connect to DecentralService: {e}")
        print("Make sure the server is running on localhost:6380")

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI client on http://localhost:8000")
    print("Make sure DecentralService server is running on localhost:6380")
    uvicorn.run(app, host="0.0.0.0", port=8000)
