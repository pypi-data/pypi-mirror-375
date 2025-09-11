"""
Core DecentralService class that orchestrates all components
"""

import threading
import time
import logging
from typing import Any, Dict, Optional, Callable, Union
from .storage import StorageEngine
from .queue import TaskQueue
from .worker import WorkerPool
from .api import APIServer


class DecentralService:
    """
    Main service class that provides Redis-like functionality with multi-threading support
    """
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 6379,
                 max_workers: int = 4,
                 enable_api: bool = True,
                 log_level: str = "INFO"):
        """
        Initialize the DecentralService
        
        Args:
            host: Host address for API server
            port: Port for API server
            max_workers: Maximum number of worker threads
            enable_api: Whether to start the HTTP API server
            log_level: Logging level
        """
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.enable_api = enable_api
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.storage = StorageEngine()
        self.task_queue = TaskQueue()
        self.worker_pool = WorkerPool(max_workers=max_workers, task_queue=self.task_queue)
        self.api_server = None
        
        # Service state
        self._running = False
        self._lock = threading.Lock()
        
        self.logger.info(f"DecentralService initialized with {max_workers} workers")
    
    def start(self) -> None:
        """Start the service and all its components"""
        with self._lock:
            if self._running:
                self.logger.warning("Service is already running")
                return
            
            try:
                # Start worker pool
                self.worker_pool.start()
                self.logger.info("Worker pool started")
                
                # Start API server if enabled
                if self.enable_api:
                    self.api_server = APIServer(
                        host=self.host, 
                        port=self.port, 
                        service=self
                    )
                    self.api_server.start()
                    self.logger.info(f"API server started on {self.host}:{self.port}")
                
                self._running = True
                self.logger.info("DecentralService started successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to start service: {e}")
                self.stop()
                raise
    
    def stop(self) -> None:
        """Stop the service and all its components"""
        with self._lock:
            if not self._running:
                return
            
            try:
                # Stop API server
                if self.api_server:
                    self.api_server.stop()
                    self.api_server = None
                    self.logger.info("API server stopped")
                
                # Stop worker pool
                self.worker_pool.stop()
                self.logger.info("Worker pool stopped")
                
                self._running = False
                self.logger.info("DecentralService stopped")
                
            except Exception as e:
                self.logger.error(f"Error stopping service: {e}")
    
    def is_running(self) -> bool:
        """Check if the service is running"""
        return self._running
    
    # Storage operations (Redis-like API)
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair with optional TTL"""
        return self.storage.set(key, value, ttl)
    
    def get(self, key: str) -> Any:
        """Get value by key"""
        return self.storage.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        return self.storage.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.storage.exists(key)
    
    def keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern"""
        return self.storage.keys(pattern)
    
    def flush(self) -> bool:
        """Clear all data"""
        return self.storage.flush()
    
    def ttl(self, key: str) -> int:
        """Get TTL for a key"""
        return self.storage.ttl(key)
    
    # Queue operations
    def enqueue(self, task: Dict[str, Any]) -> str:
        """Add a task to the queue"""
        return self.task_queue.enqueue(task)
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get next task from queue"""
        return self.task_queue.dequeue()
    
    def queue_size(self) -> int:
        """Get current queue size"""
        return self.task_queue.size()
    
    def queue_empty(self) -> bool:
        """Check if queue is empty"""
        return self.task_queue.empty()
    
    # Task management
    def submit_task(self, 
                   task_type: str, 
                   data: Any, 
                   callback: Optional[Callable] = None,
                   priority: int = 0,
                   task_id: Optional[str] = None,
                   overwrite: bool = True) -> str:
        """
        Submit a task for processing
        
        Args:
            task_type: Type of task to process
            data: Task data
            callback: Optional callback function
            priority: Task priority (higher = more priority)
            task_id: Optional custom task ID. If not provided, auto-generated
            overwrite: If True, overwrite existing task with same ID. If False, block submission
        
        Returns:
            Task ID
        """
        # Generate task ID if not provided
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}_{id(data)}"
        
        task = {
            "id": task_id,
            "type": task_type,
            "data": data,
            "callback": callback,
            "priority": priority,
            "created_at": time.time(),
            "status": "pending",
            "overwrite": overwrite
        }
        
        task_id = self.enqueue(task)
        self.logger.info(f"Task {task_id} submitted for processing")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.task_queue.get_task_status(task_id)
    
    def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific task"""
        return self.task_queue.get_task_detail(task_id)
    
    def search_tasks(self, 
                    status: Optional[str] = None,
                    task_type: Optional[str] = None,
                    limit: int = 100,
                    offset: int = 0) -> Dict[str, Any]:
        """
        Search tasks with filters
        
        Args:
            status: Filter by task status (pending, running, completed, failed, cancelled)
            task_type: Filter by task type
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
        
        Returns:
            Dictionary with tasks and pagination info
        """
        return self.task_queue.search_tasks(status, task_type, limit, offset)
    
    def list_tasks(self, 
                  limit: int = 50, 
                  offset: int = 0,
                  sort_by: str = "created_at",
                  sort_order: str = "desc") -> Dict[str, Any]:
        """
        List tasks with pagination
        
        Args:
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            sort_by: Field to sort by (created_at, priority, status)
            sort_order: Sort order (asc, desc)
        
        Returns:
            Dictionary with tasks and pagination info
        """
        return self.task_queue.list_tasks(limit, offset, sort_by, sort_order)
    
    def is_task_id_available(self, task_id: str) -> bool:
        """Check if a task ID is available for use"""
        return self.task_queue.is_task_id_available(task_id)
    
    def get_task_id_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task ID (whether it exists and its current status)"""
        return self.task_queue.get_task_id_status(task_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "running": self._running,
            "workers": self.worker_pool.get_stats(),
            "queue_size": self.queue_size(),
            "storage_size": self.storage.size(),
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        self._start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
