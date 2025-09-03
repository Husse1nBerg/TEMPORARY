import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '{levelname} {asctime} [{name}] {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '{levelname} {asctime} {name}: {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            '()': jsonlogger.JsonFormatter,
            'format': '%(levelname)s %(asctime)s %(name)s %(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'scraper_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/scraper.log',
            'maxBytes': 20971520,  # 20MB
            'backupCount': 10,
            'encoding': 'utf8'
        },
        'json_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/app.json',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        'server.app': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'error_file', 'json_file'],
            'propagate': False
        },
        'server.app.scrapers': {
            'level': 'DEBUG',
            'handlers': ['console', 'scraper_file', 'error_file'],
            'propagate': False
        },
        'server.app.api': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'json_file'],
            'propagate': False
        },
        'server.app.services': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'json_file'],
            'propagate': False
        },
        'server.app.tasks': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'json_file'],
            'propagate': False
        },
        'uvicorn': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'uvicorn.error': {
            'level': 'ERROR',
            'handlers': ['console', 'error_file'],
            'propagate': False
        },
        'uvicorn.access': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False
        },
        'sqlalchemy.engine': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': False
        },
        'celery': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'playwright': {
            'level': 'WARNING',
            'handlers': ['scraper_file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}


class LoggerSetup:
    """Logger configuration and setup utility."""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config = config_dict or LOGGING_CONFIG
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure logs directory exists."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different log types
        (log_dir / 'archive').mkdir(exist_ok=True)
    
    def setup_logging(self, log_level: str = 'INFO', enable_json: bool = False):
        """Setup logging configuration."""
        # Adjust log levels based on environment
        if log_level.upper() == 'DEBUG':
            self.config['handlers']['console']['level'] = 'DEBUG'
            self.config['loggers']['server.app']['level'] = 'DEBUG'
        
        # Enable/disable JSON logging
        if not enable_json:
            # Remove JSON handler from loggers
            for logger_config in self.config['loggers'].values():
                if isinstance(logger_config.get('handlers'), list):
                    if 'json_file' in logger_config['handlers']:
                        logger_config['handlers'].remove('json_file')
        
        # Apply configuration
        logging.config.dictConfig(self.config)
        
        # Set up exception logging
        sys.excepthook = self._log_exception
    
    def _log_exception(self, exc_type, exc_value, exc_traceback):
        """Log uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow keyboard interrupt to work normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = logging.getLogger('server.app')
        logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)
    
    def configure_scraper_logger(self, scraper_name: str) -> logging.Logger:
        """Configure a logger specifically for a scraper."""
        logger_name = f"server.app.scrapers.{scraper_name}"
        return logging.getLogger(logger_name)
    
    def configure_api_logger(self, module_name: str) -> logging.Logger:
        """Configure a logger specifically for API modules."""
        logger_name = f"server.app.api.{module_name}"
        return logging.getLogger(logger_name)
    
    def configure_service_logger(self, service_name: str) -> logging.Logger:
        """Configure a logger specifically for service modules."""
        logger_name = f"server.app.services.{service_name}"
        return logging.getLogger(logger_name)


class StructuredLogger:
    """Structured logging utility for consistent log formatting."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration_ms: float, user_id: Optional[int] = None):
        """Log HTTP request information."""
        self.logger.info(
            f"HTTP {method} {path} - {status_code} ({duration_ms:.2f}ms)",
            extra={
                'event_type': 'http_request',
                'method': method,
                'path': path,
                'status_code': status_code,
                'duration_ms': duration_ms,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_scraper_start(self, scraper_name: str, store_name: str, 
                         category_count: int):
        """Log scraper start event."""
        self.logger.info(
            f"Starting scraper for {store_name} - {category_count} categories",
            extra={
                'event_type': 'scraper_start',
                'scraper_name': scraper_name,
                'store_name': store_name,
                'category_count': category_count,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_scraper_result(self, scraper_name: str, store_name: str,
                          products_found: int, pages_scraped: int,
                          duration_seconds: float, errors: list):
        """Log scraper completion result."""
        self.logger.info(
            f"Scraper completed for {store_name} - "
            f"{products_found} products, {pages_scraped} pages "
            f"({duration_seconds:.1f}s)",
            extra={
                'event_type': 'scraper_result',
                'scraper_name': scraper_name,
                'store_name': store_name,
                'products_found': products_found,
                'pages_scraped': pages_scraped,
                'duration_seconds': duration_seconds,
                'error_count': len(errors),
                'errors': errors[:5],  # Log first 5 errors only
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_data_processing(self, operation: str, items_processed: int,
                           duplicates_removed: int, duration_seconds: float):
        """Log data processing operation."""
        self.logger.info(
            f"Data processing '{operation}' - {items_processed} items, "
            f"{duplicates_removed} duplicates removed ({duration_seconds:.1f}s)",
            extra={
                'event_type': 'data_processing',
                'operation': operation,
                'items_processed': items_processed,
                'duplicates_removed': duplicates_removed,
                'duration_seconds': duration_seconds,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_price_change(self, product_name: str, store_name: str,
                        old_price: float, new_price: float, change_percent: float):
        """Log significant price change."""
        direction = 'increased' if new_price > old_price else 'decreased'
        self.logger.info(
            f"Price {direction} for '{product_name}' at {store_name}: "
            f"${old_price:.2f} -> ${new_price:.2f} ({change_percent:+.1f}%)",
            extra={
                'event_type': 'price_change',
                'product_name': product_name,
                'store_name': store_name,
                'old_price': old_price,
                'new_price': new_price,
                'change_percent': change_percent,
                'direction': direction,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_error(self, error_type: str, message: str, context: Dict[str, Any] = None):
        """Log structured error information."""
        self.logger.error(
            f"{error_type}: {message}",
            extra={
                'event_type': 'error',
                'error_type': error_type,
                'context': context or {},
                'timestamp': datetime.utcnow().isoformat()
            }
        )


class PerformanceLogger:
    """Performance monitoring and logging utility."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.timers = {}
    
    def start_timer(self, operation_id: str):
        """Start timing an operation."""
        self.timers[operation_id] = datetime.utcnow()
    
    def end_timer(self, operation_id: str, operation_name: str, 
                  context: Dict[str, Any] = None):
        """End timing and log performance."""
        if operation_id not in self.timers:
            self.logger.warning(f"Timer '{operation_id}' not found")
            return
        
        start_time = self.timers.pop(operation_id)
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        self.logger.info(
            f"Performance: {operation_name} completed in {duration:.3f}s",
            extra={
                'event_type': 'performance',
                'operation_name': operation_name,
                'duration_seconds': duration,
                'context': context or {},
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return duration
    
    def log_memory_usage(self, operation_name: str, memory_mb: float):
        """Log memory usage information."""
        self.logger.info(
            f"Memory usage for {operation_name}: {memory_mb:.1f} MB",
            extra={
                'event_type': 'memory_usage',
                'operation_name': operation_name,
                'memory_mb': memory_mb,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


# Global logger setup instance
_logger_setup = LoggerSetup()


def setup_logging(log_level: str = 'INFO', enable_json: bool = False):
    """Setup application logging."""
    _logger_setup.setup_logging(log_level, enable_json)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    return _logger_setup.get_logger(name)


def get_scraper_logger(scraper_name: str) -> logging.Logger:
    """Get a scraper-specific logger."""
    return _logger_setup.configure_scraper_logger(scraper_name)


def get_api_logger(module_name: str) -> logging.Logger:
    """Get an API-specific logger."""
    return _logger_setup.configure_api_logger(module_name)


def get_service_logger(service_name: str) -> logging.Logger:
    """Get a service-specific logger."""
    return _logger_setup.configure_service_logger(service_name)


def get_structured_logger(logger: logging.Logger) -> StructuredLogger:
    """Get a structured logger wrapper."""
    return StructuredLogger(logger)


def get_performance_logger(logger: logging.Logger) -> PerformanceLogger:
    """Get a performance logger wrapper."""
    return PerformanceLogger(logger)


# Context manager for performance logging
class log_performance:
    """Context manager for automatic performance logging."""
    
    def __init__(self, logger: logging.Logger, operation_name: str, 
                 context: Dict[str, Any] = None):
        self.perf_logger = PerformanceLogger(logger)
        self.operation_name = operation_name
        self.context = context
        self.operation_id = f"{operation_name}_{id(self)}"
    
    def __enter__(self):
        self.perf_logger.start_timer(self.operation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.perf_logger.end_timer(self.operation_id, self.operation_name, self.context)


# Decorator for automatic function performance logging
def log_execution_time(logger: logging.Logger):
    """Decorator to log function execution time."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation_name = f"{func.__module__}.{func.__name__}"
            with log_performance(logger, operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator