"""
Client library for easy integration with DecentralService
"""

import requests
import json
from typing import Any, Dict, Optional, List


class DecentralServiceClient:
    """
    Client for interacting with DecentralService via HTTP API
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
    
    def _request(self, method: str, endpoint: str, data: Any = None) -> Dict[str, Any]:
        """Make HTTP request to the service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to DecentralService: {e}")
    
    # Storage operations
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value pair"""
        data = {"value": value}
        if ttl is not None:
            data["ttl"] = ttl
        
        result = self._request("PUT", f"/storage/{key}", data)
        return result.get("success", False)
    
    def get(self, key: str) -> Any:
        """Get value by key"""
        try:
            result = self._request("GET", f"/storage/{key}")
            return result.get("value")
        except ConnectionError:
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        result = self._request("DELETE", f"/storage/{key}")
        return result.get("success", False)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            result = self._request("GET", f"/storage/{key}/exists")
            return result.get("exists", False)
        except ConnectionError:
            return False
    
    def keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern"""
        result = self._request("GET", f"/storage/keys?pattern={pattern}")
        return result.get("keys", [])
    
    def ttl(self, key: str) -> int:
        """Get TTL for key"""
        result = self._request("GET", f"/storage/{key}/ttl")
        return result.get("ttl", -2)
    
    def flush(self) -> bool:
        """Clear all data"""
        result = self._request("POST", "/storage/flush")
        return result.get("success", False)
    
    # Task operations
    def submit_task(self, task_type: str, data: Any, priority: int = 0, task_id: Optional[str] = None, overwrite: bool = True) -> str:
        """Submit task for processing"""
        task_data = {
            "type": task_type,
            "data": data,
            "priority": priority,
            "overwrite": overwrite
        }
        
        # Add custom task ID if provided
        if task_id is not None:
            task_data["task_id"] = task_id
        
        result = self._request("POST", "/tasks", task_data)
        return result.get("task_id")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        try:
            return self._request("GET", f"/queue/tasks/{task_id}")
        except ConnectionError:
            return None
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        result = self._request("GET", "/queue/size")
        return result.get("size", 0)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return self._request("GET", "/queue/stats")
    
    # System operations
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return self._request("GET", "/health")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return self._request("GET", "/stats")
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics"""
        return self._request("GET", "/workers/stats")
    
    def get_worker_stats_by_id(self, worker_id: int) -> Optional[Dict[str, Any]]:
        """Get specific worker statistics"""
        try:
            return self._request("GET", f"/workers/{worker_id}/stats")
        except ConnectionError:
            return None
    
    def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific task"""
        try:
            return self._request("GET", f"/tasks/{task_id}")
        except ConnectionError:
            return None
    
    def search_tasks(self, 
                    status: Optional[str] = None,
                    task_type: Optional[str] = None,
                    limit: int = 100,
                    offset: int = 0) -> Dict[str, Any]:
        """Search tasks with filters"""
        params = {}
        if status:
            params['status'] = status
        if task_type:
            params['type'] = task_type
        if limit != 100:
            params['limit'] = limit
        if offset != 0:
            params['offset'] = offset
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/tasks/search?{query_string}" if query_string else "/tasks/search"
        
        return self._request("GET", endpoint)
    
    def list_tasks(self, 
                  limit: int = 50, 
                  offset: int = 0,
                  sort_by: str = "created_at",
                  sort_order: str = "desc") -> Dict[str, Any]:
        """List tasks with pagination and sorting"""
        params = {
            'limit': limit,
            'offset': offset,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        endpoint = f"/tasks?{query_string}"
        
        return self._request("GET", endpoint)
    
    def is_task_id_available(self, task_id: str) -> bool:
        """Check if a task ID is available for use"""
        try:
            status = self._request("GET", f"/tasks/check-id/{task_id}")
            return status.get("available", False)
        except ConnectionError:
            return False
    
    def get_task_id_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task ID (whether it exists and its current status)"""
        try:
            return self._request("GET", f"/tasks/check-id/{task_id}")
        except ConnectionError:
            return None


# Convenience functions for quick usage
def create_client(host: str = "localhost", port: int = 6379) -> DecentralServiceClient:
    """Create a DecentralService client"""
    return DecentralServiceClient(host, port)


def quick_set(host: str, port: int, key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Quickly set a value"""
    client = DecentralServiceClient(host, port)
    return client.set(key, value, ttl)


def quick_get(host: str, port: int, key: str) -> Any:
    """Quickly get a value"""
    client = DecentralServiceClient(host, port)
    return client.get(key)


def quick_task(host: str, port: int, task_type: str, data: Any, priority: int = 0) -> str:
    """Quickly submit a task"""
    client = DecentralServiceClient(host, port)
    return client.submit_task(task_type, data, priority)
