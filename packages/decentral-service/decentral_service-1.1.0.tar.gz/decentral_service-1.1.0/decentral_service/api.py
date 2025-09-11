"""
HTTP API server for external access to DecentralService
"""

import json
import threading
import time
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging


class APIServer:
    """
    HTTP API server that exposes DecentralService functionality via REST API
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, service=None):
        self.host = host
        self.port = port
        self.service = service
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        
        self.logger = logging.getLogger(__name__)
        self.server_thread = None
        self.running = False
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy" if self.service and self.service.is_running() else "unhealthy",
                "timestamp": time.time()
            })
        
        @self.app.route('/stats', methods=['GET'])
        def get_stats():
            """Get service statistics"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            stats = self.service.get_stats()
            return jsonify(stats)
        
        # Storage operations
        @self.app.route('/storage/<key>', methods=['GET'])
        def get_value(key):
            """Get value by key"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            value = self.service.get(key)
            if value is None:
                return jsonify({"error": "Key not found"}), 404
            
            return jsonify({"key": key, "value": value})
        
        @self.app.route('/storage/<key>', methods=['PUT'])
        def set_value(key):
            """Set key-value pair"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({"error": "JSON data required"}), 400
                
                value = data.get('value')
                ttl = data.get('ttl')
                
                if value is None:
                    return jsonify({"error": "Value is required"}), 400
                
                success = self.service.set(key, value, ttl)
                return jsonify({"success": success, "key": key})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/storage/<key>', methods=['DELETE'])
        def delete_value(key):
            """Delete key"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            success = self.service.delete(key)
            return jsonify({"success": success, "key": key})
        
        @self.app.route('/storage/<key>/exists', methods=['GET'])
        def key_exists(key):
            """Check if key exists"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            exists = self.service.exists(key)
            return jsonify({"key": key, "exists": exists})
        
        @self.app.route('/storage/<key>/ttl', methods=['GET'])
        def get_ttl(key):
            """Get TTL for key"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            ttl = self.service.ttl(key)
            return jsonify({"key": key, "ttl": ttl})
        
        @self.app.route('/storage/keys', methods=['GET'])
        def list_keys():
            """List keys with optional pattern"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            pattern = request.args.get('pattern', '*')
            keys = self.service.keys(pattern)
            return jsonify({"keys": keys, "pattern": pattern})
        
        @self.app.route('/storage/flush', methods=['POST'])
        def flush_storage():
            """Clear all storage"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            success = self.service.flush()
            return jsonify({"success": success})
        
        # Queue operations
        @self.app.route('/queue/tasks', methods=['POST'])
        def enqueue_task():
            """Add task to queue"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({"error": "JSON data required"}), 400
                
                task_id = self.service.enqueue(data)
                return jsonify({"task_id": task_id, "success": True})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/queue/tasks/<task_id>', methods=['GET'])
        def get_task_status(task_id):
            """Get task status"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            status = self.service.get_task_status(task_id)
            if status is None:
                return jsonify({"error": "Task not found"}), 404
            
            return jsonify(status)
        
        @self.app.route('/queue/tasks/<task_id>', methods=['DELETE'])
        def cancel_task(task_id):
            """Cancel task"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            # This would need to be implemented in the core service
            return jsonify({"error": "Not implemented yet"}), 501
        
        @self.app.route('/queue/size', methods=['GET'])
        def get_queue_size():
            """Get queue size"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            size = self.service.queue_size()
            return jsonify({"size": size})
        
        @self.app.route('/queue/stats', methods=['GET'])
        def get_queue_stats():
            """Get queue statistics"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            stats = self.service.task_queue.get_stats()
            return jsonify(stats)
        
        # Task submission
        @self.app.route('/tasks', methods=['POST'])
        def submit_task():
            """Submit a task for processing"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            try:
                data = request.get_json()
                if data is None:
                    return jsonify({"error": "JSON data required"}), 400
                
                task_type = data.get('type', 'default')
                task_data = data.get('data')
                priority = data.get('priority', 0)
                custom_task_id = data.get('task_id')  # Optional custom task ID
                overwrite = data.get('overwrite', True)  # Optional overwrite parameter
                
                if task_data is None:
                    return jsonify({"error": "Task data is required"}), 400
                
                task_id = self.service.submit_task(
                    task_type=task_type,
                    data=task_data,
                    priority=priority,
                    task_id=custom_task_id,
                    overwrite=overwrite
                )
                
                return jsonify({
                    "task_id": task_id,
                    "type": task_type,
                    "priority": priority,
                    "success": True
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Task detail endpoint
        @self.app.route('/tasks/<task_id>', methods=['GET'])
        def get_task_detail(task_id):
            """Get detailed information about a specific task"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            detail = self.service.get_task_detail(task_id)
            if detail is None:
                return jsonify({"error": "Task not found"}), 404
            
            return jsonify(detail)
        
        # Search tasks endpoint
        @self.app.route('/tasks/search', methods=['GET'])
        def search_tasks():
            """Search tasks with filters"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            try:
                status = request.args.get('status')
                task_type = request.args.get('type')
                limit = int(request.args.get('limit', 100))
                offset = int(request.args.get('offset', 0))
                
                result = self.service.search_tasks(
                    status=status,
                    task_type=task_type,
                    limit=limit,
                    offset=offset
                )
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # List tasks endpoint
        @self.app.route('/tasks', methods=['GET'])
        def list_tasks():
            """List tasks with pagination and sorting"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            try:
                limit = int(request.args.get('limit', 50))
                offset = int(request.args.get('offset', 0))
                sort_by = request.args.get('sort_by', 'created_at')
                sort_order = request.args.get('sort_order', 'desc')
                
                result = self.service.list_tasks(
                    limit=limit,
                    offset=offset,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                
                return jsonify(result)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Task ID availability check
        @self.app.route('/tasks/check-id/<task_id>', methods=['GET'])
        def check_task_id_availability(task_id):
            """Check if a task ID is available for use"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            try:
                status = self.service.get_task_id_status(task_id)
                return jsonify(status)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # Worker operations
        @self.app.route('/workers/stats', methods=['GET'])
        def get_worker_stats():
            """Get worker pool statistics"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            stats = self.service.worker_pool.get_stats()
            return jsonify(stats)
        
        @self.app.route('/workers/<int:worker_id>/stats', methods=['GET'])
        def get_worker_stats_by_id(worker_id):
            """Get specific worker statistics"""
            if not self.service:
                return jsonify({"error": "Service not available"}), 500
            
            stats = self.service.worker_pool.get_worker_stats(worker_id)
            if stats is None:
                return jsonify({"error": "Worker not found"}), 404
            
            return jsonify(stats)
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "Endpoint not found"}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({"error": "Internal server error"}), 500
    
    def start(self):
        """Start the API server in a separate thread"""
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self.server_thread.start()
        self.logger.info(f"API server starting on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the API server"""
        if not self.running:
            return
        
        self.running = False
        # Note: Flask doesn't have a clean shutdown method
        # In production, you'd want to use a proper WSGI server
        self.logger.info("API server stopped")
    
    def _run_server(self):
        """Run the Flask server"""
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"API server error: {e}")
            self.running = False
