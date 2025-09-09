#!/usr/bin/env python3
"""
Resource Manager - Manages cleanup and resource monitoring
Optimized for CPU-only inference with minimal resource usage
"""

import os
import psutil
import time
import signal
import logging
import threading
import subprocess
import gc
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from functools import wraps

# Custom Exceptions
class ResourceError(Exception):
    """Base exception for resource management errors"""
    pass

class MonitoringError(ResourceError):
    """Exception for monitoring errors"""
    pass

class ProcessManagementError(ResourceError):
    """Exception for process management errors"""
    pass

# Configuration
@dataclass
class ResourceConfig:
    monitoring_interval: float = 5.0
    cpu_warning_threshold: float = 80.0
    memory_warning_threshold: float = 85.0
    disk_warning_threshold: float = 90.0
    process_termination_timeout: int = 5
    enable_monitoring: bool = True
    enable_cleanup: bool = True

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class ResourceMonitor:
    def __init__(self, config: Optional[ResourceConfig] = None):
        self.config = config or ResourceConfig()
        self.logger = self._setup_logger()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used_mb": 0.0,
            "disk_usage_percent": 0.0,
            "process_count": 0,
            "timestamp": time.time()
        }
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('ResourceMonitor')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback function to be called when metrics are updated"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, metrics: Dict[str, Any]):
        """Notify all registered callbacks with current metrics"""
        for callback in self.callbacks:
            try:
                callback(metrics)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    @retry_on_failure(max_retries=3, delay=0.5)
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Process count
            process_count = len(psutil.pids())
            
            self.metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_used_mb": memory_used_mb,
                "disk_usage_percent": disk_usage_percent,
                "process_count": process_count,
                "timestamp": time.time()
            }
            
            # Notify callbacks
            self._notify_callbacks(self.metrics)
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            raise MonitoringError(f"Failed to get metrics: {e}") from e
    
    def start_monitoring(self, interval: Optional[float] = None):
        """Start continuous resource monitoring"""
        if self.monitoring:
            self.logger.warning("Monitoring already active")
            return
        
        if not self.config.enable_monitoring:
            self.logger.info("Monitoring disabled in configuration")
            return
            
        self.monitoring = True
        interval = interval or self.config.monitoring_interval
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Resource monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.get_current_metrics()
                
                # Log warnings for high resource usage
                if metrics["cpu_percent"] > self.config.cpu_warning_threshold:
                    self.logger.warning(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
                
                if metrics["memory_percent"] > self.config.memory_warning_threshold:
                    self.logger.warning(f"High memory usage: {metrics['memory_percent']:.1f}%")
                
                if metrics["disk_usage_percent"] > self.config.disk_warning_threshold:
                    self.logger.warning(f"High disk usage: {metrics['disk_usage_percent']:.1f}%")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)

class ProcessManager:
    def __init__(self, config: Optional[ResourceConfig] = None):
        self.config = config or ResourceConfig()
        self.logger = self._setup_logger()
        self.managed_processes: List[subprocess.Popen] = []
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('ProcessManager')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def add_process(self, process: subprocess.Popen):
        """Add a process to be managed"""
        if process not in self.managed_processes:
            self.managed_processes.append(process)
            self.logger.info(f"Added process {process.pid} to management")
    
    def remove_process(self, process: subprocess.Popen):
        """Remove a process from management"""
        if process in self.managed_processes:
            self.managed_processes.remove(process)
            self.logger.info(f"Removed process {process.pid} from management")
    
    def get_managed_processes(self) -> List[Dict[str, Any]]:
        """Get information about managed processes"""
        processes_info = []
        for process in self.managed_processes:
            try:
                info = {
                    "pid": process.pid,
                    "running": process.poll() is None,
                    "returncode": process.returncode
                }
                processes_info.append(info)
            except Exception as e:
                self.logger.error(f"Error getting process info: {e}")
        
        return processes_info
    
    @retry_on_failure(max_retries=2, delay=1.0)
    def kill_all_processes(self):
        """Kill all managed processes"""
        if not self.managed_processes:
            self.logger.info("No processes to terminate")
            return
        
        for process in self.managed_processes:
            try:
                if process.poll() is None:  # Process is still running
                    self.logger.info(f"Terminating process {process.pid}")
                    process.terminate()
                    
                    # Wait for graceful termination
                    try:
                        process.wait(timeout=self.config.process_termination_timeout)
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"Force killing process {process.pid}")
                        process.kill()
                        process.wait()
                        
            except Exception as e:
                self.logger.error(f"Error terminating process {process.pid}: {e}")
        
        self.managed_processes.clear()
        self.logger.info("All managed processes terminated")
    
    def cleanup_zombie_processes(self):
        """Clean up zombie processes"""
        try:
            # Remove completed processes from the list
            self.managed_processes = [
                p for p in self.managed_processes 
                if p.poll() is None
            ]
            
            # Kill any remaining zombie processes
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        self.logger.info(f"Cleaning up zombie process {proc.info['pid']}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up zombie processes: {e}")

