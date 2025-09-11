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
            "check_task": "/check-task/{task_id}",
            "health": "/health",
            "service_stats": "/service-stats"
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
