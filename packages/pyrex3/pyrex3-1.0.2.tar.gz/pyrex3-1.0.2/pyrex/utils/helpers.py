"""
General utility functions and helpers for Pyrex.
This module provides common utility functions used throughout
the Pyrex library for file operations, validation, and more.
"""

import logging
import os
import shutil
import string
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pyrex.exceptions import PyrexError, PyrexTypeError

logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    Args:
        path: Directory path to ensure
    Returns:
        Path object for the directory
    Raises:
        PyrexError: If directory creation fails
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise PyrexError(f"Failed to create directory {path}: {e}")


def clean_temp_files(pattern: str = "pyrex_*", max_age_hours: int = 24) -> int:
    """
    Clean up old temporary files and directories.
    Args:
        pattern: Glob pattern for files to clean
        max_age_hours: Maximum age in hours before cleanup
    Returns:
        Number of items cleaned up
    """
    temp_dir = Path(tempfile.gettempdir())
    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)
    cleaned_count = 0
    try:
        for item in temp_dir.glob(pattern):
            try:
                if item.stat().st_mtime < cutoff_time:
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink(missing_ok=True)
                    cleaned_count += 1
            except (OSError, PermissionError):
                continue
    except Exception as e:
        logger.warning(f"Error during temp file cleanup: {e}")
    if cleaned_count > 0:
        logger.debug(f"Cleaned up {cleaned_count} temporary items")
    return cleaned_count


def validate_timeout(timeout: float) -> None:
    """
    Validate timeout value.
    Args:
        timeout: Timeout value in seconds
    Raises:
        PyrexTypeError: If timeout is invalid
    """
    if not isinstance(timeout, (int, float)):
        raise PyrexTypeError("Timeout must be a number")
    if timeout <= 0:
        raise PyrexTypeError("Timeout must be positive")
    if timeout > 3600:  # 1h
        raise PyrexTypeError("Timeout cannot exceed 3600 seconds (1 hour)")


def generate_temp_name(prefix: str = "pyrex", suffix: str = "") -> str:
    """
    Generate a unique temporary name.
    Args:
        prefix: Name prefix
        suffix: Name suffix
    Returns:
        Unique temporary name
    """
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    timestamp = int(time.time())
    parts = [prefix, str(timestamp), unique_id]
    if suffix:
        parts.append(suffix)
    return "_".join(parts)


def safe_filename(name: str, max_length: int = 100) -> str:
    """
    Convert a string to a safe filename.
    Args:
        name: Input string
        max_length: Maximum filename length
    Returns:
        Safe filename string
    """
    safe_chars = string.ascii_letters + string.digits + "-_."
    safe_name = "".join(c if c in safe_chars else "_" for c in name)
    while "__" in safe_name:
        safe_name = safe_name.replace("__", "_")
    safe_name = safe_name.strip("_.")
    if not safe_name:
        safe_name = "unnamed"
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    return safe_name


def format_size(size_bytes: int) -> str:
    """
    Format byte size in human-readable format.
    Args:
        size_bytes: Size in bytes
    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    Args:
        seconds: Duration in seconds
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str,
                                                        Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key],
                                        dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and diagnostics.
    Returns:
        Dictionary with system information
    """
    import platform
    import sys

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "temp_dir": tempfile.gettempdir(),
        "cwd": os.getcwd(),
    }


def check_disk_space(path: Union[str, Path], required_mb: int = 100) -> bool:
    """
    Check if sufficient disk space is available.
    Args:
        path: Path to check
        required_mb: Required space in megabytes
    Returns:
        True if sufficient space is available
    """
    try:
        stat = shutil.disk_usage(path)
        available_mb = stat.free / (1024 * 1024)
        return available_mb >= required_mb
    except OSError:
        return False


def find_executable(name: str,
                    paths: Optional[List[str]] = None) -> Optional[str]:
    """
    Find an executable in the system PATH or specified paths.
    Args:
        name: Executable name
        paths: Optional list of additional paths to search
    Returns:
        Full path to executable or None if not found
    """
    result = shutil.which(name)
    if result:
        return result
    search_paths = paths if paths else []
    for path in search_paths:
        exe_path = Path(path) / name
        if exe_path.is_file() and os.access(exe_path, os.X_OK):
            return str(exe_path)
        if os.name == "nt":  # type: ignore
            for ext in [".exe", ".bat", ".cmd"]:
                exe_path_ext = exe_path.with_suffix(ext)
                if exe_path_ext.is_file() and os.access(exe_path_ext, os.X_OK):
                    return str(exe_path_ext)
    return None
