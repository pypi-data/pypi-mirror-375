"""
DecentralService - A Redis-like edge microservice for multi-threaded task processing

This package provides a lightweight, in-memory storage and task processing system
that can be used as an edge service or imported as a library.
"""

from .core import DecentralService
from .storage import StorageEngine
from .queue import TaskQueue
from .worker import WorkerPool
from .api import APIServer
from .client import DecentralServiceClient, create_client, quick_set, quick_get, quick_task

__version__ = "1.0.0"
__author__ = "DecentralService Team"

__all__ = [
    "DecentralService",
    "StorageEngine", 
    "TaskQueue",
    "WorkerPool",
    "APIServer",
    "DecentralServiceClient",
    "create_client",
    "quick_set",
    "quick_get",
    "quick_task"
]
