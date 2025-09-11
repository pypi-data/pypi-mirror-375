"""
Thread-safe storage engine for key-value operations with TTL support
"""

import threading
import time
import re
from typing import Any, Dict, Optional, List, Tuple
from collections import defaultdict


class StorageEngine:
    """
    Thread-safe in-memory storage engine with Redis-like operations
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._running = False
        
        # Start cleanup thread for expired keys
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self) -> None:
        """Start background thread to clean up expired keys"""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_expired_keys(self) -> None:
        """Background thread to remove expired keys"""
        while self._running:
            try:
                current_time = time.time()
                expired_keys = []
                
                with self._lock:
                    for key, expiry_time in self._ttl.items():
                        if current_time >= expiry_time:
                            expired_keys.append(key)
                    
                    # Remove expired keys
                    for key in expired_keys:
                        self._data.pop(key, None)
                        self._ttl.pop(key, None)
                
                if expired_keys:
                    print(f"Cleaned up {len(expired_keys)} expired keys")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
                time.sleep(5)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a key-value pair with optional TTL
        
        Args:
            key: Key to set
            value: Value to store
            ttl: Time to live in seconds (None for no expiration)
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                self._data[key] = value
                if ttl is not None:
                    self._ttl[key] = time.time() + ttl
                else:
                    self._ttl.pop(key, None)  # Remove any existing TTL
                return True
        except Exception as e:
            print(f"Error setting key {key}: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """
        Get value by key
        
        Args:
            key: Key to retrieve
        
        Returns:
            Value if exists and not expired, None otherwise
        """
        with self._lock:
            if key not in self._data:
                return None
            
            # Check if expired
            if key in self._ttl and time.time() >= self._ttl[key]:
                self._data.pop(key, None)
                self._ttl.pop(key, None)
                return None
            
            return self._data[key]
    
    def delete(self, key: str) -> bool:
        """
        Delete a key
        
        Args:
            key: Key to delete
        
        Returns:
            True if key existed and was deleted
        """
        with self._lock:
            existed = key in self._data
            self._data.pop(key, None)
            self._ttl.pop(key, None)
            return existed
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired
        
        Args:
            key: Key to check
        
        Returns:
            True if key exists and is not expired
        """
        with self._lock:
            if key not in self._data:
                return False
            
            # Check if expired
            if key in self._ttl and time.time() >= self._ttl[key]:
                self._data.pop(key, None)
                self._ttl.pop(key, None)
                return False
            
            return True
    
    def keys(self, pattern: str = "*") -> List[str]:
        """
        Get keys matching pattern (supports wildcards)
        
        Args:
            pattern: Pattern to match (* for all, ? for single char)
        
        Returns:
            List of matching keys
        """
        with self._lock:
            if pattern == "*":
                return list(self._data.keys())
            
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            regex = re.compile(f"^{regex_pattern}$")
            
            matching_keys = []
            for key in self._data.keys():
                if regex.match(key):
                    matching_keys.append(key)
            
            return matching_keys
    
    def flush(self) -> bool:
        """
        Clear all data
        
        Returns:
            True if successful
        """
        try:
            with self._lock:
                self._data.clear()
                self._ttl.clear()
                return True
        except Exception as e:
            print(f"Error flushing data: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Get TTL for a key
        
        Args:
            key: Key to check
        
        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        with self._lock:
            if key not in self._data:
                return -2
            
            if key not in self._ttl:
                return -1
            
            remaining = int(self._ttl[key] - time.time())
            if remaining <= 0:
                # Key is expired
                self._data.pop(key, None)
                self._ttl.pop(key, None)
                return -2
            
            return remaining
    
    def size(self) -> int:
        """Get number of keys in storage"""
        with self._lock:
            return len(self._data)
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get all data (for debugging/monitoring)"""
        with self._lock:
            return self._data.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            return {
                "total_keys": len(self._data),
                "keys_with_ttl": len(self._ttl),
                "memory_usage_estimate": sum(len(str(v)) for v in self._data.values())
            }
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self._running = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=1)
