"""
C language implementation for Pyrex.
This module provides comprehensive C support with modern C standards,
security features, and optimized compilation with automatic math library linking.
"""

import logging
import shutil
import tempfile
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from pyrex.core.base import BaseCompiler, CompilerConfig
from pyrex.core.types import CTypeSystem
from pyrex.exceptions import PyrexCompileError, PyrexRuntimeError

logger = logging.getLogger(__name__)


class CCompiler(BaseCompiler):
    """
    Modern C compiler with security features and automatic math library linking.
    Supports C11/C17 standards with comprehensive security checks,
    memory safety analysis, and automatic detection of math functions
    requiring the math library (-lm flag).
    """
    def __init__(self, config: Optional[CompilerConfig] = None) -> None:
        """Initialize C compiler with modern standards."""
        super().__init__(config)
        self.type_system = CTypeSystem()
        self._detect_compiler_capabilities()

    def get_language(self) -> str:
        return "c"

    def _get_default_compiler(self) -> str:
        for compiler in ["clang", "gcc", "cc"]:
            if shutil.which(compiler):
                return compiler
        return "gcc"

    def _get_default_flags(self) -> List[str]:
        base_flags = [
            "-std=c17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror=implicit-function-declaration",
            "-Wformat=2",
            "-Wstrict-prototypes",
        ]
        if "clang" in self.compiler_path or "gcc" in self.compiler_path:
            base_flags.extend(
                [
                    "-fstack-protector-strong",
                    "-D_FORTIFY_SOURCE=2",
                    "-fPIC",
                ]
            )
        return base_flags

    def _get_fast_flags(self) -> List[str]:
        """Get fast compilation flags for lightning-fast builds."""
        return [
            "-std=c17",
            "-O0",
            "-w",
        ]

    def _get_file_extension(self) -> str:
        return ".c"

    def _get_math_functions(self) -> List[str]:
        """Get list of math functions that require -lm linking."""
        return [
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "atan2",
            "sinh",
            "cosh",
            "tanh",
            "asinh",
            "acosh",
            "atanh",
            "exp",
            "exp2",
            "exp10",
            "expm1",
            "log",
            "log10",
            "log2",
            "log1p",
            "pow",
            "sqrt",
            "cbrt",
            "hypot",
            "ceil",
            "floor",
            "round",
            "trunc",
            "fabs",
            "fabsf",
            "fabsl",
            "fmod",
            "fmodf",
            "fmodl",
            "frexp",
            "frexpf",
            "frexpl",
            "ldexp",
            "ldexpf",
            "ldexpl",
            "modf",
            "modff",
            "modfl",
            "scalbn",
            "scalbln",
            "erf",
            "erfc",
            "lgamma",
            "tgamma",
            "j0",
            "j1",
            "jn",
            "y0",
            "y1",
            "yn",
        ]

    def _needs_math_library(self, code: str) -> bool:
        """Check if code contains math functions requiring -lm."""
        math_functions = self._get_math_functions()
        return any(func in code for func in math_functions)

    def execute(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        force_recompile: bool = False,
        use_sanitizers: bool = False,
        fast: bool = False,
    ) -> str:
        """
        Execute C code with comprehensive safety and optimization features.
        Args:
            code: C source code to compile and execute
            variables: Dictionary of variables to inject into the code
            timeout: Maximum execution time in seconds
            force_recompile: Skip cache and force recompilation
            use_sanitizers: Enable AddressSanitizer and UndefinedBehaviorSanitizer
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
        timeout = timeout or (5.0 if fast else self.config.default_timeout)
        if use_sanitizers and not fast:
            return self._execute_with_sanitizers(
                code, variables, timeout, force_recompile
            )
        if fast:
            original_flags = self.compile_flags.copy()
            self.compile_flags = self._get_fast_flags()
            try:
                return self._execute_internal(
                    code, variables, timeout, force_recompile, fast
                )
            finally:
                self.compile_flags = original_flags
        else:
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
        with self._lock:
            if not fast:
                self._validate_inputs(code, variables, timeout)
            cache_suffix = "_fast" if fast else ""
            cache_key = self._compute_cache_key(code, variables) + cache_suffix
            if not force_recompile:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(
                        f"Cache hit for C code{' (fast)' if fast else ''}"
                    )
                    return cached_result
            with tempfile.TemporaryDirectory(prefix="pyrex_c_") as temp_dir:
                temp_path = Path(temp_dir)
                wrapper_code = self._generate_wrapper_code(
                    code, variables, fast
                )
                source_file = temp_path / f"main{self._get_file_extension()}"
                source_file.write_text(wrapper_code, encoding="utf-8")
                binary_file = temp_path / "main"
                if os.name == "nt":  # type: ignore
                    binary_file = binary_file.with_suffix(".exe")
                self._compile_code_with_math_linking(
                    source_file, binary_file, code
                )
                stdout, stderr, exit_code = self._execute_binary(
                    binary_file, timeout
                )
                if exit_code != 0:
                    if not fast:
                        parsed_error = self.error_parser.parse_runtime_error(
                            stderr
                        )
                        raise PyrexRuntimeError(
                            f"Runtime error in C code",
                            stderr=stderr,
                            exit_code=exit_code,
                            context={
                                "parsed": parsed_error,
                                "stdout": stdout,
                            },
                        )
                    else:
                        raise PyrexRuntimeError(
                            f"Runtime error in C code (fast mode)",
                            stderr=stderr,
                            exit_code=exit_code,
                        )
                result = stdout.strip()
                self.cache_manager.set(cache_key, result, "c")
                logger.debug(
                    f"Successfully executed C code{' (fast)' if fast else ''}"
                )
                return result

    def _compile_code_with_math_linking(
        self, source_file: Path, output_file: Path, original_code: str
    ) -> None:
        """Compile C code with automatic math library linking when needed."""
        cmd = (
            [self.compiler_path] + self.compile_flags +
            [str(source_file), "-o", str(output_file)]
        )
        if self._needs_math_library(original_code):
            cmd.append("-lm")
            logger.debug("Adding -lm flag for math library linking")
        logger.debug(f"Compiling C code: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=source_file.parent,
            )
            if result.returncode != 0:
                raise PyrexCompileError(
                    "C compilation failed",
                    compiler_output=result.stderr,
                    context={
                        "command": cmd,
                        "stdout": result.stdout
                    },
                )
            if not output_file.exists():
                raise PyrexCompileError(
                    "C compilation succeeded but binary not found",
                    compiler_output=result.stderr,
                )
        except subprocess.TimeoutExpired:
            raise PyrexCompileError("C compilation timeout")

    def _execute_with_sanitizers(
        self,
        code: str,
        variables: Dict[str, Any],
        timeout: float,
        force_recompile: bool,
    ) -> str:
        """Execute C code with AddressSanitizer and other sanitizers enabled."""
        if not self.compiler_features.get("sanitizers", False):
            logger.warning(
                "Sanitizers not supported by compiler, falling back to normal execution"
            )
            return self.execute(
                code, variables, timeout, force_recompile, use_sanitizers=False
            )
        original_flags = self.compile_flags.copy()
        try:
            sanitizer_flags = [
                "-fsanitize=address",  # AddressSanitizer
                "-fsanitize=undefined",  # UndefinedBehaviorSanitizer
                "-fsanitize=signed-integer-overflow",
                "-fno-omit-frame-pointer",
                "-g",
                "-O1",
            ]
            self.compile_flags = [
                flag
                for flag in self.compile_flags if not flag.startswith("-O")
            ]
            self.compile_flags.extend(sanitizer_flags)
            return self._execute_internal(
                code, variables, timeout, force_recompile, False
            )
        finally:
            self.compile_flags = original_flags

    def _generate_wrapper_code(
        self, code: str, variables: Dict[str, Any], fast: bool = False
    ) -> str:
        """Generate secure C wrapper with proper headers and error checking."""
        var_declarations = []
        for name, value in variables.items():
            if fast:
                if isinstance(value, bool):
                    var_declarations.append(
                        f"    bool {name} = {'true' if value else 'false'};"
                    )
                elif isinstance(value, int):
                    var_declarations.append(f"    long long {name} = {value};")
                elif isinstance(value, float):
                    var_declarations.append(f"    double {name} = {value};")
                elif isinstance(value, str):
                    var_declarations.append(f'    char* {name} = "{value}";')
                elif isinstance(value, (list, tuple)) and value:
                    array_size = len(value)
                    elements = ", ".join(str(item) for item in value)
                    var_declarations.append(
                        f"    int {name}[{array_size}] = {{{elements}}};"
                    )
                else:
                    var_declarations.append(f'    char* {name} = "{value}";')
            else:
                c_type = self.type_system.get_native_type(value)
                c_value = self.type_system.convert_to_native(value)
                if isinstance(value, (list, tuple)) and value:
                    array_size = len(value)
                    if c_type.endswith("*"):
                        base_type = c_type[:-1]
                        var_declarations.append(
                            f"    {base_type} {name}[{array_size}] = {c_value};"
                        )
                    else:
                        var_declarations.append(
                            f"    {c_type} {name} = {c_value};"
                        )
                else:
                    var_declarations.append(f"    {c_type} {name} = {c_value};")
        if fast:
            wrapper = f"""// Fast-mode C wrapper by Pyrex
{self._get_fast_headers(code)}
int main(void) {{
{chr(10).join(var_declarations)}
{self._indent_code(code, 4)}
    return 0;
}}
"""
        else:
            wrapper = self._get_c_template().format(
                headers=self._get_required_headers(code),
                variable_declarations="\n".join(var_declarations),
                user_code=self._indent_code(code, 4),
                safety_checks=self._generate_safety_checks(),
            )
        return wrapper

    def _get_fast_headers(self, code: str) -> str:
        """Get essential headers for fast mode with comprehensive code analysis."""
        headers = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <stdbool.h>",
        ]
        if any(
            func in code
            for func in ["clock", "clock_t", "CLOCKS_PER_SEC", "time"]
        ):
            headers.append("#include <time.h>")
        if self._needs_math_library(code):
            headers.append("#include <math.h>")
        if "assert" in code:
            headers.append("#include <assert.h>")
        if any(
            func in code
            for func in ["isalpha", "isdigit", "tolower", "toupper"]
        ):
            headers.append("#include <ctype.h>")
        if "errno" in code:
            headers.append("#include <errno.h>")
        return "\n".join(sorted(set(headers)))

    def _detect_compiler_capabilities(self) -> None:
        """Detect what features the C compiler supports."""
        self.compiler_features = {
            "sanitizers": False,
            "lto": False,
            "security_flags": False,
            "math_library": True,  # tempfix
        }
        try:
            result = subprocess.run(
                [
                    self.compiler_path,
                    "-fsanitize=address",
                    "-x",
                    "c",
                    "-",
                    "-o",
                    "/dev/null",
                ],
                input="int main(){return 0;}",
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                self.compiler_features["sanitizers"] = True
                logger.debug("C compiler supports sanitizers")
        except:
            pass
        try:
            result = subprocess.run(
                [
                    self.compiler_path, "-flto", "-x", "c", "-", "-o",
                    "/dev/null"
                ],
                input="int main(){return 0;}",
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                self.compiler_features["lto"] = True
                logger.debug("C compiler supports LTO")
        except:
            pass
        try:
            result = subprocess.run(
                [self.compiler_path, "-lm", "-x", "c", "-", "-o", "/dev/null"],
                input="#include <math.h>\nint main(){sqrt(4.0); return 0;}",
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                self.compiler_features["math_library"] = True
                logger.debug("C compiler supports math library")
            else:
                self.compiler_features["math_library"] = False
                logger.warning("Math library not available")
        except:
            pass

    def _get_c_template(self) -> str:
        """Get the C code template with security features."""
        return """// Auto-generated C wrapper by Pyrex
{headers}
// Safety macros
    if ((src) && (dst) && (size) > 0) {{ \\
        strncpy(dst, src, (size)-1); \\
        (dst)[(size)-1] = '\\0'; \\
    }} \\
}} while(0)
int main(void) {{
{safety_checks}
{variable_declarations}
    // === User code begins ===
{user_code}
    // === User code ends ===
    return 0;
}}
"""

    def _get_required_headers(self, code: str) -> str:
        """Analyze code and include necessary headers."""
        headers = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <stdbool.h>",
        ]
        if any(
            func in code for func in ["malloc", "calloc", "realloc", "free"]
        ):
            if "#include <stdlib.h>" not in headers:
                headers.append("#include <stdlib.h>")
        if any(
            func in code
            for func in ["clock", "clock_t", "CLOCKS_PER_SEC", "time"]
        ):
            headers.append("#include <time.h>")
        if self._needs_math_library(code):
            headers.append("#include <math.h>")
        if "assert" in code:
            headers.append("#include <assert.h>")
        if any(
            func in code
            for func in ["isalpha", "isdigit", "tolower", "toupper"]
        ):
            headers.append("#include <ctype.h>")
        if "errno" in code:
            headers.append("#include <errno.h>")
        return "\n".join(sorted(set(headers)))

    def _generate_safety_checks(self) -> str:
        """Generate runtime safety checks."""
        return """    // Runtime safety initialization
    setvbuf(stdout, NULL, _IONBF, 0);  // Unbuffered output
    setvbuf(stderr, NULL, _IONBF, 0);  // Unbuffered errors"""

    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent C code with proper formatting."""
        indent = " " * spaces
        lines = code.split("\n")
        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append(indent + line)
            else:
                indented_lines.append("")
        return "\n".join(indented_lines)


c = CCompiler(
    CompilerConfig(
        compile_flags=[
            "-std=c17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-fstack-protector-strong",
            "-D_FORTIFY_SOURCE=2",
        ],
        enable_security=True,
        default_timeout=30.0,
    )
)
