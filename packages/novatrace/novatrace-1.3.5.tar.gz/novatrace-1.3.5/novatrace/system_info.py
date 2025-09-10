"""
System information and monitoring utilities for NovaTrace.
Provides real system metrics (CPU, memory, disk usage) for monitoring dashboard.
"""

import psutil
import time
from typing import Dict, Any
import platform
import os

class SystemMonitor:
    """System monitoring utility class"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU usage information"""
        try:
            # Get per-core CPU percentages
            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                "usage": round(cpu_percent, 1),
                "cores": cpu_count,
                "frequency": {
                    "current": round(cpu_freq.current, 2) if cpu_freq else None,
                    "min": round(cpu_freq.min, 2) if cpu_freq else None,
                    "max": round(cpu_freq.max, 2) if cpu_freq else None
                }
            }
        except Exception as e:
            return {
                "usage": 0.0,
                "cores": 0,
                "frequency": {"current": None, "min": None, "max": None},
                "error": str(e)
            }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total": round(memory.total / (1024**3), 2),  # GB
                "available": round(memory.available / (1024**3), 2),  # GB
                "used": round(memory.used / (1024**3), 2),  # GB
                "percent": round(memory.percent, 1),
                "swap": {
                    "total": round(swap.total / (1024**3), 2),
                    "used": round(swap.used / (1024**3), 2),
                    "percent": round(swap.percent, 1)
                }
            }
        except Exception as e:
            return {
                "total": 0.0,
                "available": 0.0,
                "used": 0.0,
                "percent": 0.0,
                "swap": {"total": 0.0, "used": 0.0, "percent": 0.0},
                "error": str(e)
            }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            # Get disk usage for the current directory (where NovaTrace is running)
            current_disk = psutil.disk_usage('/')
            
            # Get all disk partitions
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": round(partition_usage.total / (1024**3), 2),
                        "used": round(partition_usage.used / (1024**3), 2),
                        "free": round(partition_usage.free / (1024**3), 2),
                        "percent": round((partition_usage.used / partition_usage.total) * 100, 1)
                    })
                except PermissionError:
                    continue
            
            return {
                "total": round(current_disk.total / (1024**3), 2),  # GB
                "used": round(current_disk.used / (1024**3), 2),  # GB
                "free": round(current_disk.free / (1024**3), 2),  # GB
                "percent": round((current_disk.used / current_disk.total) * 100, 1),
                "partitions": partitions
            }
        except Exception as e:
            return {
                "total": 0.0,
                "used": 0.0,
                "free": 0.0,
                "percent": 0.0,
                "partitions": [],
                "error": str(e)
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            network_io = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            return {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "connections": network_connections
            }
        except Exception as e:
            return {
                "bytes_sent": 0,
                "bytes_recv": 0,
                "packets_sent": 0,
                "packets_recv": 0,
                "connections": 0,
                "error": str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        try:
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            return {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "boot_time": boot_time,
                "uptime_seconds": round(uptime, 0),
                "novatrace_uptime": round(time.time() - self.start_time, 0)
            }
        except Exception as e:
            return {
                "platform": "Unknown",
                "platform_release": "Unknown",
                "platform_version": "Unknown",
                "architecture": "Unknown",
                "hostname": "Unknown",
                "python_version": platform.python_version(),
                "boot_time": 0,
                "uptime_seconds": 0,
                "novatrace_uptime": round(time.time() - self.start_time, 0),
                "error": str(e)
            }
    
    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the current NovaTrace process"""
        try:
            current_process = psutil.Process()
            
            return {
                "pid": current_process.pid,
                "memory_info": {
                    "rss": round(current_process.memory_info().rss / (1024**2), 2),  # MB
                    "vms": round(current_process.memory_info().vms / (1024**2), 2),  # MB
                    "percent": round(current_process.memory_percent(), 2)
                },
                "cpu_percent": round(current_process.cpu_percent(), 2),
                "num_threads": current_process.num_threads(),
                "create_time": current_process.create_time(),
                "status": current_process.status()
            }
        except Exception as e:
            return {
                "pid": os.getpid(),
                "memory_info": {"rss": 0.0, "vms": 0.0, "percent": 0.0},
                "cpu_percent": 0.0,
                "num_threads": 0,
                "create_time": 0,
                "status": "unknown",
                "error": str(e)
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all system metrics in one call"""
        return {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "system": self.get_system_info(),
            "process": self.get_process_info(),
            "timestamp": time.time()
        }

# Global system monitor instance
system_monitor = SystemMonitor()

def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    return system_monitor.get_all_metrics()

def get_simple_metrics() -> Dict[str, Any]:
    """Get simplified metrics for dashboard display"""
    metrics = system_monitor.get_all_metrics()
    
    return {
        "cpu_usage": metrics["cpu"]["usage"],
        "memory_usage": metrics["memory"]["percent"],
        "disk_usage": metrics["disk"]["percent"],
        "uptime": metrics["system"]["uptime_seconds"],
        "process_memory": metrics["process"]["memory_info"]["rss"],
        "timestamp": metrics["timestamp"]
    }
