"""
Exception hierarchy for Pyrex library.
This module defines all custom exceptions used throughout Pyrex
with comprehensive context and debugging information.
"""

from typing import Any, Dict, List, Optional


class PyrexError(Exception):
    """Base exception class for all Pyrex-related errors."""
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize Pyrex error.
        Args:
            message: Error message
            context: Additional context information
            suggestions: Suggested fixes or actions
        """
        super().__init__(message)
        self.context = context or {}
        self.suggestions = suggestions or []
        self.error_type = self.__class__.__name__

    def __str__(self) -> str:
        """Return formatted error message."""
        parts = [super().__str__()]
        if self.suggestions:
            parts.append("\nSuggestions:")
            for suggestion in self.suggestions:
                parts.append(f"  - {suggestion}")
        return "".join(parts)

    def get_full_context(self) -> Dict[str, Any]:
        """Get complete error context for debugging."""
        return {
            "error_type": self.error_type,
            "message": str(self),
            "context": self.context,
            "suggestions": self.suggestions,
        }


class PyrexCompileError(PyrexError):
    """Exception raised when compilation fails."""
    def __init__(
        self,
        message: str,
        compiler_output: str = "",
        line_number: Optional[int] = None,
        column_number: Optional[int] = None,
        code_snippet: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize compilation error.
        Args:
            message: Error message
            compiler_output: Raw compiler output
            line_number: Line number where error occurred
            column_number: Column number where error occurred
            code_snippet: Code snippet around the error
            context: Additional context
            suggestions: Suggested fixes
        """
        super().__init__(message, context, suggestions)
        self.compiler_output = compiler_output
        self.line_number = line_number
        self.column_number = column_number
        self.code_snippet = code_snippet

    def __str__(self) -> str:
        """Return formatted compilation error message."""
        parts = [super().__str__()]
        if self.line_number:
            location = f"line {self.line_number}"
            if self.column_number:
                location += f", column {self.column_number}"
            parts.append(f"\nLocation: {location}")
        if self.code_snippet:
            parts.append(f"\nCode snippet:\n{self.code_snippet}")
        if self.compiler_output and self.compiler_output.strip():
            parts.append(f"\nCompiler output:\n{self.compiler_output.strip()}")
        return "".join(parts)


class PyrexRuntimeError(PyrexError):
    """Exception raised when compiled code execution fails."""
    def __init__(
        self,
        message: str,
        stderr: str = "",
        stdout: str = "",
        exit_code: Optional[int] = None,
        execution_time: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize runtime error.
        Args:
            message: Error message
            stderr: Standard error output
            stdout: Standard output (if relevant)
            exit_code: Process exit code
            execution_time: Time taken before error
            context: Additional context
            suggestions: Suggested fixes
        """
        super().__init__(message, context, suggestions)
        self.stderr = stderr
        self.stdout = stdout
        self.exit_code = exit_code
        self.execution_time = execution_time

    def __str__(self) -> str:
        """Return formatted runtime error message."""
        parts = [super().__str__()]
        if self.exit_code is not None:
            parts.append(f"\nExit code: {self.exit_code}")
        if self.execution_time is not None:
            parts.append(f"\nExecution time: {self.execution_time:.3f}s")
        if self.stderr and self.stderr.strip():
            parts.append(f"\nError output:\n{self.stderr.strip()}")
        if self.stdout and self.stdout.strip():
            parts.append(f"\nStandard output:\n{self.stdout.strip()}")
        return "".join(parts)


class PyrexTypeError(PyrexError):
    """Exception raised when type conversion or validation fails."""
    def __init__(
        self,
        message: str,
        python_type: Optional[type] = None,
        target_language: Optional[str] = None,
        variable_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize type error.
        Args:
            message: Error message
            python_type: Python type that caused the error
            target_language: Target language for conversion
            variable_name: Variable name if applicable
            context: Additional context
            suggestions: Suggested fixes
        """
        super().__init__(message, context, suggestions)
        self.python_type = python_type
        self.target_language = target_language
        self.variable_name = variable_name

    def __str__(self) -> str:
        """Return formatted type error message."""
        parts = [super().__str__()]
        if self.variable_name:
            parts.append(f"\nVariable: {self.variable_name}")
        if self.python_type:
            parts.append(f"\nPython type: {self.python_type.__name__}")
        if self.target_language:
            parts.append(f"\nTarget language: {self.target_language}")
        return "".join(parts)


class PyrexSecurityError(PyrexError):
    """Exception raised when security validation fails."""
    def __init__(
        self,
        message: str,
        violation_type: Optional[str] = None,
        severity: str = "error",
        detected_patterns: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize security error.
        Args:
            message: Error message
            violation_type: Type of security violation
            severity: Severity level (error, warning, info)
            detected_patterns: List of detected dangerous patterns
            context: Additional context
            suggestions: Security recommendations
        """
        super().__init__(message, context, suggestions)
        self.violation_type = violation_type
        self.severity = severity
        self.detected_patterns = detected_patterns or []

    def __str__(self) -> str:
        """Return formatted security error message."""
        parts = [f"🔒 SECURITY {self.severity.upper()}: {super().__str__()}"]
        if self.violation_type:
            parts.append(f"\nViolation type: {self.violation_type}")
        if self.detected_patterns:
            parts.append(f"\nDetected patterns:")
            for pattern in self.detected_patterns[:5]:
                parts.append(f"  - {pattern}")
            if len(self.detected_patterns) > 5:
                parts.append(
                    f"  ... and {len(self.detected_patterns) - 5} more"
                )
        return "".join(parts)


class PyrexConfigurationError(PyrexError):
    """Exception raised when configuration is invalid."""
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        valid_options: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize configuration error.
        Args:
            message: Error message
            config_key: Configuration key that's invalid
            config_value: Invalid configuration value
            valid_options: List of valid options
            context: Additional context
            suggestions: Configuration suggestions
        """
        super().__init__(message, context, suggestions)
        self.config_key = config_key
        self.config_value = config_value
        self.valid_options = valid_options or []

    def __str__(self) -> str:
        """Return formatted configuration error message."""
        parts = [super().__str__()]
        if self.config_key:
            parts.append(f"\nConfiguration key: {self.config_key}")
        if self.config_value is not None:
            parts.append(f"\nProvided value: {self.config_value}")
        if self.valid_options:
            parts.append(
                f"\nValid options: {', '.join(map(str, self.valid_options))}"
            )
        return "".join(parts)


class PyrexCacheError(PyrexError):
    """Exception raised when cache operations fail."""
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        cache_operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize cache error.
        Args:
            message: Error message
            cache_key: Cache key involved in the error
            cache_operation: Operation that failed (get, set, clear, etc.)
            context: Additional context
            suggestions: Cache-related suggestions
        """
        super().__init__(message, context, suggestions)
        self.cache_key = cache_key
        self.cache_operation = cache_operation

    def __str__(self) -> str:
        """Return formatted cache error message."""
        parts = [super().__str__()]
        if self.cache_operation:
            parts.append(f"\nOperation: {self.cache_operation}")
        if self.cache_key:
            parts.append(f"\nCache key: {self.cache_key}")
        return "".join(parts)
