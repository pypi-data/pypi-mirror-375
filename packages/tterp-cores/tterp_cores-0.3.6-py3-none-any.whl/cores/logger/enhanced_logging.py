"""
Enterprise-grade logging system với structured logging, correlation ID và performance monitoring.

Hệ thống logging mới này cung cấp:
- Structured JSON logging cho easy parsing
- Correlation ID để trace requests
- Multiple handlers với configuration linh hoạt
- Performance monitoring tích hợp
- Health check logging cho infrastructure services
- Async logging support
"""

import asyncio
import json
import logging
import logging.handlers
import os
import sys
import time
import traceback
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any
import gzip

import psutil
from cores.config.settings import core_settings, CoreSettings


class LogLevel(str, Enum):
    """Enum cho các log levels chuẩn"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LogCategory(str, Enum):
    """Enum cho các categories của logs"""

    API = "api"
    SERVICE = "service"
    REPOSITORY = "repository"
    WORKER = "worker"
    HEALTH_CHECK = "health_check"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    SYSTEM = "system"


# Context variables cho correlation tracking
correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
user_id: ContextVar[int | None] = ContextVar("user_id", default=None)
request_path: ContextVar[str | None] = ContextVar("request_path", default=None)
session_id: ContextVar[str | None] = ContextVar("session_id", default=None)


class StructuredFormatter(logging.Formatter):
    """
    Formatter tạo structured JSON logs với đầy đủ metadata.

    Tự động thêm correlation ID, timestamp, performance metrics và context information.
    """

    def __init__(
        self, service_name: str = "royalty-service", include_trace: bool = True
    ):
        super().__init__()
        self.service_name = service_name
        self.include_trace = include_trace

    # ===== Internal helpers for local-only traceback filtering =====
    @staticmethod
    def _get_project_root() -> str:
        """Resolve project root for filtering traceback.

        Priority: ENV LOG_PROJECT_ROOT -> ENV PROJECT_ROOT -> current working directory.
        """
        try:
            root = core_settings.EFFECTIVE_PROJECT_ROOT or os.getcwd()
            return os.path.abspath(root)
        except Exception:
            return os.getcwd()

    @staticmethod
    def _is_local_frame(filename: str, project_root: str) -> bool:
        """Decide whether a frame file belongs to local project code."""
        try:
            fpath = os.path.abspath(filename)
        except Exception:
            fpath = filename or ""
        # Exclude common third-party locations
        third_party_markers = ("site-packages", "dist-packages")
        if any(marker in fpath for marker in third_party_markers):
            return False
        # Keep only files under project root
        return fpath.startswith(project_root)

    @classmethod
    def _format_local_traceback(
        cls,
        tb: Any,
        fallback_keep: int = 5,
        as_list: bool = True,
        max_frames: int | None = None,
    ) -> list[str] | str:
        """Format traceback keeping only local project frames.

        If filtering removes all frames, keep the last few frames as a fallback
        to preserve minimal context.
        """
        project_root = cls._get_project_root()
        try:
            frames = traceback.extract_tb(tb)
            local_frames = [
                f for f in frames if cls._is_local_frame(f.filename, project_root)
            ]
            use_frames = local_frames if local_frames else frames[-fallback_keep:]
            if max_frames and max_frames > 0 and len(use_frames) > max_frames:
                use_frames = use_frames[-max_frames:]
            formatted = traceback.format_list(use_frames)
            return formatted if as_list else "".join(formatted)
        except Exception:
            # Fallback to standard formatting if anything goes wrong
            formatted = traceback.format_tb(tb)
            return formatted if as_list else "".join(formatted)

    @classmethod
    def _format_local_stack(cls, fallback_keep: int = 5, max_frames: int | None = None) -> list[str]:
        """Format current stack keeping only local project frames."""
        project_root = cls._get_project_root()
        try:
            frames = traceback.extract_stack()
            local_frames = [
                f for f in frames if cls._is_local_frame(f.filename, project_root)
            ]
            use_frames = local_frames if local_frames else frames[-fallback_keep:]
            if max_frames and max_frames > 0 and len(use_frames) > max_frames:
                use_frames = use_frames[-max_frames:]
            return traceback.format_list(use_frames)
        except Exception:
            return traceback.format_stack()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record thành structured JSON"""

        # Base log structure
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "category": getattr(record, "category", LogCategory.SYSTEM.value),
            # Context information
            "correlation_id": correlation_id.get(),
            "user_id": user_id.get(),
            "request_path": request_path.get(),
            "session_id": session_id.get(),
            # Code location
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "file": record.pathname,
            # Process information
            "process_id": os.getpid(),
            "thread_id": record.thread,
            "thread_name": record.threadName,
        }

        # Short, minimal output for health check logs
        try:
            category_val = getattr(record, "category", LogCategory.SYSTEM.value)
        except Exception:
            category_val = LogCategory.SYSTEM.value
        if category_val == LogCategory.HEALTH_CHECK.value:
            minimal = {
                "timestamp": log_entry["timestamp"],
                "service": self.service_name,
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "category": category_val,
            }
            # Chỉ thêm trường tối thiểu: target service và status nếu có
            if hasattr(record, "extra_fields") and record.extra_fields:
                svc = record.extra_fields.get("service")
                stt = record.extra_fields.get("status")
                if svc is not None:
                    minimal["target"] = svc
                if stt is not None:
                    minimal["status"] = stt
            return json.dumps(minimal, ensure_ascii=False, default=str)

        # Add extra fields from record
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_entry.update(record.extra_fields)

        # Add performance metrics if available
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        if hasattr(record, "memory_mb"):
            log_entry["memory_mb"] = record.memory_mb

        # Load runtime config flags from Pydantic settings
        local_only = bool(core_settings.LOG_TRACE_LOCAL_ONLY)
        include_stack = bool(core_settings.LOG_INCLUDE_STACK)
        trace_max = int(core_settings.LOG_TRACE_MAX_FRAMES or 0)
        stack_max = int(core_settings.LOG_STACK_MAX_FRAMES or 0)

        # Add exception information
        if record.exc_info and self.include_trace:
            if local_only:
                exc_type = record.exc_info[0].__name__ if record.exc_info[0] else None
                exc_message = (
                    str(record.exc_info[1]) if record.exc_info[1] else None
                )
                exc_tb = record.exc_info[2]
                log_entry["exception"] = {
                    "type": exc_type,
                    "message": exc_message,
                    "traceback": self._format_local_traceback(
                        exc_tb, as_list=True, max_frames=(trace_max or None)
                    ),
                }
            else:
                # Full exception, but optionally cap formatted length by frames
                formatted = traceback.format_exception(*record.exc_info)
                if trace_max and trace_max > 0 and len(formatted) > trace_max:
                    formatted = formatted[-trace_max:]
                log_entry["exception"] = {
                    "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                    "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                    "traceback": formatted,
                }

        # Add stack trace for errors (trừ health_check đã return ở trên)
        if record.levelno >= logging.ERROR and self.include_trace and include_stack:
            if local_only:
                log_entry["stack_trace"] = self._format_local_stack(
                    max_frames=(stack_max or None)
                )
            else:
                stack_list = traceback.format_stack()
                if stack_max and stack_max > 0 and len(stack_list) > stack_max:
                    stack_list = stack_list[-stack_max:]
                log_entry["stack_trace"] = stack_list

        return json.dumps(log_entry, ensure_ascii=False, default=str)


class EnhancedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Enhanced rotating file handler với compression và cleanup tự động.
    """

    def __init__(
        self,
        filename: str,
        maxBytes: int = 50 * 1024 * 1024,
        backupCount: int = 10,
        encoding: str = "utf-8",
        compress: bool = True,
        **kwargs,
    ):
        # Tạo thư mục nếu chưa tồn tại
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            filename,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            **kwargs,
        )
        self.compress = compress

    def doRollover(self):
        """Override để thêm timestamp, nén và dọn dẹp backup"""
        super().doRollover()

        rotated_tmp = self.baseFilename + ".1"
        # Đổi tên file .1 -> .{timestamp}
        if os.path.exists(rotated_tmp):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.baseFilename}.{timestamp}"
            try:
                os.rename(rotated_tmp, backup_name)
            except Exception:
                # Nếu rename thất bại, thử copy rồi xóa
                with open(rotated_tmp, "rb") as src, open(backup_name, "wb") as dst:
                    dst.write(src.read())
                try:
                    os.remove(rotated_tmp)
                except Exception:
                    pass

            # Nén gzip nếu bật
            if self.compress and os.path.exists(backup_name):
                gz_name = backup_name + ".gz"
                try:
                    with open(backup_name, "rb") as f_in, gzip.open(gz_name, "wb") as f_out:
                        f_out.writelines(f_in)
                    os.remove(backup_name)
                except Exception:
                    # Nếu nén lỗi, giữ nguyên file chưa nén
                    pass

        # Dọn dẹp theo backupCount
        try:
            base = Path(self.baseFilename)
            # Mẫu: application.log.20240101_120000 hoặc .gz
            candidates = sorted(
                [
                    p for p in base.parent.glob(base.name + ".*")
                    if p.name != base.name
                ],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            if self.backupCount > 0 and len(candidates) > self.backupCount:
                for old in candidates[self.backupCount:]:
                    try:
                        old.unlink(missing_ok=True)
                    except Exception:
                        pass
        except Exception:
            # Không chặn logging nếu cleanup lỗi
            pass


class LoggingConfig:
    """Configuration class cho logging system"""

    def __init__(self):
        # Luôn đọc cấu hình mới nhất từ ENV để hỗ trợ test thay đổi os.environ
        # Không phá vỡ core_settings global (giữ để các nơi khác vẫn dùng),
        # nhưng LoggingConfig ưu tiên bản mới khởi tạo để phản ánh ENV hiện tại.
        _settings = CoreSettings()

        self.service_name = _settings.SERVICE_NAME
        self.log_level = (_settings.LOG_LEVEL or "INFO").upper()
        self.log_dir = Path(_settings.LOG_DIR)
        self.enable_console = _settings.ENABLE_CONSOLE_LOG
        self.enable_file = _settings.ENABLE_FILE_LOG
        self.enable_json = _settings.ENABLE_JSON_LOG
        self.max_file_size = int(_settings.LOG_MAX_FILE_SIZE)
        self.backup_count = int(_settings.LOG_BACKUP_COUNT)
        self.compress = bool(_settings.LOG_COMPRESS)

        # ELK/External logging (optional, keep defaults if not present)
        self.elk_enabled = os.getenv("ELK_ENABLED", "false").lower() == "true"
        self.elk_host = os.getenv("ELK_HOST", "localhost")
        self.elk_port = int(os.getenv("ELK_PORT", "5000"))


class EnhancedLogger:
    """
    Enhanced Logger với structured logging, correlation tracking và performance monitoring.

    Đây là replacement cho ApiLogger với các tính năng nâng cao:
    - Structured JSON logging
    - Correlation ID tracking
    - Performance monitoring
    - Health check logging
    - Multiple output formats
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Luôn reload cấu hình từ ENV để hỗ trợ test thay đổi os.environ
        # Vẫn giữ singleton instance nhưng reconfigure mỗi lần gọi
        self.config = LoggingConfig()
        self._setup_logging()
        self._initialized = True

    def _setup_logging(self):
        """Thiết lập logging system với multiple handlers"""

        # Tạo thư mục logs
        self.config.log_dir.mkdir(parents=True, exist_ok=True)

        # Root logger
        self.logger = logging.getLogger(self.config.service_name)
        self.logger.setLevel(getattr(logging, self.config.log_level))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Structured formatter
        structured_formatter = StructuredFormatter(
            service_name=self.config.service_name, include_trace=True
        )

        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            if self.config.enable_json:
                console_handler.setFormatter(structured_formatter)
            else:
                # Simple formatter cho console
                simple_formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                console_handler.setFormatter(simple_formatter)

            self.logger.addHandler(console_handler)

        # File handlers
        if self.config.enable_file:
            # Main log file
            main_handler = EnhancedRotatingFileHandler(
                filename=str(self.config.log_dir / "application.log"),
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
                compress=self.config.compress,
            )
            main_handler.setLevel(logging.INFO)
            main_handler.setFormatter(structured_formatter)
            self.logger.addHandler(main_handler)

            # Error log file
            error_handler = EnhancedRotatingFileHandler(
                filename=str(self.config.log_dir / "error.log"),
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
                compress=self.config.compress,
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(structured_formatter)
            self.logger.addHandler(error_handler)

            # Performance log file
            perf_handler = EnhancedRotatingFileHandler(
                filename=str(self.config.log_dir / "performance.log"),
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
                compress=self.config.compress,
            )
            perf_handler.setLevel(logging.INFO)
            perf_handler.setFormatter(structured_formatter)

            # Filter chỉ performance logs
            perf_handler.addFilter(
                lambda record: getattr(record, "category", "")
                == LogCategory.PERFORMANCE.value
            )
            self.logger.addHandler(perf_handler)

    def _create_log_record(
        self,
        level: str,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra_fields: dict[str, Any] | None = None,
        exc_info: bool | None = None,
    ) -> None:
        """Tạo và gửi log record với metadata đầy đủ"""

        # Chuẩn hoá exc_info: logging.makeRecord cần tuple hoặc None
        exc_info_value = None
        if exc_info:
            if isinstance(exc_info, tuple):
                exc_info_value = exc_info
            elif isinstance(exc_info, BaseException):
                exc_info_value = (exc_info.__class__, exc_info, exc_info.__traceback__)
            elif isinstance(exc_info, bool):
                exc_info_value = sys.exc_info()

        # Tạo LogRecord
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=getattr(logging, level),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=exc_info_value,
        )

        # Thêm metadata
        record.category = category.value
        record.extra_fields = extra_fields or {}

        # Thêm memory usage
        try:
            process = psutil.Process()
            record.memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        except:
            record.memory_mb = 0

        # Handle log record
        self.logger.handle(record)

    # Core logging methods
    def debug(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log debug message"""
        self._create_log_record("DEBUG", message, category, extra_fields)

    def info(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log info message"""
        self._create_log_record("INFO", message, category, extra_fields)

    def warning(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log warning message"""
        self._create_log_record("WARNING", message, category, extra_fields)

    def error(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra_fields: dict[str, Any] | None = None,
        exc_info: bool = True,
    ) -> None:
        """Log error message với exception info"""
        self._create_log_record("ERROR", message, category, extra_fields, exc_info)

    def critical(
        self,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        extra_fields: dict[str, Any] | None = None,
        exc_info: bool = True,
    ) -> None:
        """Log critical message"""
        self._create_log_record("CRITICAL", message, category, extra_fields, exc_info)

    # Specialized logging methods
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: int | None = None,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log API request với performance metrics"""

        fields = {
            "http_method": method,
            "http_path": path,
            "http_status": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            **(extra_fields or {}),
        }

        level = (
            "ERROR"
            if status_code >= 500
            else "WARNING"
            if status_code >= 400
            else "INFO"
        )
        message = f"{method} {path} - {status_code} ({duration_ms}ms)"

        record = self.logger.makeRecord(
            name=self.logger.name,
            level=getattr(logging, level),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )

        record.category = LogCategory.API.value
        record.extra_fields = fields
        record.duration_ms = duration_ms

        self.logger.handle(record)

    def log_business_action(
        self,
        action: str,
        entity_type: str,
        entity_id: int | str,
        user_id: int | None = None,
        success: bool = True,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log business action cho audit trail"""

        fields = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "user_id": user_id,
            "success": success,
            **(extra_fields or {}),
        }

        status = "SUCCESS" if success else "FAILED"
        message = f"Business action: {action} on {entity_type}#{entity_id} - {status}"

        level = "INFO" if success else "WARNING"
        self._create_log_record(level, message, LogCategory.BUSINESS, fields)

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log performance metrics"""

        fields = {
            "operation": operation,
            "duration_ms": duration_ms,
            **(extra_fields or {}),
        }

        message = f"Performance: {operation} took {duration_ms}ms"

        record = self.logger.makeRecord(
            name=self.logger.name,
            level=logging.INFO,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None,
        )

        record.category = LogCategory.PERFORMANCE.value
        record.extra_fields = fields
        record.duration_ms = duration_ms

        self.logger.handle(record)

    def log_health_check(
        self,
        service: str,
        status: str,
        response_time_ms: float,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log health check results"""

        fields = {
            "service": service,
            "status": status,
            "response_time_ms": response_time_ms,
            **(extra_fields or {}),
        }

        message = f"Health check: {service} - {status} ({response_time_ms}ms)"
        level = "INFO" if status.upper() == "HEALTHY" else "ERROR"

        self._create_log_record(level, message, LogCategory.HEALTH_CHECK, fields)

    def log_worker_activity(
        self,
        worker_name: str,
        activity: str,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log worker/queue activity"""

        fields = {
            "worker_name": worker_name,
            "activity": activity,
            **(extra_fields or {}),
        }

        message = f"Worker: {worker_name} - {activity}"
        self._create_log_record("INFO", message, LogCategory.WORKER, fields)


# Context managers cho correlation tracking
class LogContext:
    """Context manager để set correlation ID và user context"""

    def __init__(
        self,
        correlation_id_val: str | None = None,
        user_id_val: int | None = None,
        request_path_val: str | None = None,
        session_id_val: str | None = None,
    ):
        self.correlation_id_val = correlation_id_val or str(uuid.uuid4())
        self.user_id_val = user_id_val
        self.request_path_val = request_path_val
        self.session_id_val = session_id_val

        self.correlation_token = None
        self.user_token = None
        self.path_token = None
        self.session_token = None

    def __enter__(self):
        self.correlation_token = correlation_id.set(self.correlation_id_val)
        self.user_token = user_id.set(self.user_id_val)
        self.path_token = request_path.set(self.request_path_val)
        self.session_token = session_id.set(self.session_id_val)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.correlation_token:
            correlation_id.reset(self.correlation_token)
        if self.user_token:
            user_id.reset(self.user_token)
        if self.path_token:
            request_path.reset(self.path_token)
        if self.session_token:
            session_id.reset(self.session_token)


# Decorators cho automatic logging
def log_performance(
    operation_name: str | None = None, category: LogCategory = LogCategory.PERFORMANCE
):
    """Decorator để tự động log performance của functions"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                result = await func(*args, **kwargs)
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.log_performance(op_name, duration_ms)
                return result
            except Exception as e:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.error(
                    f"Operation {op_name} failed after {duration_ms}ms: {str(e)}",
                    category=category,
                    extra_fields={"operation": op_name, "duration_ms": duration_ms},
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                result = func(*args, **kwargs)
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.log_performance(op_name, duration_ms)
                return result
            except Exception as e:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.error(
                    f"Operation {op_name} failed after {duration_ms}ms: {str(e)}",
                    category=category,
                    extra_fields={"operation": op_name, "duration_ms": duration_ms},
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def log_business_action(action: str, entity_type: str):
    """Decorator để tự động log business actions"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                # Try to extract entity_id from result or kwargs
                entity_id = getattr(result, "id", None) or kwargs.get("id", "unknown")
                logger.log_business_action(
                    action, entity_type, entity_id, user_id=user_id.get(), success=True
                )
                return result
            except Exception as e:
                entity_id = kwargs.get("id", "unknown")
                logger.log_business_action(
                    action,
                    entity_type,
                    entity_id,
                    user_id=user_id.get(),
                    success=False,
                    extra_fields={"error": str(e)},
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                entity_id = getattr(result, "id", None) or kwargs.get("id", "unknown")
                logger.log_business_action(
                    action, entity_type, entity_id, user_id=user_id.get(), success=True
                )
                return result
            except Exception as e:
                entity_id = kwargs.get("id", "unknown")
                logger.log_business_action(
                    action,
                    entity_type,
                    entity_id,
                    user_id=user_id.get(),
                    success=False,
                    extra_fields={"error": str(e)},
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Global logger instance
logger = EnhancedLogger()

# Backward compatibility aliases
ApiLogger = logger  # For easy migration

# Export public API
__all__ = [
    "EnhancedLogger",
    "LogLevel",
    "LogCategory",
    "LogContext",
    "log_performance",
    "log_business_action",
    "logger",
    "ApiLogger",
]
