"""
Compilation engine for coordinating the build process across languages.
This module provides the core compilation orchestration, handling the workflow
from source code to executable binaries with optimization and error recovery.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pyrex.exceptions import PyrexCompileError, PyrexRuntimeError
from pyrex.utils.helpers import ensure_directory, clean_temp_files

logger = logging.getLogger(__name__)


class CompilationEngine:
    """
    Orchestrates the compilation process for multiple languages.
    This engine handles the complete workflow from source generation
    to binary compilation with optimization and error recovery.
    """
    def __init__(
        self, language: str, compiler_path: str, flags: List[str]
    ) -> None:
        """
        Initialize the compilation engine.
        Args:
            language: Target programming language
            compiler_path: Path to the compiler executable
            flags: Compilation flags and options
        """
        self.language = language
        self.compiler_path = compiler_path
        self.flags = flags
        self._temp_directories: List[Path] = []

    def create_build_environment(self) -> Path:
        """Create a temporary build environment."""
        temp_dir = Path(
            tempfile.mkdtemp(prefix=f"pyrex_{self.language}_build_")
        )
        self._temp_directories.append(temp_dir)
        (temp_dir / "src").mkdir(exist_ok=True)
        (temp_dir / "build").mkdir(exist_ok=True)
        (temp_dir / "output").mkdir(exist_ok=True)
        logger.debug(f"Created build environment: {temp_dir}")
        return temp_dir

    def write_source_file(
        self, build_dir: Path, code: str, filename: str
    ) -> Path:
        """Write source code to a file in the build directory."""
        source_path = build_dir / "src" / filename
        source_path.write_text(code, encoding="utf-8")
        logger.debug(f"Written source file: {source_path}")
        return source_path

    def compile_to_binary(
        self,
        source_file: Path,
        output_file: Path,
        additional_flags: Optional[List[str]] = None,
    ) -> None:
        """
        Compile source code to binary executable.
        Args:
            source_file: Path to the source code file
            output_file: Path for the output binary
            additional_flags: Extra compilation flags for this specific build
        Raises:
            PyrexCompileError: If compilation fails
        """
        all_flags = self.flags.copy()
        if additional_flags:
            all_flags.extend(additional_flags)
        cmd = (
            [self.compiler_path] + all_flags +
            [str(source_file), "-o", str(output_file)]
        )
        logger.info(f"Compiling {self.language}: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=source_file.parent,
                env=self._get_compilation_env(),
            )
            if result.returncode != 0:
                self._handle_compilation_error(result, cmd, source_file)
            if not output_file.exists():
                raise PyrexCompileError(
                    f"Compilation reported success but output file not found: {output_file}",
                    compiler_output=result.stderr,
                    context={
                        "command": cmd,
                        "stdout": result.stdout
                    },
                )
            if os.name != "nt":
                output_file.chmod(0o755)
            logger.info(
                f"Successfully compiled {self.language} code to {output_file}"
            )
        except subprocess.TimeoutExpired:
            raise PyrexCompileError(
                f"Compilation timeout for {self.language} code (>120s)",
                context={
                    "command": cmd,
                    "source_file": str(source_file)
                },
            )
        except Exception as e:
            raise PyrexCompileError(
                f"Unexpected error during {self.language} compilation: {e}",
                context={
                    "command": cmd,
                    "source_file": str(source_file),
                    "error": str(e),
                },
            )

    def _get_compilation_env(self) -> Dict[str, str]:
        """Get environment variables for compilation."""
        env = os.environ.copy()
        if self.language == "rust":
            env["RUST_BACKTRACE"] = "1"
        elif self.language in ("c", "cpp"):
            env["LC_ALL"] = "C"
        return env

    def _handle_compilation_error(
        self,
        result: subprocess.CompletedProcess,
        cmd: List[str],
        source_file: Path,
    ) -> None:
        """Handle and format compilation errors."""
        error_output = result.stderr.strip()
        error_lines = error_output.split("\n")
        primary_error = None
        for line in error_lines:
            if any(
                keyword in line.lower()
                for keyword in ["error:", "fatal:", "failed"]
            ):
                primary_error = line.strip()
                break
        if not primary_error and error_lines:
            primary_error = error_lines[0].strip()
        raise PyrexCompileError(
            f"Compilation failed for {self.language}: {primary_error or 'Unknown error'}",
            compiler_output=error_output,
            context={
                "command": cmd,
                "stdout": result.stdout,
                "source_file": str(source_file),
                "exit_code": result.returncode,
            },
        )

    def execute_binary(
        self,
        binary_path: Path,
        timeout: float = 30.0,
        input_data: Optional[str] = None,
    ) -> Tuple[str, str, int]:
        """
        Execute a compiled binary.
        Args:
            binary_path: Path to the executable binary
            timeout: Maximum execution time in seconds
            input_data: Optional stdin input for the process
        Returns:
            Tuple of (stdout, stderr, exit_code)
        Raises:
            PyrexRuntimeError: If execution fails
        """
        logger.debug(f"Executing binary: {binary_path} (timeout: {timeout}s)")
        try:
            result = subprocess.run(
                [str(binary_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                input=input_data,
                cwd=binary_path.parent,
            )
            logger.debug(
                f"Execution completed with exit code: {result.returncode}"
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            raise PyrexRuntimeError(
                f"Execution timeout for {self.language} binary ({timeout}s)",
                context={
                    "binary_path": str(binary_path),
                    "timeout": timeout
                },
            )
        except Exception as e:
            raise PyrexRuntimeError(
                f"Unexpected error during execution: {e}",
                context={
                    "binary_path": str(binary_path),
                    "error": str(e)
                },
            )

    def cleanup_build_environment(self, build_dir: Path) -> None:
        """Clean up temporary build files and directories."""
        try:
            if build_dir.exists():
                shutil.rmtree(build_dir, ignore_errors=True)
                logger.debug(f"Cleaned up build directory: {build_dir}")
            if build_dir in self._temp_directories:
                self._temp_directories.remove(build_dir)
        except Exception as e:
            logger.warning(
                f"Failed to cleanup build directory {build_dir}: {e}"
            )

    def cleanup_all(self) -> None:
        """Clean up all temporary build environments."""
        for temp_dir in self._temp_directories.copy():
            self.cleanup_build_environment(temp_dir)
        self._temp_directories.clear()

    def __del__(self):
        """Cleanup on garbage collection."""
        try:
            self.cleanup_all()
        except Exception:
            pass
