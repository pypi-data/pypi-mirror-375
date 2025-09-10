"""
NovaTrace System Metrics Collector
Collects and stores historical system metrics data
"""
import asyncio
import logging
import json
import psutil
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

from ..database.model import SystemMetrics, sessionmaker, engine as default_engine
from ..system.system import get_os_info, get_cpu_info, get_memory_info, get_disk_info
from ..connect import hora

logger = logging.getLogger(__name__)

class SystemMetricsCollector:
    """
    Collects system metrics and stores them in the database for historical analysis
    """
    
    def __init__(self, collection_interval_seconds: int = 30):  # Default: 30 seconds for granular data
        self.collection_interval = collection_interval_seconds
        self.is_running = False
        self.session_factory = None
        
    def setup_database(self, engine=None):
        """Setup database session factory"""
        db_engine = engine or default_engine
        self.session_factory = sessionmaker(bind=db_engine)
    
    def collect_current_metrics(self) -> dict:
        """
        Collect current system metrics
        Returns a dictionary with all current system information
        """
        try:
            # Get current process for NovaTrace metrics
            current_process = psutil.Process(os.getpid())
            process_memory = current_process.memory_info().rss / (1024 * 1024)  # MB
            process_cpu = current_process.cpu_percent(interval=1)
            
            # Collect system information (without GPU)
            os_info = get_os_info()
            cpu_info = get_cpu_info()
            memory_info = get_memory_info()
            disk_info = get_disk_info()
            
            # Structure the metrics data
            metrics = {
                'timestamp': datetime.now(hora),
                'cpu_percent': cpu_info.get('Uso de CPU (%)', 0.0),
                'cpu_count_physical': cpu_info.get('Cores físicos', 0),
                'cpu_count_logical': cpu_info.get('Cores lógicos', 0),
                'memory_total_gb': memory_info.get('Total (GB)', 0.0),
                'memory_available_gb': memory_info.get('Disponible (GB)', 0.0),
                'memory_used_gb': memory_info.get('Total (GB)', 0.0) - memory_info.get('Disponible (GB)', 0.0),
                'memory_percent': memory_info.get('Uso (%)', 0.0),
                'disk_total_gb': disk_info.get('Total (GB)', 0.0),
                'disk_used_gb': disk_info.get('Usado (GB)', 0.0),
                'disk_free_gb': disk_info.get('Libre (GB)', 0.0),
                'disk_percent': disk_info.get('Uso (%)', 0.0),
                'gpu_info': None,  # Sin GPU
                'os_info': os_info,
                'process_memory_mb': process_memory,
                'process_cpu_percent': process_cpu
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def store_metrics(self, metrics: dict) -> bool:
        """
        Store metrics data in the database
        Returns True if successful, False otherwise
        """
        if not metrics or not self.session_factory:
            return False
            
        try:
            db = self.session_factory()
            
            # Create new metrics record
            system_metric = SystemMetrics(
                timestamp=metrics['timestamp'],
                cpu_percent=metrics.get('cpu_percent'),
                cpu_count_physical=metrics.get('cpu_count_physical'),
                cpu_count_logical=metrics.get('cpu_count_logical'),
                memory_total_gb=metrics.get('memory_total_gb'),
                memory_available_gb=metrics.get('memory_available_gb'),
                memory_used_gb=metrics.get('memory_used_gb'),
                memory_percent=metrics.get('memory_percent'),
                disk_total_gb=metrics.get('disk_total_gb'),
                disk_used_gb=metrics.get('disk_used_gb'),
                disk_free_gb=metrics.get('disk_free_gb'),
                disk_percent=metrics.get('disk_percent'),
                gpu_info=metrics.get('gpu_info'),
                os_info=metrics.get('os_info'),
                process_memory_mb=metrics.get('process_memory_mb'),
                process_cpu_percent=metrics.get('process_cpu_percent')
            )
            
            db.add(system_metric)
            db.commit()
            db.close()
            
            logger.info(f"System metrics stored successfully at {metrics['timestamp']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing system metrics: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    def cleanup_old_metrics(self, days_to_keep: int = 30):
        """
        Remove old metrics data to prevent database bloat
        Keeps data for the specified number of days
        """
        if not self.session_factory:
            return False
            
        try:
            db = self.session_factory()
            cutoff_date = datetime.now(hora) - timedelta(days=days_to_keep)
            
            # Delete old records
            deleted_count = db.query(SystemMetrics).filter(
                SystemMetrics.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old system metrics records")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    async def start_collection(self):
        """
        Start the metrics collection loop
        """
        if self.is_running:
            logger.warning("Metrics collection is already running")
            return
        
        if not self.session_factory:
            logger.error("Database not setup. Call setup_database() first")
            return
        
        self.is_running = True
        logger.info(f"Starting system metrics collection (interval: {self.collection_interval}s)")
        
        try:
            while self.is_running:
                # Collect and store metrics
                metrics = self.collect_current_metrics()
                if metrics:
                    self.store_metrics(metrics)
                
                # Cleanup old data once per day (when running for first time each day)
                current_hour = datetime.now().hour
                if current_hour == 2:  # Run cleanup at 2 AM
                    self.cleanup_old_metrics()
                
                # Wait for next collection interval
                await asyncio.sleep(self.collection_interval)
                
        except asyncio.CancelledError:
            logger.info("Metrics collection was cancelled")
        except Exception as e:
            logger.error(f"Error in metrics collection loop: {e}")
        finally:
            self.is_running = False
    
    def stop_collection(self):
        """
        Stop the metrics collection
        """
        if self.is_running:
            self.is_running = False
            logger.info("Stopping system metrics collection")
    
    def get_historical_metrics(self, hours_back: int = 24) -> list:
        """
        Retrieve historical metrics for the specified time period
        
        Args:
            hours_back: Number of hours of history to retrieve
            
        Returns:
            List of metrics dictionaries
        """
        if not self.session_factory:
            return []
        
        try:
            db = self.session_factory()
            
            # Calculate time range
            end_time = datetime.now(hora)
            start_time = end_time - timedelta(hours=hours_back)
            
            # Query historical data
            metrics = db.query(SystemMetrics).filter(
                SystemMetrics.timestamp >= start_time,
                SystemMetrics.timestamp <= end_time
            ).order_by(desc(SystemMetrics.timestamp)).all()
            
            db.close()
            
            # Convert to dictionary format
            result = []
            for metric in metrics:
                result.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'cpu_percent': metric.cpu_percent,
                    'cpu_count_physical': metric.cpu_count_physical,
                    'cpu_count_logical': metric.cpu_count_logical,
                    'memory_total_gb': metric.memory_total_gb,
                    'memory_available_gb': metric.memory_available_gb,
                    'memory_used_gb': metric.memory_used_gb,
                    'memory_percent': metric.memory_percent,
                    'disk_total_gb': metric.disk_total_gb,
                    'disk_used_gb': metric.disk_used_gb,
                    'disk_free_gb': metric.disk_free_gb,
                    'disk_percent': metric.disk_percent,
                    'gpu_info': metric.gpu_info,
                    'os_info': metric.os_info,
                    'process_memory_mb': metric.process_memory_mb,
                    'process_cpu_percent': metric.process_cpu_percent
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving historical metrics: {e}")
            if 'db' in locals():
                db.close()
            return []

# Global instance
_metrics_collector = SystemMetricsCollector()

def get_metrics_collector() -> SystemMetricsCollector:
    """Get the global metrics collector instance"""
    return _metrics_collector

def start_metrics_collection(engine=None, interval_seconds: int = 60):
    """
    Start the system metrics collection background task
    
    Args:
        engine: Database engine to use (optional)
        interval_seconds: Collection interval in seconds (default: 30 seconds)
    """
    collector = get_metrics_collector()
    collector.collection_interval = interval_seconds
    collector.setup_database(engine)
    
    # Start the collection in a background task
    loop = asyncio.get_event_loop()
    task = loop.create_task(collector.start_collection())
    return task

def stop_metrics_collection():
    """Stop the system metrics collection"""
    collector = get_metrics_collector()
    collector.stop_collection()

def get_historical_system_metrics(hours_back: int = 24) -> list:
    """
    Get historical system metrics
    
    Args:
        hours_back: Number of hours of history to retrieve
        
    Returns:
        List of historical metrics
    """
    collector = get_metrics_collector()
    return collector.get_historical_metrics(hours_back)
