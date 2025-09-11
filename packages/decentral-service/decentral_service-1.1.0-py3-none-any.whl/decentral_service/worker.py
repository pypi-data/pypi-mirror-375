"""
Multi-threaded worker pool for task processing
"""

import threading
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from .queue import TaskQueue, Task, TaskStatus


class Worker:
    """Individual worker thread"""
    
    def __init__(self, worker_id: int, task_queue: TaskQueue, 
                 task_handlers: Dict[str, Callable] = None):
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.task_handlers = task_handlers or {}
        self.thread = None
        self.running = False
        self.current_task = None
        self.logger = logging.getLogger(f"Worker-{worker_id}")
        
        # Statistics
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.start_time = None
    
    def start(self):
        """Start the worker thread"""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info(f"Worker {self.worker_id} started")
    
    def stop(self):
        """Stop the worker thread"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.logger.info(f"Worker {self.worker_id} stopped")
    
    def _run(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get next task
                task = self.task_queue.dequeue(timeout=1.0)
                if not task:
                    continue
                
                self.current_task = task
                self.logger.info(f"Worker {self.worker_id} processing task {task.id}")
                
                # Process the task
                success = self._process_task(task)
                
                if success:
                    self.tasks_processed += 1
                    self.task_queue.complete_task(task.id, task.result)
                    self.logger.info(f"Worker {self.worker_id} completed task {task.id}")
                else:
                    self.tasks_failed += 1
                    self.task_queue.fail_task(task.id, task.error or "Unknown error")
                    self.logger.error(f"Worker {self.worker_id} failed task {task.id}: {task.error}")
                
                self.current_task = None
                
            except Exception as e:
                self.logger.error(f"Worker {self.worker_id} error: {e}")
                if self.current_task:
                    self.task_queue.fail_task(self.current_task.id, str(e))
                    self.current_task = None
                time.sleep(1)  # Brief pause on error
    
    def _process_task(self, task: Task) -> bool:
        """Process a single task"""
        try:
            # Get handler for task type
            handler = self.task_handlers.get(task.type)
            if not handler:
                # Default handler - just return the data
                task.result = task.data
                return True
            
            # Execute handler
            if callable(handler):
                result = handler(task.data, task)
                task.result = result
                return True
            else:
                task.error = f"Invalid handler for task type: {task.type}"
                return False
                
        except Exception as e:
            task.error = str(e)
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            "worker_id": self.worker_id,
            "running": self.running,
            "current_task": self.current_task.id if self.current_task else None,
            "tasks_processed": self.tasks_processed,
            "tasks_failed": self.tasks_failed,
            "uptime": uptime,
            "tasks_per_second": self.tasks_processed / uptime if uptime > 0 else 0
        }


class WorkerPool:
    """Pool of worker threads for task processing"""
    
    def __init__(self, max_workers: int = 4, task_queue: TaskQueue = None,
                 task_handlers: Dict[str, Callable] = None):
        self.max_workers = max_workers
        self.task_queue = task_queue or TaskQueue()
        self.task_handlers = task_handlers or {}
        self.workers: List[Worker] = []
        self.running = False
        self.logger = logging.getLogger("WorkerPool")
        
        # Create workers
        for i in range(max_workers):
            worker = Worker(i, self.task_queue, self.task_handlers)
            self.workers.append(worker)
    
    def start(self):
        """Start all workers"""
        if self.running:
            return
        
        self.running = True
        for worker in self.workers:
            worker.start()
        
        self.logger.info(f"Worker pool started with {len(self.workers)} workers")
    
    def stop(self):
        """Stop all workers"""
        if not self.running:
            return
        
        self.running = False
        for worker in self.workers:
            worker.stop()
        
        self.logger.info("Worker pool stopped")
    
    def add_task_handler(self, task_type: str, handler: Callable):
        """Add a task handler for a specific task type"""
        self.task_handlers[task_type] = handler
        # Update all workers
        for worker in self.workers:
            worker.task_handlers[task_type] = handler
        self.logger.info(f"Added task handler for type: {task_type}")
    
    def remove_task_handler(self, task_type: str):
        """Remove a task handler"""
        if task_type in self.task_handlers:
            del self.task_handlers[task_type]
            # Update all workers
            for worker in self.workers:
                worker.task_handlers.pop(task_type, None)
            self.logger.info(f"Removed task handler for type: {task_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics"""
        worker_stats = [worker.get_stats() for worker in self.workers]
        total_processed = sum(w.tasks_processed for w in self.workers)
        total_failed = sum(w.tasks_failed for w in self.workers)
        
        return {
            "running": self.running,
            "max_workers": self.max_workers,
            "active_workers": len([w for w in self.workers if w.running]),
            "total_tasks_processed": total_processed,
            "total_tasks_failed": total_failed,
            "success_rate": total_processed / (total_processed + total_failed) if (total_processed + total_failed) > 0 else 0,
            "workers": worker_stats
        }
    
    def get_worker_stats(self, worker_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific worker"""
        if 0 <= worker_id < len(self.workers):
            return self.workers[worker_id].get_stats()
        return None


# Built-in task handlers
def default_task_handler(data: Any, task: Task) -> Any:
    """Default task handler that just returns the data"""
    return data


def echo_task_handler(data: Any, task: Task) -> Any:
    """Echo handler that returns the data with metadata"""
    return {
        "original_data": data,
        "task_id": task.id,
        "processed_at": time.time(),
        "worker_id": getattr(task, 'worker_id', 'unknown')
    }


def delay_task_handler(data: Any, task: Task) -> Any:
    """Delay handler that sleeps for the specified duration"""
    delay = data.get('delay', 1) if isinstance(data, dict) else 1
    time.sleep(delay)
    return {"delayed_for": delay, "original_data": data}


def math_task_handler(data: Any, task: Task) -> Any:
    """Math handler that performs basic arithmetic operations"""
    if not isinstance(data, dict):
        return {"error": "Data must be a dictionary with 'operation' and 'values'"}
    
    operation = data.get('operation')
    values = data.get('values', [])
    
    if not isinstance(values, list) or len(values) < 2:
        return {"error": "Values must be a list with at least 2 numbers"}
    
    try:
        if operation == 'add':
            result = sum(values)
        elif operation == 'multiply':
            result = 1
            for v in values:
                result *= v
        elif operation == 'subtract':
            result = values[0] - sum(values[1:])
        elif operation == 'divide':
            result = values[0]
            for v in values[1:]:
                result /= v
        else:
            return {"error": f"Unknown operation: {operation}"}
        
        return {"operation": operation, "values": values, "result": result}
    
    except Exception as e:
        return {"error": str(e)}


# Default task handlers
DEFAULT_TASK_HANDLERS = {
    "default": default_task_handler,
    "echo": echo_task_handler,
    "delay": delay_task_handler,
    "math": math_task_handler
}
