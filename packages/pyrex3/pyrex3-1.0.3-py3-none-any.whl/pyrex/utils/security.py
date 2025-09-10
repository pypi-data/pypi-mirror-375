"""
Comprehensive security validation and sandboxing system.
This module provides multi-layered security including code analysis,
execution sandboxing, and resource limit enforcement.
"""

import logging
import re
import os
import resource
from typing import Dict, List, Optional, Pattern
from dataclasses import dataclass
from pyrex.exceptions import PyrexSecurityError

logger = logging.getLogger(__name__)


@dataclass
class SecurityRule:
    """Represents a security validation rule."""

    name: str
    pattern: Pattern[str]
    severity: str  # "error", "warning", "info"
    description: str
    language: Optional[str] = None


class SecurityManager:
    """
    Comprehensive security manager for code validation and sandboxing.
    Features:
    - Multi-language code pattern analysis
    - Resource limit enforcement
    - Sandboxed execution environment
    - Configurable security policies
    """
    def __init__(self, strict_mode: bool = True) -> None:
        """
        Initialize security manager.
        Args:
            strict_mode: Whether to enforce strict security policies
        """
        self.strict_mode = strict_mode
        self.max_code_length = 100_000  # 100KB
        self.max_execution_time = 300  # 5m
        self.max_memory_mb = 512  # 512MB
        self._security_rules: List[SecurityRule] = []
        self._setup_security_rules()
        self._setup_allowed_patterns()
        logger.debug(
            f"Security manager initialized (strict_mode: {strict_mode})"
        )

    def _setup_security_rules(self) -> None:
        """Setup comprehensive security validation rules."""
        self._add_rule(
            "file_operations",
            r"\b(?:fopen|open|file|ifstream|ofstream|File::open)\s*\(",
            "error",
            "File system operations are restricted for security",
        )
        self._add_rule(
            "network_operations",
            r"\b(?:socket|connect|bind|listen|TcpStream::connect|UdpSocket::bind)\s*\(",
            "error",
            "Network operations are not allowed",
        )
        self._add_rule(
            "process_execution",
            r"\b(?:system|exec\w*|popen|Command::new|std::process::)\s*\(",
            "error",
            "Process execution is prohibited",
        )
        self._add_rule(
            "unsafe_memory",
            r"\b(?:gets|strcpy|strcat|sprintf|vsprintf)\s*\(",
            "error",
            "Unsafe memory operations detected",
            "c",
        )
        self._add_rule(
            "unsafe_memory",
            r"\b(?:gets|strcpy|strcat|sprintf|vsprintf)\s*\(",
            "error",
            "Unsafe memory operations detected",
            "cpp",
        )
        self._add_rule(
            "unsafe_rust",
            r"\bunsafe\s*\{",
            "error" if self.strict_mode else "warning",
            "Unsafe Rust blocks are restricted",
            "rust",
        )
        self._add_rule(
            "dangerous_includes",
            r'#include\s*[<"](?:windows\.h|sys/|unistd\.h)[>"]',
            "error",
            "System headers are restricted",
        )
        self._add_rule(
            "dynamic_execution",
            r"\b(?:eval|exec|compile|__import__)\s*\(",
            "error",
            "Dynamic code execution is not allowed",
        )
        self._add_rule(
            "infinite_loops",
            r"\bwhile\s*\(\s*(?:true|1|True)\s*\)",
            "warning",
            "Infinite loop detected - ensure proper exit condition",
        )
        self._add_rule(
            "large_allocations",
            r"\b(?:malloc|calloc|new)\s*\([^)]*[0-9]{6,}",
            "warning",
            "Large memory allocation detected",
        )

    def _add_rule(
        self,
        name: str,
        pattern: str,
        severity: str,
        description: str,
        language: Optional[str] = None,
    ) -> None:
        """Add a security rule."""
        compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        rule = SecurityRule(
            name, compiled_pattern, severity, description, language
        )
        self._security_rules.append(rule)

    def _setup_allowed_patterns(self) -> None:
        """Setup whitelist of allowed patterns."""
        self.allowed_includes = {
            "c":
                {
                    "stdio.h",
                    "stdlib.h",
                    "string.h",
                    "math.h",
                    "time.h",
                    "stdbool.h",
                    "stdint.h",
                    "limits.h",
                    "float.h",
                    "ctype.h",
                    "assert.h",
                    "errno.h",
                },
            "cpp":
                {
                    "iostream",
                    "string",
                    "vector",
                    "map",
                    "set",
                    "algorithm",
                    "cmath",
                    "ctime",
                    "memory",
                    "utility",
                    "iterator",
                    "numeric",
                    "queue",
                    "stack",
                    "deque",
                    "list",
                    "array",
                    "tuple",
                    "functional",
                    "random",
                    "chrono",
                    "thread",
                    "mutex",
                },
            "rust":
                {
                    "std::collections",
                    "std::iter",
                    "std::fmt",
                    "std::mem",
                    "std::ptr",
                    "std::slice",
                    "std::str",
                    "std::vec",
                    "std::option",
                    "std::result",
                    "std::cmp",
                    "std::ops",
                },
        }
        self.safe_functions = {
            "c":
                {
                    "printf",
                    "fprintf",
                    "sprintf",
                    "snprintf",
                    "scanf",
                    "sscanf",
                    "malloc",
                    "calloc",
                    "realloc",
                    "free",
                    "strlen",
                    "strncpy",
                    "strncmp",
                    "strncat",
                    "memcpy",
                    "memset",
                    "memcmp",
                },
            "cpp":
                {
                    "cout",
                    "cin",
                    "cerr",
                    "endl",
                    "string",
                    "vector",
                    "map",
                    "set",
                    "sort",
                    "find",
                    "transform",
                    "for_each",
                    "count",
                },
            "rust":
                {
                    "println!",
                    "print!",
                    "vec!",
                    "format!",
                    "panic!",
                    "assert!",
                    "debug_assert!",
                    "unimplemented!",
                    "todo!",
                },
        }

    def validate_code(self, code: str, language: str) -> None:
        """
        Comprehensive code validation.
        Args:
            code: Source code to validate
            language: Programming language
        Raises:
            PyrexSecurityError: If validation fails
        """
        self._validate_code_length(code)
        self._validate_code_structure(code, language)
        violations = self._check_security_patterns(code, language)
        errors = [v for v in violations if v["severity"] == "error"]
        warnings = [v for v in violations if v["severity"] == "warning"]
        if errors:
            error_msg = f"Security violations detected in {language} code:\n"
            for error in errors[:3]:
                error_msg += f"  - {error['description']} (line {error['line']})\n"
            if len(errors) > 3:
                error_msg += f"  ... and {len(errors) - 3} more errors\n"
            raise PyrexSecurityError(
                error_msg.strip(),
                violation_type="code_analysis",
                context={
                    "language": language,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "violations": errors[:5],
                },
            )
        if warnings and self.strict_mode:
            logger.warning(
                f"Security warnings in {language} code: {len(warnings)} issues"
            )
            for warning in warnings[:3]:
                logger.warning(
                    f"  - {warning['description']} (line {warning['line']})"
                )
        if language == "c":
            self._validate_c_specific(code)
        elif language == "cpp":
            self._validate_cpp_specific(code)
        elif language == "rust":
            self._validate_rust_specific(code)

    def _validate_code_length(self, code: str) -> None:
        """Validate code length limits."""
        if len(code) > self.max_code_length:
            raise PyrexSecurityError(
                f"Code too long: {len(code)} characters (max: {self.max_code_length})",
                violation_type="code_length",
                context={
                    "length": len(code),
                    "max_length": self.max_code_length
                },
            )

    def _validate_code_structure(self, code: str, language: str) -> None:
        """Validate basic code structure and syntax."""
        if not code.strip():
            raise PyrexSecurityError(
                "Empty code is not allowed", violation_type="empty_code"
            )
        try:
            code.encode("ascii")
        except UnicodeEncodeError:
            suspicious_chars = ["\u200b", "\u200c", "\u200d", "\ufeff"]
            for char in suspicious_chars:
                if char in code:
                    raise PyrexSecurityError(
                        "Suspicious hidden characters detected in code",
                        violation_type="suspicious_encoding",
                    )

    def _check_security_patterns(self, code: str, language: str) -> List[Dict]:
        """Check code against security patterns."""
        violations = []
        for rule in self._security_rules:
            if rule.language and rule.language != language:
                continue
            matches = rule.pattern.finditer(code)
            for match in matches:
                line_number = code[:match.start()].count("\n") + 1
                violations.append(
                    {
                        "rule": rule.name,
                        "severity": rule.severity,
                        "description": rule.description,
                        "line": line_number,
                        "match": match.group(),
                        "position": match.start(),
                    }
                )
        return violations

    def _validate_c_specific(self, code: str) -> None:
        """C-specific security validation."""
        dangerous_functions = [
            "gets",
            "strcpy",
            "strcat",
            "sprintf",
            "vsprintf",
            "scanf",
            "fscanf",
            "sscanf",
        ]
        for func in dangerous_functions:
            if re.search(rf"\b{func}\s*\(", code):
                raise PyrexSecurityError(
                    f"Dangerous C function '{func}' is not allowed",
                    violation_type="dangerous_function",
                    context={
                        "function": func,
                        "language": "c"
                    },
                )
        self._validate_includes(code, "c")

    def _validate_cpp_specific(self, code: str) -> None:
        """C++-specific security validation."""
        if re.search(r"reinterpret_cast\s*<", code):
            if self.strict_mode:
                raise PyrexSecurityError(
                    "reinterpret_cast is not allowed in strict mode",
                    violation_type="dangerous_cast",
                )
        self._validate_includes(code, "cpp")

    def _validate_rust_specific(self, code: str) -> None:
        """Rust-specific security validation."""
        unsafe_matches = re.finditer(r"\bunsafe\s*\{", code)
        unsafe_count = sum(1 for _ in unsafe_matches)
        if unsafe_count > 0 and self.strict_mode:
            raise PyrexSecurityError(
                f"Unsafe Rust blocks are not allowed in strict mode ({unsafe_count} found)",
                violation_type="unsafe_code",
                context={"unsafe_blocks": unsafe_count},
            )
        self._validate_includes(code, "rust")

    def _validate_includes(self, code: str, language: str) -> None:
        """Validate include/import statements."""
        allowed = self.allowed_includes.get(language, set())
        if language in ("c", "cpp"):
            pattern = re.compile(r'#include\s*[<"]([^>"]+)[>"]')
        elif language == "rust":
            pattern = re.compile(r"use\s+([^;]+);")
        else:
            return
        for match in pattern.finditer(code):
            include = match.group(1).strip()
            is_allowed = any(
                include == allowed_inc or
                include.startswith(allowed_inc + "::")
                for allowed_inc in allowed
            )
            if not is_allowed:
                if self.strict_mode:
                    raise PyrexSecurityError(
                        f"Include/use statement not allowed: {include}",
                        violation_type="forbidden_include",
                        context={
                            "include": include,
                            "language": language,
                            "line": code[:match.start()].count("\n") + 1,
                        },
                    )
                else:
                    logger.warning(f"Potentially unsafe include: {include}")

    def validate_variable_name(self, name: str) -> None:
        """Validate that a variable name is safe."""
        if not name.isidentifier():
            raise PyrexSecurityError(
                f"Invalid variable name: '{name}'",
                violation_type="invalid_variable_name",
            )
        dangerous_names = {
            "system",
            "exec",
            "eval",
            "open",
            "file",
            "input",
            "raw_input",
            "__import__",
            "compile",
            "globals",
            "locals",
            "main",
            "argv",
            "environ",
            "exit",
            "quit",
        }
        if name.lower() in dangerous_names:
            raise PyrexSecurityError(
                f"Variable name '{name}' is reserved and not allowed",
                violation_type="reserved_variable_name",
            )
        if name.startswith("_"):
            raise PyrexSecurityError(
                f"Variable names cannot start with underscore: '{name}'",
                violation_type="invalid_variable_name",
            )

    def create_secure_environment(self) -> Dict[str, str]:
        """Create a secure environment for code execution."""
        secure_env = {
            "PATH": "/usr/bin:/bin",
            "HOME": "/tmp",
            "SHELL": "/bin/sh",
            "LANG": "C",
            "LC_ALL": "C",
        }
        if "CARGO_HOME" in os.environ:
            secure_env["CARGO_HOME"] = os.environ["CARGO_HOME"]
        if "RUSTUP_HOME" in os.environ:
            secure_env["RUSTUP_HOME"] = os.environ["RUSTUP_HOME"]
        return secure_env

    def set_resource_limits(self) -> None:
        """Set resource limits for the current process."""
        try:
            memory_limit = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.max_execution_time, self.max_execution_time)
            )
            max_file_size = 10 * 1024 * 1024  # 10MB
            resource.setrlimit(
                resource.RLIMIT_FSIZE, (max_file_size, max_file_size)
            )
            logger.debug("Resource limits applied")
        except (AttributeError, OSError) as e:
            logger.warning(f"Could not set resource limits: {e}")
