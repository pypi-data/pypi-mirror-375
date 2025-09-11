"""
Thread-safe task queue system with priority support
"""

import threading
import time
import heapq
import uuid
import logging
from typing import Any, Dict, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task data structure"""
    id: str
    type: str
    data: Any
    callback: Optional[Callable] = None
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """For priority queue ordering (higher priority first)"""
        return self.priority > other.priority


class TaskQueue:
    """
    Thread-safe priority queue for task management
    """
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize task queue
        
        Args:
            max_size: Maximum number of tasks in queue
        """
        self.max_size = max_size
        self._queue: List[Task] = []
        self._tasks: Dict[str, Task] = {}  # Task ID -> Task mapping
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self.logger = logging.getLogger(__name__)
        self._stats = {
            "total_enqueued": 0,
            "total_processed": 0,
            "total_failed": 0,
            "total_cancelled": 0
        }
    
    def enqueue(self, task_data: Dict[str, Any]) -> str:
        """
        Add a task to the queue
        
        Args:
            task_data: Task data dictionary
        
        Returns:
            Task ID
        """
        with self._condition:
            if len(self._queue) >= self.max_size:
                raise RuntimeError(f"Queue is full (max size: {self.max_size})")
            
            # Generate task ID if not provided
            task_id = task_data.get("id", str(uuid.uuid4()))
            
            # Check for duplicate task ID
            if task_id in self._tasks:
                existing_task = self._tasks[task_id]
                overwrite_mode = task_data.get("overwrite", True)
                
                # Check if existing task is still active (not completed/failed/cancelled)
                if existing_task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]:
                    if overwrite_mode:
                        # Overwrite mode: Remove existing task and continue
                        self.logger.info(f"Overwriting existing task '{task_id}' (status: {existing_task.status.value})")
                        # Remove old task from queue if it exists
                        try:
                            self._queue.remove(existing_task)
                            heapq.heapify(self._queue)
                        except ValueError:
                            pass  # Task not in queue (already processed)
                        # Update stats
                        self._stats["total_cancelled"] += 1
                    else:
                        # Block mode: Raise error
                        raise ValueError(f"Task ID '{task_id}' already exists and is active (status: {existing_task.status.value})")
                # If task is completed/failed/cancelled, we can always reuse the ID
                else:
                    # Remove old task from queue if it exists
                    try:
                        self._queue.remove(existing_task)
                        heapq.heapify(self._queue)
                    except ValueError:
                        pass  # Task not in queue (already processed)
            
            # Create task object
            task = Task(
                id=task_id,
                type=task_data.get("type", "default"),
                data=task_data.get("data"),
                callback=task_data.get("callback"),
                priority=task_data.get("priority", 0),
                max_retries=task_data.get("max_retries", 3)
            )
            
            # Add to queue and task registry
            heapq.heappush(self._queue, task)
            self._tasks[task_id] = task
            self._stats["total_enqueued"] += 1
            
            # Notify waiting threads
            self._condition.notify()
            
            return task_id
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Task]:
        """
        Get next task from queue
        
        Args:
            timeout: Maximum time to wait for a task
        
        Returns:
            Next task or None if timeout/empty
        """
        with self._condition:
            if timeout is None:
                # Wait indefinitely
                while not self._queue:
                    self._condition.wait()
            else:
                # Wait with timeout
                if not self._queue:
                    self._condition.wait(timeout)
            
            if self._queue:
                task = heapq.heappop(self._queue)
                task.status = TaskStatus.PROCESSING
                task.started_at = time.time()
                return task
            
            return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status information"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "type": task.type,
            "status": task.status.value,
            "priority": task.priority,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "retry_count": task.retry_count,
            "error": task.error,
            "result": task.result
        }
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark task as completed"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.result = result
            self._stats["total_processed"] += 1
            
            # Execute callback if provided
            if task.callback:
                try:
                    task.callback(task)
                except Exception as e:
                    print(f"Error in task callback: {e}")
            
            return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            task.error = error
            self._stats["total_failed"] += 1
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                task.completed_at = None
                task.error = None
                
                # Re-enqueue for retry
                heapq.heappush(self._queue, task)
                with self._condition:
                    self._condition.notify()
            
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if task.status == TaskStatus.PENDING:
                # Remove from queue
                try:
                    self._queue.remove(task)
                    heapq.heapify(self._queue)
                except ValueError:
                    pass  # Task not in queue
            
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self._stats["total_cancelled"] += 1
            
            return True
    
    def size(self) -> int:
        """Get current queue size"""
        with self._lock:
            return len(self._queue)
    
    def empty(self) -> bool:
        """Check if queue is empty"""
        with self._lock:
            return len(self._queue) == 0
    
    def clear(self) -> int:
        """Clear all pending tasks"""
        with self._lock:
            cleared_count = len(self._queue)
            self._queue.clear()
            # Keep completed/failed tasks in registry for status checking
            return cleared_count
    
    def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific task"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None
            
            return {
                "id": task.id,
                "type": task.type,
                "data": task.data,
                "status": task.status.value,
                "priority": task.priority,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "execution_time": task.execution_time,
                "result": task.result,
                "error": task.error,
                "retry_count": task.retry_count,
                "max_retries": task.max_retries,
                "worker_id": getattr(task, 'worker_id', None)
            }
    
    def search_tasks(self, 
                    status: Optional[str] = None,
                    task_type: Optional[str] = None,
                    limit: int = 100,
                    offset: int = 0) -> Dict[str, Any]:
        """Search tasks with filters"""
        with self._lock:
            # Filter tasks
            filtered_tasks = []
            for task in self._tasks.values():
                # Apply status filter
                if status and task.status.value != status:
                    continue
                
                # Apply task type filter
                if task_type and task.type != task_type:
                    continue
                
                filtered_tasks.append(task)
            
            # Sort by created_at (newest first)
            filtered_tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            # Apply pagination
            total_count = len(filtered_tasks)
            paginated_tasks = filtered_tasks[offset:offset + limit]
            
            # Convert to dictionaries
            tasks_data = []
            for task in paginated_tasks:
                tasks_data.append({
                    "id": task.id,
                    "type": task.type,
                    "status": task.status.value,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "execution_time": task.execution_time,
                    "retry_count": task.retry_count
                })
            
            return {
                "tasks": tasks_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
    
    def list_tasks(self, 
                  limit: int = 50, 
                  offset: int = 0,
                  sort_by: str = "created_at",
                  sort_order: str = "desc") -> Dict[str, Any]:
        """List tasks with pagination and sorting"""
        with self._lock:
            # Get all tasks
            all_tasks = list(self._tasks.values())
            
            # Sort tasks
            reverse = sort_order.lower() == "desc"
            if sort_by == "created_at":
                all_tasks.sort(key=lambda t: t.created_at, reverse=reverse)
            elif sort_by == "priority":
                all_tasks.sort(key=lambda t: t.priority, reverse=reverse)
            elif sort_by == "status":
                all_tasks.sort(key=lambda t: t.status.value, reverse=reverse)
            else:
                # Default to created_at
                all_tasks.sort(key=lambda t: t.created_at, reverse=reverse)
            
            # Apply pagination
            total_count = len(all_tasks)
            paginated_tasks = all_tasks[offset:offset + limit]
            
            # Convert to dictionaries
            tasks_data = []
            for task in paginated_tasks:
                tasks_data.append({
                    "id": task.id,
                    "type": task.type,
                    "status": task.status.value,
                    "priority": task.priority,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "execution_time": task.execution_time,
                    "retry_count": task.retry_count,
                    "worker_id": getattr(task, 'worker_id', None)
                })
            
            return {
                "tasks": tasks_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count,
                "sort_by": sort_by,
                "sort_order": sort_order
            }

    def is_task_id_available(self, task_id: str) -> bool:
        """Check if a task ID is available for use"""
        with self._lock:
            if task_id not in self._tasks:
                return True
            
            existing_task = self._tasks[task_id]
            # ID is available if task is completed, failed, or cancelled
            return existing_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def get_task_id_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task ID (whether it exists and its current status)"""
        with self._lock:
            if task_id not in self._tasks:
                return {"exists": False, "available": True}
            
            existing_task = self._tasks[task_id]
            return {
                "exists": True,
                "available": existing_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED],
                "status": existing_task.status.value,
                "created_at": existing_task.created_at
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self._lock:
            return {
                "queue_size": len(self._queue),
                "total_tasks": len(self._tasks),
                "pending_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.PENDING]),
                "processing_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.PROCESSING]),
                "completed_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]),
                "failed_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.FAILED]),
                "cancelled_tasks": len([t for t in self._tasks.values() if t.status == TaskStatus.CANCELLED]),
                **self._stats
            }
    
    def cleanup_old_tasks(self, max_age_seconds: int = 3600) -> int:
        """
        Remove old completed/failed tasks to free memory
        
        Args:
            max_age_seconds: Maximum age of tasks to keep
        
        Returns:
            Number of tasks cleaned up
        """
        with self._lock:
            current_time = time.time()
            to_remove = []
            
            for task_id, task in self._tasks.items():
                if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                    task.completed_at and
                    current_time - task.completed_at > max_age_seconds):
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self._tasks[task_id]
            
            return len(to_remove)
