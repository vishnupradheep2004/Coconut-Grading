"""
utils/logging_manager.py
Logging and monitoring for Coconut Grading AI
Tracks application events, errors, and performance metrics
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


class LoggingManager:
    """Centralized logging management"""
    
    def __init__(self, log_dir: Path, app_name: str = "coconut_grading_ai", level: str = "INFO"):
        """
        Initialize logging manager
        
        Args:
            log_dir: Directory for log files
            app_name: Application name for log prefix
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.app_name = app_name
        
        # Create logger
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(getattr(logging, level))
        
        # File handler
        log_file = self.log_dir / f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info level message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning level message"""
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log error level message"""
        if exception:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug level message"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Log critical level message"""
        self.logger.critical(message)
    
    def log_analysis(self, username: str, filename: str, coconut_count: int, grade: str, processing_time: float):
        """Log analysis event"""
        self.logger.info(
            f"Analysis: user={username}, file={filename}, coconuts={coconut_count}, "
            f"grade={grade}, time={processing_time:.2f}s"
        )
    
    def log_batch_processing(self, username: str, batch_name: str, image_count: int, 
                            total_coconuts: int, processing_time: float):
        """Log batch processing event"""
        self.logger.info(
            f"Batch Processing: user={username}, batch={batch_name}, images={image_count}, "
            f"coconuts={total_coconuts}, time={processing_time:.2f}s"
        )
    
    def log_user_action(self, username: str, action: str, details: str = ""):
        """Log user action"""
        msg = f"User Action: user={username}, action={action}"
        if details:
            msg += f", details={details}"
        self.logger.info(msg)


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = {}
    
    def start_timer(self, operation_name: str):
        """Start timing an operation"""
        self.metrics[operation_name] = {
            "start_time": datetime.now(),
            "end_time": None,
            "duration": None
        }
    
    def end_timer(self, operation_name: str) -> float:
        """End timing and return duration in seconds"""
        if operation_name not in self.metrics:
            return 0.0
        
        self.metrics[operation_name]["end_time"] = datetime.now()
        duration = (self.metrics[operation_name]["end_time"] - 
                   self.metrics[operation_name]["start_time"]).total_seconds()
        self.metrics[operation_name]["duration"] = duration
        
        return duration
    
    def get_metric(self, operation_name: str) -> Optional[float]:
        """Get duration of operation"""
        if operation_name in self.metrics:
            return self.metrics[operation_name]["duration"]
        return None
    
    def get_all_metrics(self) -> dict:
        """Get all recorded metrics"""
        return self.metrics
