"""
Advanced error parsing and formatting for better user experience.
This module provides intelligent error parsing for different compilers
and languages, extracting meaningful information from compiler output.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Pattern, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedError:
    """Represents a parsed error with structured information."""

    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    error_type: Optional[str] = None
    severity: str = "error"
    code_snippet: Optional[str] = None
    suggestions: List[str] = None
    raw_output: str = ""


class ErrorPattern:
    """Represents an error pattern for a specific compiler/language."""
    def __init__(
        self,
        name: str,
        pattern: str,
        message_group: int,
        file_group: Optional[int] = None,
        line_group: Optional[int] = None,
        column_group: Optional[int] = None,
        error_type_group: Optional[int] = None,
    ):
        self.name = name
        self.pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)
        self.message_group = message_group
        self.file_group = file_group
        self.line_group = line_group
        self.column_group = column_group
        self.error_type_group = error_type_group


class ErrorParser:
    """
    Advanced error parser for multiple compilers and languages.
    Provides intelligent parsing of compiler output to extract meaningful
    error information, code snippets, and suggestions for fixes.
    """
    def __init__(self, language: str) -> None:
        """
        Initialize error parser for a specific language.
        Args:
            language: Programming language (rust, c, cpp)
        """
        self.language = language.lower()
        self._setup_error_patterns()
        self._setup_suggestion_patterns()

    def _setup_error_patterns(self) -> None:
        """Setup error parsing patterns for different compilers."""
        self.error_patterns: List[ErrorPattern] = []
        if self.language == "rust":
            self._setup_rust_patterns()
        elif self.language == "c":
            self._setup_c_patterns()
        elif self.language == "cpp":
            self._setup_cpp_patterns()

    def _setup_rust_patterns(self) -> None:
        """Setup Rust-specific error patterns."""
        self.error_patterns.append(
            ErrorPattern(
                name="rustc_error",
                pattern=
                r"error(?:\[E\d+\])?\s*:\s*([^\n]+)\n.*?-->\s+([^:]+):(\d+):(\d+)",
                message_group=1,
                file_group=2,
                line_group=3,
                column_group=4,
            )
        )
        self.error_patterns.append(
            ErrorPattern(
                name="cargo_error",
                pattern=r"error:\s*([^\n]+)\n.*?-->\s+([^:]+):(\d+):(\d+)",
                message_group=1,
                file_group=2,
                line_group=3,
                column_group=4,
            )
        )
        self.error_patterns.append(
            ErrorPattern(
                name="rust_panic",
                pattern=
                r"thread '[^']+' panicked at '([^']+)', ([^:]+):(\d+):(\d+)",
                message_group=1,
                file_group=2,
                line_group=3,
                column_group=4,
            )
        )
        self.error_patterns.append(
            ErrorPattern(
                name="rust_simple",
                pattern=r"error:\s*(.+)",
                message_group=1,
            )
        )

    def _setup_c_patterns(self) -> None:
        """Setup C-specific error patterns."""
        self.error_patterns.append(
            ErrorPattern(
                name="gcc_error",
                pattern=
                r"([^:]+):(\d+):(?:(\d+):)?\s*(?:fatal\s+)?(error|warning):\s*(.+)",
                message_group=5,
                file_group=1,
                line_group=2,
                column_group=3,
                error_type_group=4,
            )
        )
        self.error_patterns.append(
            ErrorPattern(
                name="c_simple",
                pattern=r"error:\s*(.+)",
                message_group=1,
            )
        )

    def _setup_cpp_patterns(self) -> None:
        """Setup C++-specific error patterns."""
        self.error_patterns.append(
            ErrorPattern(
                name="gpp_error",
                pattern=
                r"([^:]+):(\d+):(?:(\d+):)?\s*(?:fatal\s+)?(error|warning):\s*(.+)",
                message_group=5,
                file_group=1,
                line_group=2,
                column_group=3,
                error_type_group=4,
            )
        )
        self.error_patterns.append(
            ErrorPattern(
                name="cpp_template_error",
                pattern=
                r"([^:]+):(\d+):(\d+):\s*error:\s*(.+?)\n(?:.*?\n)*?\s*required from",
                message_group=4,
                file_group=1,
                line_group=2,
                column_group=3,
            )
        )
        self.error_patterns.append(
            ErrorPattern(
                name="cpp_simple",
                pattern=r"error:\s*(.+)",
                message_group=1,
            )
        )

    def _setup_suggestion_patterns(self) -> None:
        """Setup patterns for generating helpful suggestions."""
        self.suggestion_patterns = {
            "rust":
                [
                    (
                        re.compile(r"cannot find value `(\w+)`"),
                        lambda m:
                        f"Did you forget to declare variable '{m.group(1)}'?",
                    ),
                    (
                        re.compile(
                            r"mismatched types.*expected `([^`]+)`, found `([^`]+)`"
                        ),
                        lambda m:
                        f"Type mismatch: expected {m.group(1)}, got {m.group(2)}. Try type conversion.",
                    ),
                    (
                        re.compile(r"borrowed value does not live long enough"),
                        lambda m:
                        "Consider using owned values or adjusting lifetimes.",
                    ),
                ],
            "c":
                [
                    (
                        re.compile(r"'(\w+)' undeclared"),
                        lambda m:
                        f"Variable '{m.group(1)}' is not declared. Add declaration before use.",
                    ),
                    (
                        re.compile(r"implicit declaration of function '(\w+)'"),
                        lambda m:
                        f"Function '{m.group(1)}' not declared. Include proper header or add prototype.",
                    ),
                    (
                        re.compile(
                            r"assignment makes pointer from integer without a cast"
                        ),
                        lambda m:
                        "Type mismatch: trying to assign integer to pointer. Check types.",
                    ),
                ],
            "cpp":
                [
                    (
                        re.compile(r"'(\w+)' was not declared in this scope"),
                        lambda m:
                        f"'{m.group(1)}' not found. Check spelling or add proper #include.",
                    ),
                    (
                        re.compile(r"no matching function for call to '(\w+)'"),
                        lambda m:
                        f"No matching overload for '{m.group(1)}'. Check function parameters.",
                    ),
                    (
                        re.compile(r"no operator.*matches these operands"),
                        lambda m:
                        "No matching operator. Check types or include necessary headers.",
                    ),
                ],
        }

    def parse_compile_error(self, error_output: str,
                            source_file: str) -> Dict[str, Any]:
        """
        Parse compiler error output into structured information.
        Args:
            error_output: Raw compiler error output
            source_file: Path to the source file
        Returns:
            Dictionary with parsed error information
        """
        if not error_output.strip():
            return {
                "raw_output": error_output,
                "message": "Unknown compilation error"
            }
        for pattern in self.error_patterns:
            match = pattern.pattern.search(error_output)
            if match:
                parsed = self._extract_error_info(match, pattern, error_output)
                if parsed.line_number and Path(source_file).exists():
                    parsed.code_snippet = self._extract_code_snippet(
                        source_file, parsed.line_number
                    )
                parsed.suggestions = self._generate_suggestions(parsed.message)
                return self._parsed_error_to_dict(parsed)
        return {
            "raw_output": error_output,
            "message": self._extract_primary_error_message(error_output),
            "suggestions": self._generate_suggestions(error_output),
        }

    def parse_runtime_error(self, error_output: str) -> Dict[str, Any]:
        """
        Parse runtime error output.
        Args:
            error_output: Runtime error output (stderr)
        Returns:
            Dictionary with parsed error information
        """
        if not error_output.strip():
            return {
                "raw_output": error_output,
                "message": "Unknown runtime error"
            }
        if self.language == "rust":
            return self._parse_rust_runtime_error(error_output)
        elif self.language in ("c", "cpp"):
            return self._parse_c_runtime_error(error_output)
        return {
            "raw_output": error_output,
            "message": error_output.strip().split("\n")[0],
            "suggestions": ["Check for segmentation faults or memory issues"],
        }

    def _extract_error_info(
        self, match: re.Match, pattern: ErrorPattern, raw_output: str
    ) -> ParsedError:
        """Extract structured error information from regex match."""
        parsed = ParsedError(
            message=match.group(pattern.message_group),
            raw_output=raw_output,
        )
        if pattern.file_group:
            parsed.file_path = match.group(pattern.file_group)
        if pattern.line_group:
            try:
                parsed.line_number = int(match.group(pattern.line_group))
            except (ValueError, TypeError):
                pass
        if pattern.column_group and match.group(pattern.column_group):
            try:
                parsed.column_number = int(match.group(pattern.column_group))
            except (ValueError, TypeError):
                pass
        if pattern.error_type_group:
            parsed.error_type = match.group(pattern.error_type_group)
            parsed.severity = (
                "warning" if "warning" in parsed.error_type.lower() else "error"
            )
        return parsed

    def _extract_code_snippet(
        self,
        source_file: str,
        line_number: int,
        context_lines: int = 3
    ) -> Optional[str]:
        """Extract code snippet around the error line."""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if line_number <= 0 or line_number > len(lines):
                return None
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            snippet_lines = []
            for i in range(start, end):
                line_prefix = ">>> " if i == line_number - 1 else "    "
                line_num = f"{i + 1:3d}"
                snippet_lines.append(
                    f"{line_prefix}{line_num}: {lines[i].rstrip()}"
                )
            return "\n".join(snippet_lines)
        except (FileNotFoundError, IndexError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to extract code snippet: {e}")
            return None

    def _generate_suggestions(self, error_message: str) -> List[str]:
        """Generate helpful suggestions based on error message."""
        suggestions = []
        if self.language in self.suggestion_patterns:
            for pattern, suggestion_func in self.suggestion_patterns[
                self.language]:
                match = pattern.search(error_message)
                if match:
                    suggestions.append(suggestion_func(match))
        error_lower = error_message.lower()
        if "syntax error" in error_lower:
            suggestions.append(
                "Check for missing semicolons, brackets, or parentheses."
            )
        if "undefined" in error_lower or "undeclared" in error_lower:
            suggestions.append(
                "Make sure all variables and functions are properly declared."
            )
        if "type" in error_lower and "mismatch" in error_lower:
            suggestions.append(
                "Check variable types and consider explicit type conversion."
            )
        return suggestions or ["Review the code around the error location."]

    def _extract_primary_error_message(self, error_output: str) -> str:
        """Extract the primary error message from output."""
        lines = error_output.strip().split("\n")
        for line in lines:
            line = line.strip()
            if any(
                keyword in line.lower()
                for keyword in ["error:", "fatal:", "failed"]
            ):
                return line
        for line in lines:
            if line.strip():
                return line.strip()
        return "Unknown error"

    def _parse_rust_runtime_error(self, error_output: str) -> Dict[str, Any]:
        """Parse Rust-specific runtime errors."""
        panic_pattern = re.compile(r"thread '[^']*' panicked at '([^']+)'")
        match = panic_pattern.search(error_output)
        if match:
            return {
                "raw_output":
                    error_output,
                "message":
                    f"Panic: {match.group(1)}",
                "error_type":
                    "panic",
                "suggestions":
                    [
                        "Check for array bounds violations or unwrap() on None/Err values",
                        "Consider using expect() with descriptive messages for better debugging",
                    ],
            }
        return {
            "raw_output": error_output,
            "message": error_output.strip().split("\n")[0],
            "suggestions": ["Check for runtime panics or assertion failures"],
        }

    def _parse_c_runtime_error(self, error_output: str) -> Dict[str, Any]:
        """Parse C/C++-specific runtime errors."""
        error_lower = error_output.lower()
        if "segmentation fault" in error_lower or "segfault" in error_lower:
            return {
                "raw_output":
                    error_output,
                "message":
                    "Segmentation fault",
                "error_type":
                    "segfault",
                "suggestions":
                    [
                        "Check for null pointer dereferences",
                        "Verify array bounds and buffer overflows",
                        "Ensure proper memory allocation and deallocation",
                    ],
            }
        if "abort" in error_lower or "aborted" in error_lower:
            return {
                "raw_output":
                    error_output,
                "message":
                    "Program aborted",
                "error_type":
                    "abort",
                "suggestions":
                    [
                        "Check for assertion failures",
                        "Look for calls to abort() or exit()",
                        "Verify memory allocation didn't fail",
                    ],
            }
        return {
            "raw_output":
                error_output,
            "message":
                (
                    error_output.strip().split("\n")[0]
                    if error_output.strip() else "Runtime error"
                ),
            "suggestions":
                ["Check for memory access violations or runtime assertions"],
        }

    def _parsed_error_to_dict(self, parsed: ParsedError) -> Dict[str, Any]:
        """Convert ParsedError to dictionary."""
        result = {
            "message": parsed.message,
            "raw_output": parsed.raw_output,
            "severity": parsed.severity,
        }
        if parsed.file_path:
            result["file_path"] = parsed.file_path
        if parsed.line_number:
            result["line_number"] = parsed.line_number
        if parsed.column_number:
            result["column_number"] = parsed.column_number
        if parsed.error_type:
            result["error_type"] = parsed.error_type
        if parsed.code_snippet:
            result["code_snippet"] = parsed.code_snippet
        if parsed.suggestions:
            result["suggestions"] = parsed.suggestions
        return result
