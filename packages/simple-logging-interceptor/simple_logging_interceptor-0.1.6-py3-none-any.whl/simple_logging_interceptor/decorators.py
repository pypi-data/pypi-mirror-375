# simple_logging_interceptor/decorators.py
import functools
import logging
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("simple_logging_interceptor")
logger.setLevel(logging.INFO)

_configured = False
_current_dir = Path("./.logs")

def _timestamped_log_file(log_dir: Path) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return log_dir / f"interceptor_{ts}.log"

def _ensure_handlers(log_dir: Path | None = None):
    """Configure handlers once, and only when needed."""
    global _configured, _current_dir
    if _configured:
        return
    if log_dir is not None:
        _current_dir = Path(log_dir)

    _current_dir.mkdir(parents=True, exist_ok=True)
    log_file = _timestamped_log_file(_current_dir)

    fmt = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    # Avoid duplicate handlers if user re-imports in an interactive session
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        logger.addHandler(fh)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(ch)

    _configured = True
    logger.info(f"Logging initialized at: {log_file}")

def set_log_directory(log_dir: str):
    """Change log directory; reconfigure handlers to a new timestamped file."""
    global _configured, _current_dir
    _current_dir = Path(log_dir)

    # Remove existing file handlers only; keep console handler
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass

    _configured = False
    _ensure_handlers(_current_dir)
    logger.info(f"Logging directory changed to: {_current_dir}")

def simple_logging_interceptor(func):
    """Decorator to log function calls, arguments, return values, and errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _ensure_handlers()  # <-- lazy init here
        logger.info(f"Calling: {func.__name__} with args={args}, kwargs={kwargs}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start) * 1000
            logger.info(f"Returned from {func.__name__} -> {result} (took {elapsed:.4f} ms)")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise
    return wrapper