class MemoryManager:
    def __init__(self, config: Optional[ResourceConfig] = None):
        self.config = config or ResourceConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('MemoryManager')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def force_garbage_collection(self):
        """Force Python garbage collection"""
        try:
            collected = gc.collect()
            self.logger.info(f"Garbage collection freed {collected} objects")
            return collected
        except Exception as e:
            self.logger.error(f"Garbage collection failed: {e}")
            raise ResourceError(f"Garbage collection failed: {e}") from e
    
    def clear_python_cache(self):
        """Clear Python import cache"""
        try:
            # Clear sys.modules cache (be careful with this)
            import sys
            modules_to_remove = []
            for module_name in sys.modules:
                if module_name.startswith(('llama_cpp', 'torch', 'transformers')):
                    modules_to_remove.append(module_name)
            
            for module_name in modules_to_remove:
                del sys.modules[module_name]
            
            self.logger.info(f"Cleared {len(modules_to_remove)} modules from cache")
            return len(modules_to_remove)
            
        except Exception as e:
            self.logger.error(f"Failed to clear Python cache: {e}")
            raise ResourceError(f"Failed to clear Python cache: {e}") from e
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / (1024 * 1024),  # Resident Set Size
                "vms_mb": memory_info.vms / (1024 * 1024),  # Virtual Memory Size
                "percent": process.memory_percent()
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}
    
    def get_system_memory_info(self) -> Dict[str, Any]:
        """Get system-wide memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "used_mb": memory.used / (1024 * 1024),
                "percent": memory.percent,
                "swap_total_mb": swap.total / (1024 * 1024),
                "swap_used_mb": swap.used / (1024 * 1024),
                "swap_percent": swap.percent
            }
        except Exception as e:
            self.logger.error(f"Failed to get system memory info: {e}")
            return {}

class ResourceManager:
    """Main resource management class"""
    
    def __init__(self, config: Optional[ResourceConfig] = None):
        self.config = config or ResourceConfig()
        self.monitor = ResourceMonitor(self.config)
        self.process_manager = ProcessManager(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logger with proper handler management"""
        logger = logging.getLogger('ResourceManager')
        if not logger.handlers:  # Only add handler if none exist
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def start_monitoring(self, interval: Optional[float] = None):
        """Start resource monitoring"""
        self.monitor.start_monitoring(interval)
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitor.stop_monitoring()
    
    def add_monitoring_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback for monitoring events"""
        self.monitor.add_callback(callback)
    
    def cleanup_all(self):
        """Perform complete cleanup"""
        if not self.config.enable_cleanup:
            self.logger.info("Cleanup disabled in configuration")
            return
            
        self.logger.info("Starting complete cleanup...")
        
        try:
            # Stop monitoring
            self.stop_monitoring()
            
            # Kill all managed processes
            self.process_manager.kill_all_processes()
            
            # Clean up zombie processes
            self.process_manager.cleanup_zombie_processes()
            
            # Force garbage collection
            self.memory_manager.force_garbage_collection()
            
            # Clear Python cache
            self.memory_manager.clear_python_cache()
            
            # Final garbage collection
            self.memory_manager.force_garbage_collection()
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
            raise ResourceError(f"Cleanup failed: {e}") from e
    
    def get_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        try:
            metrics = self.monitor.get_current_metrics()
            memory_usage = self.memory_manager.get_memory_usage()
            system_memory = self.memory_manager.get_system_memory_info()
            managed_processes = self.process_manager.get_managed_processes()
            
            return {
                "system_metrics": metrics,
                "process_memory": memory_usage,
                "system_memory": system_memory,
                "managed_processes": managed_processes,
                "managed_process_count": len(managed_processes),
                "monitoring_active": self.monitor.monitoring,
                "config": {
                    "monitoring_interval": self.config.monitoring_interval,
                    "cpu_warning_threshold": self.config.cpu_warning_threshold,
                    "memory_warning_threshold": self.config.memory_warning_threshold,
                    "enable_monitoring": self.config.enable_monitoring,
                    "enable_cleanup": self.config.enable_cleanup
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {"error": str(e)}
    
    def add_process(self, process: subprocess.Popen):
        """Add a process to be managed"""
        self.process_manager.add_process(process)
    
    def remove_process(self, process: subprocess.Popen):
        """Remove a process from management"""
        self.process_manager.remove_process(process)
    
    def get_resource_info(self) -> Dict[str, Any]:
        """Get comprehensive resource information"""
        return {
            "status": self.get_status(),
            "config": {
                "monitoring_interval": self.config.monitoring_interval,
                "cpu_warning_threshold": self.config.cpu_warning_threshold,
                "memory_warning_threshold": self.config.memory_warning_threshold,
                "disk_warning_threshold": self.config.disk_warning_threshold,
                "process_termination_timeout": self.config.process_termination_timeout,
                "enable_monitoring": self.config.enable_monitoring,
                "enable_cleanup": self.config.enable_cleanup
            }
        }

if __name__ == "__main__":
    # Example usage
    config = ResourceConfig(monitoring_interval=2.0, enable_monitoring=True)
    manager = ResourceManager(config)
    
    # Add a monitoring callback
    def resource_callback(metrics):
        if metrics["cpu_percent"] > 50:
            print(f"High CPU usage detected: {metrics['cpu_percent']:.1f}%")
    
    manager.add_monitoring_callback(resource_callback)
    
    # Start monitoring
    manager.start_monitoring(interval=2.0)
    
    try:
        # Simulate some work
        time.sleep(10)
        
        # Get status
        status = manager.get_status()
        print("Resource status:")
        print(f"CPU: {status['system_metrics']['cpu_percent']:.1f}%")
        print(f"Memory: {status['system_metrics']['memory_percent']:.1f}%")
        print(f"Process Memory: {status['process_memory']['rss_mb']:.1f} MB")
        
        # Get comprehensive info
        info = manager.get_resource_info()
        print(f"\nResource info: {info}")
        
    finally:
        # Cleanup
        manager.cleanup_all()