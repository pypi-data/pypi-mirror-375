"""
Rust language implementation for Pyrex.

This module provides comprehensive Rust support with both rustc and cargo options,
modern Rust features, and optimized compilation workflows.
"""

import logging
import shutil
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

from pyrex.core.base import BaseCompiler, CompilerConfig
from pyrex.core.types import RustTypeSystem
from pyrex.exceptions import PyrexCompileError, PyrexRuntimeError

logger = logging.getLogger(__name__)

RustCompilerType = Literal["rustc", "cargo", "auto"]


class RustCompiler(BaseCompiler):
    """
    Advanced Rust compiler with both rustc and cargo support.
    
    This compiler supports both direct rustc compilation and cargo-based
    project compilation, allowing users to choose based on their needs.
    """
    def __init__(
        self,
        config: Optional[CompilerConfig] = None,
        compiler_type: RustCompilerType = "auto",
        use_cargo_for_dependencies: bool = False,
    ) -> None:
        """
        Initialize Rust compiler with flexible compilation options.
        
        Args:
            config: Compiler configuration
            compiler_type: "rustc", "cargo", or "auto" (detect best available)
            use_cargo_for_dependencies: Whether to use cargo when dependencies are detected
        """
        self.compiler_type = compiler_type
        self.use_cargo_for_dependencies = use_cargo_for_dependencies

        self._detect_rust_tools()
        self._select_compilation_mode()

        super().__init__(config)
        self.type_system = RustTypeSystem()

    def get_language(self) -> str:
        return "rust"

    def _detect_rust_tools(self) -> None:
        """Detect available Rust compilation tools."""
        self.has_rustc = shutil.which("rustc") is not None
        self.has_cargo = shutil.which("cargo") is not None

        self.rust_capabilities = {
            "rustc_available": self.has_rustc,
            "cargo_available": self.has_cargo,
            "rustc_version": None,
            "cargo_version": None,
        }

        # Get version information
        if self.has_rustc:
            try:
                result = subprocess.run(
                    ["rustc", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    self.rust_capabilities["rustc_version"
                                          ] = result.stdout.strip()
            except:
                pass

        if self.has_cargo:
            try:
                result = subprocess.run(
                    ["cargo", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    self.rust_capabilities["cargo_version"
                                          ] = result.stdout.strip()
            except:
                pass

        logger.debug(f"Rust tools detected: {self.rust_capabilities}")

    def _select_compilation_mode(self) -> None:
        """Select the appropriate compilation mode based on availability and preferences."""
        if self.compiler_type == "rustc":
            if not self.has_rustc:
                raise PyrexRuntimeError(
                    "rustc not available but explicitly requested"
                )
            self.active_compiler = "rustc"
            self.selected_compiler_path = "rustc"

        elif self.compiler_type == "cargo":
            if not self.has_cargo:
                raise PyrexRuntimeError(
                    "cargo not available but explicitly requested"
                )
            self.active_compiler = "cargo"
            self.selected_compiler_path = "cargo"

        else:  # auto
            if self.has_cargo:
                self.active_compiler = "cargo"
                self.selected_compiler_path = "cargo"
                logger.debug("Auto-selected cargo for Rust compilation")
            elif self.has_rustc:
                self.active_compiler = "rustc"
                self.selected_compiler_path = "rustc"
                logger.debug("Auto-selected rustc for Rust compilation")
            else:
                raise PyrexRuntimeError(
                    "No Rust compiler available (neither rustc nor cargo found)"
                )

    def _get_default_compiler(self) -> str:
        """Return the selected compiler path."""
        return self.selected_compiler_path

    def _get_default_flags(self) -> List[str]:
        """Get default compilation flags based on active compiler."""
        if self.active_compiler == "cargo":
            return ["build", "--release", "--quiet", "--message-format=short"]
        else:  # rustc
            return [
                "-O",
                "--edition",
                "2021",
                "--allow",
                "unused_variables",
                "--allow",
                "dead_code",
                "-C",
                "opt-level=2",
            ]

    def _get_rustc_flags(self, fast: bool = False) -> List[str]:
        """Get rustc-specific flags."""
        if fast:
            return [
                "--edition",
                "2021",
                "--allow",
                "unused_variables",
                "--allow",
                "dead_code",
                "-C",
                "opt-level=0",
                "-C",
                "debuginfo=0",
            ]
        else:
            return [
                "-O",
                "--edition",
                "2021",
                "--allow",
                "unused_variables",
                "--allow",
                "dead_code",
                "-C",
                "opt-level=2",
            ]

    def _get_cargo_flags(self, fast: bool = False) -> List[str]:
        """Get cargo-specific flags."""
        if fast:
            return ["build", "--quiet", "--message-format=short"]
        else:
            return ["build", "--release", "--quiet", "--message-format=short"]

    def _get_file_extension(self) -> str:
        return ".rs"

    def execute(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        force_recompile: bool = False,
        fast: bool = False,
    ) -> str:
        """
        Execute Rust code with the selected compiler.
        
        This is the main execute method that handles both rustc and cargo compilation
        based on the compiler selection and code analysis.
        
        Args:
            code: Rust source code to compile and execute
            variables: Dictionary of variables to inject into the code
            timeout: Maximum execution time in seconds
            force_recompile: Skip cache and force recompilation
            fast: Use fast compilation (minimal optimization, faster builds)
            
        Returns:
            Standard output from the executed code
            
        Raises:
            PyrexCompileError: If compilation fails
            PyrexRuntimeError: If execution fails
            PyrexTypeError: If type validation fails
            PyrexSecurityError: If security validation fails
        """
        variables = variables or {}
        timeout = timeout or (10.0 if fast else self.config.default_timeout)

        return self._execute_internal(
            code, variables, timeout, force_recompile, fast
        )

    def _execute_internal(
        self,
        code: str,
        variables: Dict[str, Any],
        timeout: float,
        force_recompile: bool,
        fast: bool,
    ) -> str:
        """Internal execute method with fast mode support."""
        # fast => rustc > cargo
        if fast and self.has_rustc:
            return self._execute_with_rustc(
                code, variables, timeout, force_recompile, fast
            )

        needs_cargo = self._should_use_cargo(code)

        if needs_cargo and self.has_cargo and self.use_cargo_for_dependencies and not fast:
            return self._execute_with_cargo(
                code, variables, timeout, force_recompile, fast
            )
        elif self.active_compiler == "cargo" and self.has_cargo and not fast:
            return self._execute_with_cargo(
                code, variables, timeout, force_recompile, fast
            )
        else:
            return self._execute_with_rustc(
                code, variables, timeout, force_recompile, fast
            )

    def _should_use_cargo(self, code: str) -> bool:
        """Determine if cargo should be used based on code analysis."""
        import re

        external_patterns = [
            r'extern\s+crate',
            r'use\s+(?!std::)\w+::',
            r'#\[\s*derive\s*\(',
            r'#\[\s*cfg\s*\(',
        ]

        for pattern in external_patterns:
            if re.search(pattern, code):
                return True

        return False

    def _execute_with_rustc(
        self,
        code: str,
        variables: Dict[str, Any],
        timeout: float,
        force_recompile: bool,
        fast: bool = False,
    ) -> str:
        """Execute using rustc directly."""
        with self._lock:
            if not fast:
                self._validate_inputs(code, variables, timeout)

            cache_suffix = "_rustc_fast" if fast else "_rustc"
            cache_key = self._compute_cache_key(code, variables) + cache_suffix
            if not force_recompile:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(
                        f"Cache hit for Rust code ({'fast ' if fast else ''}rustc)"
                    )
                    return cached_result

            with tempfile.TemporaryDirectory(
                prefix="pyrex_rust_rustc_"
            ) as temp_dir:
                temp_path = Path(temp_dir)

                wrapper_code = self._generate_wrapper_code(
                    code, variables, fast
                )

                source_file = temp_path / f"main{self._get_file_extension()}"
                source_file.write_text(wrapper_code, encoding="utf-8")

                binary_file = temp_path / "main"
                if os.name == "nt":  
                    binary_file = binary_file.with_suffix(".exe")

               
                self._compile_with_rustc(source_file, binary_file, fast)

                
                stdout, stderr, exit_code = self._execute_binary(
                    binary_file, timeout
                )

                if exit_code != 0:
                    if not fast:  
                        parsed_error = self.error_parser.parse_runtime_error(
                            stderr
                        )
                        raise PyrexRuntimeError(
                            "Runtime error in Rust code",
                            stderr=stderr,
                            exit_code=exit_code,
                            context=parsed_error,
                        )
                    else:
                        raise PyrexRuntimeError(
                            f"Runtime error in Rust code (fast mode)",
                            stderr=stderr,
                            exit_code=exit_code,
                        )

                result = stdout.strip()
                self.cache_manager.set(cache_key, result, "rust")
                return result

    def _execute_with_cargo(
        self,
        code: str,
        variables: Dict[str, Any],
        timeout: float,
        force_recompile: bool,
        fast: bool = False,
    ) -> str:
        """Execute using cargo for enhanced features."""
        with self._lock:

            if not fast:
                self._validate_inputs(code, variables, timeout)


            cache_suffix = "_cargo_fast" if fast else "_cargo"
            cache_key = self._compute_cache_key(code, variables) + cache_suffix
            if not force_recompile:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(
                        f"Cache hit for Rust code ({'fast ' if fast else ''}cargo)"
                    )
                    return cached_result

            
            with tempfile.TemporaryDirectory(
                prefix="pyrex_rust_cargo_"
            ) as temp_dir:
                temp_path = Path(temp_dir)
                wrapper_code = self._generate_wrapper_code(
                    code, variables, fast
                )
                project_dir = self._create_cargo_project(
                    temp_path, wrapper_code, fast
                )

                
                binary_path = self._compile_with_cargo(project_dir, fast)

              
                stdout, stderr, exit_code = self._execute_binary(
                    binary_path, timeout
                )

                if exit_code != 0:
                    if not fast:  
                        parsed_error = self.error_parser.parse_runtime_error(
                            stderr
                        )
                        raise PyrexRuntimeError(
                            "Runtime error in Rust code",
                            stderr=stderr,
                            exit_code=exit_code,
                            context=parsed_error,
                        )
                    else:
                        raise PyrexRuntimeError(
                            f"Runtime error in Rust code (fast mode)",
                            stderr=stderr,
                            exit_code=exit_code,
                        )

                result = stdout.strip()
                self.cache_manager.set(cache_key, result, "rust")
                return result

    def _generate_wrapper_code(
        self, code: str, variables: Dict[str, Any], fast: bool = False
    ) -> str:
        """Generate Rust wrapper with proper type handling for all modes."""

        var_declarations = []
        for name, value in variables.items():
            rust_type = self.type_system.get_native_type(value)
            rust_value = self.type_system.convert_to_native(value)
            var_declarations.append(
                f"    let {name}: {rust_type} = {rust_value};"
            )


        if fast:
            # tempfix
            wrapper = f'''// Fast-mode Rust wrapper by Pyrex
{self._get_basic_imports()}

#[allow(unused_variables, unused_mut, dead_code)]
fn main() {{
{chr(10).join(var_declarations)}

{self._indent_code(code, 4)}
}}
'''
        else:
            wrapper = self._get_rust_template().format(
                variable_declarations="\n".join(var_declarations),
                user_code=self._indent_code(code, 4),
                std_imports=self._get_required_imports(code),
                allow_attributes=self._get_allow_attributes(),
            )

        return wrapper

    def _get_basic_imports(self) -> str:
        """Get basic imports for fast mode."""
        return '''// Basic imports for fast mode
use std::time::Instant;'''

    def _get_rust_template(self) -> str:
        """Get the Rust code template with modern features."""
        return '''// Auto-generated Rust wrapper by Pyrex
{std_imports}

{allow_attributes}
#[allow(unused_imports)]
use std::collections::{{HashMap, BTreeMap, HashSet, BTreeSet}};
#[allow(unused_imports)]
use std::{{mem, ptr, slice, str}};

fn main() {{
{variable_declarations}

    // === User code begins ===
{user_code}
    // === User code ends ===
}}
'''

    def _get_allow_attributes(self) -> str:
        """Get allow attributes for common inline code patterns."""
        return '''#[allow(unused_variables)]
#[allow(unused_mut)]
#[allow(dead_code)]'''

    def _get_required_imports(self, code: str) -> str:
        """Analyze code and add required imports."""
        imports = []

      
        imports.append("use std::time::Instant;")

        
        if "HashMap" in code or "BTreeMap" in code:
            imports.append("use std::collections::{HashMap, BTreeMap};")

        if "File" in code or "read_to_string" in code or "write" in code:
            imports.append("use std::fs;")
            imports.append("use std::io::prelude::*;")

        if "thread::" in code or "spawn" in code:
            imports.append("use std::thread;")

        if "Duration" in code or "sleep" in code:
            imports.append("use std::time::{Duration, Instant};")

        if "Mutex" in code or "Arc" in code:
            imports.append("use std::sync::{Arc, Mutex};")

        if "Receiver" in code or "Sender" in code or "channel" in code:
            imports.append("use std::sync::mpsc;")

        return "\n".join(imports)

    def _create_cargo_project(
        self, temp_dir: Path, code: str, fast: bool = False
    ) -> Path:
        """Create a cargo project for advanced compilation."""
        project_dir = temp_dir / "rust_project"
        project_dir.mkdir()


        cargo_toml = project_dir / "Cargo.toml"

        if fast:

            cargo_content = '''[package]
name = "pyrex_generated"
version = "0.1.0"
edition = "2021"

[dependencies]

[[bin]]
name = "main"
path = "src/main.rs"

[profile.dev]
opt-level = 0
debug = false
'''
        else:
            cargo_content = '''[package]
name = "pyrex_generated"
version = "0.1.0"
edition = "2021"

[dependencies]

[[bin]]
name = "main"
path = "src/main.rs"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"
strip = true

[profile.dev]
opt-level = 1
'''

        cargo_toml.write_text(cargo_content)


        src_dir = project_dir / "src"
        src_dir.mkdir()
        main_rs = src_dir / "main.rs"
        main_rs.write_text(code)

        return project_dir

    def _compile_with_rustc(
        self, source_file: Path, output_file: Path, fast: bool = False
    ) -> None:
        """Compile using rustc directly with appropriate flags."""
        rustc_flags = self._get_rustc_flags(fast)
        cmd = ["rustc"] + rustc_flags + [
            str(source_file), "-o", str(output_file)
        ]

        logger.debug(f"Compiling with rustc: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60 if fast else 120,
                cwd=source_file.parent,
            )

            if result.returncode != 0:
                raise PyrexCompileError(
                    "rustc compilation failed",
                    compiler_output=result.stderr,
                    context={
                        "command": cmd,
                        "stdout": result.stdout
                    }
                )

            if not output_file.exists():
                raise PyrexCompileError(
                    "rustc compilation succeeded but binary not found",
                    compiler_output=result.stderr,
                )

        except subprocess.TimeoutExpired:
            raise PyrexCompileError("rustc compilation timeout")

    def _compile_with_cargo(
        self, project_dir: Path, fast: bool = False
    ) -> Path:
        """Compile using cargo for better optimization and dependency management."""
        cargo_flags = self._get_cargo_flags(fast)

        try:
            result = subprocess.run(
                ["cargo"] + cargo_flags,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=90 if fast else 180,
            )

            if result.returncode != 0:
                raise PyrexCompileError(
                    "Cargo compilation failed",
                    compiler_output=result.stderr,
                    context={"stdout": result.stdout}
                )

            if fast:
                binary_paths = [
                    project_dir / "target" / "debug" / "main",
                    project_dir / "target" / "debug" / "main.exe",
                    project_dir / "target" / "release" / "main",
                    project_dir / "target" / "release" / "main.exe",
                ]
            else:
                binary_paths = [
                    project_dir / "target" / "release" / "main",
                    project_dir / "target" / "release" / "main.exe",
                    project_dir / "target" / "debug" / "main",
                    project_dir / "target" / "debug" / "main.exe",
                ]

            for binary_path in binary_paths:
                if binary_path.exists():
                    return binary_path

            raise PyrexCompileError(
                "Cargo compilation succeeded but binary not found",
                compiler_output=result.stderr,
            )

        except subprocess.TimeoutExpired:
            raise PyrexCompileError("Cargo compilation timeout")

    def execute_with_rustc(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        force_recompile: bool = False,
        fast: bool = False,
    ) -> str:
        """Execute Rust code using rustc directly (explicit method)."""
        if not self.has_rustc:
            raise PyrexRuntimeError("rustc not available")

        return self._execute_with_rustc(
            code, variables or {}, timeout or
            (10.0 if fast else self.config.default_timeout), force_recompile,
            fast
        )

    def execute_with_cargo(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        force_recompile: bool = False,
        fast: bool = False,
    ) -> str:
        """Execute Rust code using cargo for enhanced features (explicit method)."""
        if not self.has_cargo:
            raise PyrexRuntimeError("cargo not available")

        return self._execute_with_cargo(
            code, variables or {}, timeout or
            (10.0 if fast else self.config.default_timeout), force_recompile,
            fast
        )

    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code with proper Rust formatting."""
        indent = " " * spaces
        lines = code.split("\n")

        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append(indent + line)
            else:
                indented_lines.append("")

        return "\n".join(indented_lines)

    def get_compiler_info(self) -> Dict[str, Any]:
        """Get information about available Rust compilers."""
        return {
            "active_compiler": self.active_compiler,
            "capabilities": self.rust_capabilities,
            "compiler_type_preference": self.compiler_type,
            "use_cargo_for_dependencies": self.use_cargo_for_dependencies,
        }



rust = RustCompiler(
    CompilerConfig(
        enable_security=True,
        default_timeout=30.0,
    ),
    compiler_type="auto", 
    use_cargo_for_dependencies=True,
)


rust_rustc = RustCompiler(
    CompilerConfig(
        compile_flags=["-O", "--edition", "2021"],
        enable_security=True,
        default_timeout=30.0,
    ),
    compiler_type="rustc",
)

rust_cargo = RustCompiler(
    CompilerConfig(
        enable_security=True,
        default_timeout=45.0,
    ),
    compiler_type="cargo",
)
