"""
Base classes and core abstractions for Pyrex.
This module defines the fundamental interfaces and base classes that all
language-specific implementations inherit from.
"""

import hashlib
import logging
import os
import subprocess
import tempfile
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pyrex.exceptions import (
    PyrexCompileError,
    PyrexRuntimeError,
    PyrexTypeError,
)
from pyrex.utils.cache import CacheManager
from pyrex.utils.security import SecurityManager
from pyrex.utils.errors import ErrorParser
from pyrex.utils.helpers import validate_timeout

logger = logging.getLogger(__name__)


@dataclass
class CompilerConfig:
    """Configuration for compiler instances."""

    compiler_path: Optional[str] = None
    compile_flags: List[str] = field(default_factory=list)
    cache_dir: Optional[str] = None
    enable_security: bool = True
    max_code_length: int = 100_000
    default_timeout: float = 30.0
    enable_async: bool = False
    debug_mode: bool = False


class BaseCompiler(ABC):
    """
    Abstract base class for all language compilers.
    This class provides the common infrastructure for compiling and executing
    code in different programming languages with safety, caching, and error handling.
    """
    def __init__(self, config: Optional[CompilerConfig] = None) -> None:
        """
        Initialize the compiler with configuration.
        Args:
            config: Compiler configuration options
        """
        self.config = config or CompilerConfig()
        self.compiler_path = self.config.compiler_path or self._get_default_compiler(
        )
        self.compile_flags = self.config.compile_flags or self._get_default_flags(
        )
        self.cache_manager = CacheManager(self.config.cache_dir)
        self.security_manager = (
            SecurityManager() if self.config.enable_security else None
        )
        self.error_parser = ErrorParser(self.get_language())
        self._lock = threading.RLock()
        self._verify_compiler()
        logger.info(f"Initialized {self.get_language()} compiler")

    @abstractmethod
    def get_language(self) -> str:
        """Return the programming language name."""
        pass

    @abstractmethod
    def _get_default_compiler(self) -> str:
        """Return the default compiler executable path."""
        pass

    @abstractmethod
    def _get_default_flags(self) -> List[str]:
        """Return default compilation flags."""
        pass

    @abstractmethod
    def _generate_wrapper_code(
        self, code: str, variables: Dict[str, Any]
    ) -> str:
        """Generate wrapper code that integrates user code with variable handling."""
        pass

    @abstractmethod
    def _get_file_extension(self) -> str:
        """Return the file extension for source files."""
        pass

    def _verify_compiler(self) -> None:
        """Verify that the compiler is available and functional."""
        try:
            result = subprocess.run(
                [self.compiler_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise PyrexRuntimeError(
                    f"Compiler verification failed for {self.get_language()}",
                    stderr=result.stderr,
                    exit_code=result.returncode,
                )
            logger.debug(
                f"Verified {self.get_language()} compiler: {result.stdout.split()[0]}"
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise PyrexRuntimeError(
                f"Compiler not found or not working: {self.compiler_path}",
                context={
                    "error": str(e),
                    "language": self.get_language()
                },
            )

    def _compute_cache_key(self, code: str, variables: Dict[str, Any]) -> str:
        """Compute a unique cache key for the given code and variables."""
        content_parts = [
            code,
            str(sorted(variables.items())),
            str(self.compile_flags),
            self.get_language(),
            self.__class__.__name__,
        ]
        content = "|".join(content_parts)
        return hashlib.sha256(content.encode()).hexdigest()

    def _validate_inputs(
        self, code: str, variables: Dict[str, Any], timeout: float
    ) -> None:
        """Validate all inputs before processing."""
        if not isinstance(code, str):
            raise PyrexTypeError("Code must be a string")
        if len(code.strip()) == 0:
            raise PyrexTypeError("Code cannot be empty")
        if len(code) > self.config.max_code_length:
            raise PyrexTypeError(
                f"Code too long: {len(code)} chars (max: {self.config.max_code_length})",
                context={
                    "length": len(code),
                    "max_length": self.config.max_code_length,
                },
            )
        if not isinstance(variables, dict):
            raise PyrexTypeError("Variables must be a dictionary")
        for name, value in variables.items():
            if not isinstance(name, str) or not name.isidentifier():
                raise PyrexTypeError(f"Invalid variable name: '{name}'")
            if not self._is_supported_type(value):
                raise PyrexTypeError(
                    f"Unsupported variable type: {type(value).__name__}",
                    python_type=type(value),
                    target_language=self.get_language(),
                )
        validate_timeout(timeout)
        if self.security_manager:
            self.security_manager.validate_code(code, self.get_language())
            for name in variables:
                self.security_manager.validate_variable_name(name)

    def _is_supported_type(self, value: Any) -> bool:
        """Check if a Python value type is supported."""
        supported_types = (int, float, str, bool, list, tuple, type(None))
        if isinstance(value, supported_types):
            if isinstance(value, (list, tuple)):
                return all(self._is_supported_type(item) for item in value)
            return True
        return False

    def _compile_code(self, source_file: Path, output_file: Path) -> None:
        """Compile source code to executable binary."""
        cmd = (
            [self.compiler_path] + self.compile_flags +
            [str(source_file), "-o", str(output_file)]
        )
        logger.debug(f"Compiling {self.get_language()} code: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=source_file.parent,
            )
            if result.returncode != 0:
                parsed_error = self.error_parser.parse_compile_error(
                    result.stderr,
                    str(source_file),
                )
                raise PyrexCompileError(
                    f"Compilation failed for {self.get_language()} code",
                    compiler_output=result.stderr,
                    line_number=parsed_error.get("line_number"),
                    code_snippet=parsed_error.get("code_snippet"),
                    context={
                        "command": cmd,
                        "stdout": result.stdout,
                        "parsed": parsed_error,
                    },
                )
            if not output_file.exists():
                raise PyrexCompileError(
                    f"Compilation succeeded but output file not created: {output_file}",
                    compiler_output=result.stderr,
                )
            logger.debug(
                f"Successfully compiled {self.get_language()} code to {output_file}"
            )
        except subprocess.TimeoutExpired:
            raise PyrexCompileError(
                f"Compilation timeout for {self.get_language()} code (>60s)",
                context={"command": cmd},
            )

    def _execute_binary(self, binary_path: Path,
                        timeout: float) -> Tuple[str, str, int]:
        """Execute compiled binary and return results."""
        logger.debug(f"Executing binary: {binary_path} (timeout: {timeout}s)")
        try:
            result = subprocess.run(
                [str(binary_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=binary_path.parent,
            )
            logger.debug(
                f"Execution completed with exit code: {result.returncode}"
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            raise PyrexRuntimeError(
                f"Execution timeout for {self.get_language()} code ({timeout}s)",
                context={
                    "binary_path": str(binary_path),
                    "timeout": timeout
                },
            )

    def execute(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        force_recompile: bool = False,
    ) -> str:
        """
        Execute code with optional variable injection.
        Args:
            code: Source code to compile and execute
            variables: Dictionary of variables to pass to the code
            timeout: Maximum execution time in seconds
            force_recompile: Skip cache and force recompilation
        Returns:
            Standard output from the executed code
        Raises:
            PyrexCompileError: If compilation fails
            PyrexRuntimeError: If execution fails
            PyrexTypeError: If type validation fails
            PyrexSecurityError: If security validation fails
        """
        with self._lock:
            variables = variables or {}
            timeout = timeout or self.config.default_timeout
            self._validate_inputs(code, variables, timeout)
            cache_key = self._compute_cache_key(code, variables)
            if not force_recompile:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {self.get_language()} code")
                    return cached_result
            with tempfile.TemporaryDirectory(
                prefix=f"pyrex_{self.get_language()}_"
            ) as temp_dir:
                temp_path = Path(temp_dir)
                wrapper_code = self._generate_wrapper_code(code, variables)
                source_file = temp_path / f"main{self._get_file_extension()}"
                source_file.write_text(wrapper_code, encoding="utf-8")
                binary_file = temp_path / "main"
                if os.name == "nt":
                    binary_file = binary_file.with_suffix(".exe")
                self._compile_code(source_file, binary_file)
                stdout, stderr, exit_code = self._execute_binary(
                    binary_file, timeout
                )
                if exit_code != 0:
                    parsed_error = self.error_parser.parse_runtime_error(stderr)
                    raise PyrexRuntimeError(
                        f"Runtime error in {self.get_language()} code",
                        stderr=stderr,
                        exit_code=exit_code,
                        context={
                            "parsed": parsed_error,
                            "stdout": stdout,
                        },
                    )
                result = stdout.strip()
                self.cache_manager.set(cache_key, result)
                logger.debug(
                    f"Successfully executed {self.get_language()} code"
                )
                return result
