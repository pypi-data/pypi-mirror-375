"""
C++ language implementation for Pyrex.
This module provides comprehensive C++ support with modern standards,
STL integration, and advanced compilation features with automatic header detection.
"""

import logging
import shutil
import tempfile
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from pyrex.core.base import BaseCompiler, CompilerConfig
from pyrex.core.types import CppTypeSystem
from pyrex.exceptions import PyrexRuntimeError

logger = logging.getLogger(__name__)


class CppCompiler(BaseCompiler):
    """
    Modern C++ compiler with STL support and automatic header detection.
    Supports C++17/C++20 standards with comprehensive STL integration,
    template support, modern C++ best practices, and automatic detection
    of required headers including <cmath>, <chrono>, and <iomanip>.
    """
    def __init__(self, config: Optional[CompilerConfig] = None) -> None:
        """Initialize C++ compiler with modern standards."""
        super().__init__(config)
        self.type_system = CppTypeSystem()
        self._detect_cpp_version()

    def get_language(self) -> str:
        return "cpp"

    def _get_default_compiler(self) -> str:
        for compiler in ["clang++", "g++", "c++"]:
            if shutil.which(compiler):
                return compiler
        return "g++"

    def _get_default_flags(self) -> List[str]:
        base_flags = [
            "-std=c++17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Wpedantic",  # Pedantic 
            "-Wno-unused-variable",
        ]
        if "clang++" in self.compiler_path or "g++" in self.compiler_path:
            base_flags.extend(
                [
                    "-fstack-protector-strong",
                    "-D_GLIBCXX_ASSERTIONS",  # STL debuggerrr
                    "-fPIC",
                ]
            )
        return base_flags

    def _get_fast_flags(self) -> List[str]:
        """Get fast compilation flags for lightning-fast builds."""
        return [
            "-std=c++17",
            "-O0",
            "-w",
        ]

    def _get_file_extension(self) -> str:
        return ".cpp"

    def execute(
        self,
        code: str,
        variables: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        force_recompile: bool = False,
        cpp_standard: Optional[str] = None,
        use_concepts: bool = False,
        fast: bool = False,
    ) -> str:
        """
        Execute C++ code with comprehensive STL support and modern features.
        Args:
            code: C++ source code to compile and execute
            variables: Dictionary of variables to inject into the code
            timeout: Maximum execution time in seconds
            force_recompile: Skip cache and force recompilation
            cpp_standard: Force specific C++ standard (e.g., "c++17", "c++20")
            use_concepts: Enable C++20 concepts if available
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
        if use_concepts and not fast:
            return self._execute_with_concepts(
                code, variables, timeout, force_recompile
            )
        if (
            cpp_standard and
            cpp_standard in getattr(self, "cpp_standards", []) and not fast
        ):
            return self._execute_with_standard(
                code, variables, timeout, force_recompile, cpp_standard
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
            if hasattr(self, "cpp_standard_override"):
                cache_suffix += f"_{self.cpp_standard_override}"
            cache_key = self._compute_cache_key(code, variables) + cache_suffix
            if not force_recompile:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    logger.debug(
                        f"Cache hit for C++ code{' (fast)' if fast else ''}"
                    )
                    return cached_result
            with tempfile.TemporaryDirectory(prefix="pyrex_cpp_") as temp_dir:
                temp_path = Path(temp_dir)
                wrapper_code = self._generate_wrapper_code(
                    code, variables, fast
                )
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
                    if not fast:
                        parsed_error = self.error_parser.parse_runtime_error(
                            stderr
                        )
                        raise PyrexRuntimeError(
                            f"Runtime error in C++ code",
                            stderr=stderr,
                            exit_code=exit_code,
                            context={
                                "parsed": parsed_error,
                                "stdout": stdout,
                            },
                        )
                    else:
                        raise PyrexRuntimeError(
                            f"Runtime error in C++ code (fast mode)",
                            stderr=stderr,
                            exit_code=exit_code,
                        )
                result = stdout.strip()
                self.cache_manager.set(cache_key, result, "cpp")
                logger.debug(
                    f"Successfully executed C++ code{' (fast)' if fast else ''}"
                )
                return result

    def _execute_with_concepts(
        self,
        code: str,
        variables: Dict[str, Any],
        timeout: float,
        force_recompile: bool,
    ) -> str:
        """Execute C++ code with C++20 concepts if available."""
        if "c++20" not in getattr(self, "cpp_standards", []):
            logger.warning("C++20 not supported, falling back to C++17")
            return self.execute(code, variables, timeout, force_recompile)
        return self._execute_with_standard(
            code, variables, timeout, force_recompile, "c++20"
        )

    def _execute_with_standard(
        self,
        code: str,
        variables: Dict[str, Any],
        timeout: float,
        force_recompile: bool,
        standard: str,
    ) -> str:
        """Execute C++ code with a specific standard."""
        original_flags = self.compile_flags.copy()
        try:
            self.compile_flags = [
                flag if not flag.startswith("-std=") else f"-std={standard}"
                for flag in self.compile_flags
            ]
            if not any(flag.startswith("-std=") for flag in self.compile_flags):
                self.compile_flags.append(f"-std={standard}")
            self.cpp_standard_override = standard
            return self._execute_internal(
                code, variables, timeout, force_recompile, False
            )
        finally:
            self.compile_flags = original_flags
            if hasattr(self, "cpp_standard_override"):
                delattr(self, "cpp_standard_override")

    def _detect_cpp_version(self) -> None:
        """Detect the highest C++ standard supported."""
        import subprocess

        self.cpp_standards = []
        for std in ["c++20", "c++17", "c++14", "c++11"]:
            try:
                result = subprocess.run(
                    [
                        self.compiler_path,
                        f"-std={std}",
                        "-x",
                        "c++",
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
                    self.cpp_standards.append(std)
            except:
                continue
        if self.cpp_standards:
            logger.debug(
                f"C++ compiler supports standards: {', '.join(self.cpp_standards)}"
            )
            if "c++20" in self.cpp_standards:
                self._update_std_flag("c++20")
            elif "c++17" in self.cpp_standards:
                self._update_std_flag("c++17")

    def _update_std_flag(self, standard: str) -> None:
        """Update the C++ standard flag."""
        for i, flag in enumerate(self.compile_flags):
            if flag.startswith("-std="):
                self.compile_flags[i] = f"-std={standard}"
                break

    def _generate_wrapper_code(
        self, code: str, variables: Dict[str, Any], fast: bool = False
    ) -> str:
        """Generate modern C++ wrapper with STL and smart features."""
        if fast:
            return self._generate_fast_wrapper(code, variables)
        else:
            return self._generate_full_wrapper(code, variables)

    def _generate_fast_wrapper(
        self, code: str, variables: Dict[str, Any]
    ) -> str:
        """Generate simplified C++ wrapper for fast mode with comprehensive header detection."""
        var_declarations = []
        for name, value in variables.items():
            if isinstance(value, bool):
                var_declarations.append(
                    f"    bool {name} = {'true' if value else 'false'};"
                )
            elif isinstance(value, int):
                var_declarations.append(f"    long long {name} = {value};")
            elif isinstance(value, float):
                var_declarations.append(f"    double {name} = {value};")
            elif isinstance(value, str):
                var_declarations.append(f'    std::string {name} = "{value}";')
            elif isinstance(value, (list, tuple)) and value:
                elements = ", ".join(str(item) for item in value)
                var_declarations.append(
                    f"    std::vector<int> {name} = {{{elements}}};"
                )
            else:
                var_declarations.append(f'    std::string {name} = "{value}";')
        function_definitions = self._extract_function_definitions(code)
        clean_user_code = self._remove_function_definitions(code)
        wrapper = f"""// Fast-mode C++ wrapper by Pyrex
{self._get_fast_headers(code)}
using namespace std;
{chr(10).join(function_definitions)}
int main() {{
{chr(10).join(var_declarations)}
{self._indent_code(clean_user_code, 4)}
    return 0;
}}
"""
        return wrapper

    def _get_fast_headers(self, code: str) -> str:
        """Get essential headers for fast mode with comprehensive code analysis."""
        headers = [
            "#include <iostream>",
            "#include <vector>",
            "#include <string>",
        ]
        if any(
            item in code for item in [
                "chrono",
                "high_resolution_clock",
                "duration_cast",
                "microseconds",
                "milliseconds",
                "nanoseconds",
                "steady_clock",
                "system_clock",
            ]
        ):
            headers.append("#include <chrono>")
        if any(
            item in code for item in [
                "fixed",
                "setprecision",
                "setw",
                "setfill",
                "left",
                "right",
                "internal",
                "hex",
                "dec",
                "oct",
            ]
        ):
            headers.append("#include <iomanip>")
        if any(
            item in code for item in [
                "algorithm",
                "sort",
                "transform",
                "for_each",
                "find",
                "count",
                "reverse",
                "unique",
                "partition",
            ]
        ):
            headers.append("#include <algorithm>")
        if any(
            item in code for item in [
                "accumulate",
                "inner_product",
                "iota",
                "adjacent_difference",
                "partial_sum",
            ]
        ):
            headers.append("#include <numeric>")
        if any(
            item in code for item in [
                "random_device",
                "mt19937",
                "shuffle",
                "uniform_int_distribution",
                "normal_distribution",
            ]
        ):
            headers.append("#include <random>")
        if any(item in code for item in ["map", "unordered_map"]):
            headers.append("#include <map>")
            headers.append("#include <unordered_map>")
        if any(item in code for item in ["set", "unordered_set"]):
            headers.append("#include <set>")
            headers.append("#include <unordered_set>")
        if any(item in code for item in ["queue", "priority_queue"]):
            headers.append("#include <queue>")
        if any(item in code for item in ["stack"]):
            headers.append("#include <stack>")
        if any(item in code for item in ["deque"]):
            headers.append("#include <deque>")
        if any(item in code for item in ["list", "forward_list"]):
            headers.append("#include <list>")
        if any(
            item in code
            for item in ["function", "bind", "lambda", "placeholders"]
        ):
            headers.append("#include <functional>")
        if any(
            item in code
            for item in ["pair", "make_pair", "tuple", "make_tuple"]
        ):
            headers.append("#include <utility>")
            headers.append("#include <tuple>")
        if any(
            func in code for func in [
                "sqrt",
                "sin",
                "cos",
                "tan",
                "exp",
                "log",
                "pow",
                "ceil",
                "floor",
                "round",
                "abs",
                "fabs",
                "atan",
                "asin",
                "acos",
                "sinh",
                "cosh",
                "tanh",
            ]
        ):
            headers.append("#include <cmath>")
        if any(
            item in code for item in
            ["unique_ptr", "shared_ptr", "make_unique", "make_shared"]
        ):
            headers.append("#include <memory>")
        if any(
            item in code
            for item in ["stringstream", "istringstream", "ostringstream"]
        ):
            headers.append("#include <sstream>")
        if any(item in code for item in ["ifstream", "ofstream", "fstream"]):
            headers.append("#include <fstream>")
        return "\n".join(sorted(set(headers)))

    def _generate_full_wrapper(
        self, code: str, variables: Dict[str, Any]
    ) -> str:
        """Generate full-featured C++ wrapper for normal mode."""
        required_headers = self._analyze_required_headers(code)
        namespace_usage = self._analyze_namespace_usage(code, variables)
        function_definitions = self._extract_function_definitions(code)
        var_declarations = []
        for name, value in variables.items():
            cpp_type = self.type_system.get_native_type(value)
            cpp_value = self.type_system.convert_to_native(value)
            if self._should_use_auto(cpp_type, value):
                var_declarations.append(f"    auto {name} = {cpp_value};")
            else:
                var_declarations.append(f"    {cpp_type} {name} = {cpp_value};")
        clean_user_code = self._remove_function_definitions(code)
        wrapper = self._get_cpp_template().format(
            includes=self._get_required_includes(code, required_headers),
            namespaces=self._get_namespace_declarations(code, namespace_usage),
            function_definitions="\n".join(function_definitions),
            variable_declarations="\n".join(var_declarations),
            user_code=self._indent_code(clean_user_code, 4),
        )
        return wrapper

    def _extract_function_definitions(self, code: str) -> List[str]:
        """Extract function definitions from user code."""
        function_defs = []
        function_pattern = re.compile(
            r"^\s*((?:inline\s+)?(?:static\s+)?(?:virtual\s+)?(?:const\s+)?"
            r"(?:unsigned\s+|signed\s+)?"
            r"(?:long\s+long|long|short|int|float|double|char|bool|void|auto|\w+)"
            r"(?:\s*\*+|\s*&+|\s+)"
            r"(?:const\s+)?"
            r"(\w+)\s*\([^)]*\)\s*(?:const\s+)?(?:noexcept\s*(?:\([^)]*\))?\s*)?"
            r"\{)",
            re.MULTILINE | re.DOTALL,
        )
        lines = code.split("\n")
        current_function = []
        brace_count = 0
        in_function = False
        function_start_line = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("#"):
                if not in_function:
                    continue
            if not in_function and function_pattern.search(line):
                in_function = True
                function_start_line = i
                current_function = [line]
                brace_count = line.count("{") - line.count("}")
                continue
            if in_function:
                current_function.append(line)
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0:
                    func_def = "\n".join(current_function)
                    function_defs.append(func_def)
                    current_function = []
                    in_function = False
        return function_defs

    def _remove_function_definitions(self, code: str) -> str:
        """Remove function definitions from code, leaving only the main logic."""
        function_defs = self._extract_function_definitions(code)
        clean_code = code
        for func_def in function_defs:
            clean_code = clean_code.replace(func_def, "")
        lines = clean_code.split("\n")
        clean_lines = []
        for line in lines:
            if line.strip():
                clean_lines.append(line)
            elif (clean_lines and clean_lines[-1].strip()):
                clean_lines.append(line)
        return "\n".join(clean_lines)

    def _should_use_auto(self, cpp_type: str, value: Any) -> bool:
        """Determine if 'auto' should be used instead of explicit type."""
        complex_types = [
            "std::vector",
            "std::string",
            "std::map",
            "std::unordered_map",
            "std::set",
            "std::unordered_set",
            "std::pair",
            "std::tuple",
        ]
        return any(cpp_type.startswith(t) for t in complex_types)

    def _analyze_required_headers(self, code: str) -> Set[str]:
        """Analyze code to determine required headers."""
        required = set()
        if re.search(r"\b(vector|map|set|list|deque|array)\b", code):
            required.update(["vector", "map", "set", "list", "deque", "array"])
        if re.search(
            r"\b(sort|find|transform|for_each|count|accumulate)\b", code
        ):
            required.update(["algorithm", "numeric"])
        if re.search(
            r"\b(cout|cin|cerr|endl|ifstream|ofstream|stringstream)\b", code
        ):
            required.update(["iostream", "fstream", "sstream"])
        if re.search(
            r"\b(unique_ptr|shared_ptr|make_unique|make_shared)\b", code
        ):
            required.add("memory")
        if re.search(r"\b(pair|tuple|make_pair|get)\b", code):
            required.update(["utility", "tuple"])
        if re.search(r"\b(thread|mutex|lock|condition_variable)\b", code):
            required.update(["thread", "mutex"])
        if re.search(
            r"\b(chrono|duration|time_point|high_resolution_clock)\b", code
        ):
            required.add("chrono")
        if re.search(
            r"\b(sqrt|sin|cos|tan|exp|log|pow|abs|floor|ceil)\b", code
        ):
            required.add("cmath")
        if re.search(r"\b(random|mt19937|uniform_|normal_)\b", code):
            required.add("random")
        if re.search(r"\b(function|bind|lambda)\b", code):
            required.add("functional")
        if re.search(r"\b(fixed|setprecision|setw)\b", code):
            required.add("iomanip")
        return required

    def _analyze_namespace_usage(self, code: str,
                                 variables: Dict[str, Any]) -> Dict[str, bool]:
        """Analyze which namespace declarations are needed."""
        usage = {
            "std": False,
            "std_selective": set(),
            "custom_namespaces": set(),
        }
        std_usage_count = len(re.findall(r"\bstd::", code))
        total_std_identifiers = len(
            re.findall(r"\b(cout|cin|vector|string|map|sort|endl)\b", code)
        )
        if std_usage_count > 5 or total_std_identifiers > 8:
            usage["std"] = True
        else:
            common_std_items = [
                "cout",
                "cin",
                "cerr",
                "endl",
                "string",
                "vector",
                "map",
                "set",
                "pair",
                "make_pair",
                "sort",
                "find",
                "begin",
                "end",
            ]
            for item in common_std_items:
                if re.search(rf"\b{item}\b",
                             code) and not re.search(rf"std::{item}", code):
                    usage["std_selective"].add(item)
        custom_ns_matches = re.findall(r"(\w+)::\w+", code)
        for match in custom_ns_matches:
            if match != "std":
                usage["custom_namespaces"].add(match)
        return usage

    def _get_cpp_template(self) -> str:
        """Get the C++ code template with modern features."""
        return """// Auto-generated C++ wrapper by Pyrex
{includes}
{namespaces}
{function_definitions}
int main() {{
{variable_declarations}
    // === User code begins ===
{user_code}
    // === User code ends ===
    return 0;
}}
"""

    def _get_required_includes(
        self, code: str, required_headers: Set[str]
    ) -> str:
        """Generate appropriate #include statements."""
        includes = [
            "#include <iostream>",
        ]
        header_map = {
            "vector": "#include <vector>",
            "string": "#include <string>",
            "map": "#include <map>",
            "set": "#include <set>",
            "list": "#include <list>",
            "deque": "#include <deque>",
            "array": "#include <array>",
            "algorithm": "#include <algorithm>",
            "numeric": "#include <numeric>",
            "iostream": "#include <iostream>",
            "fstream": "#include <fstream>",
            "sstream": "#include <sstream>",
            "memory": "#include <memory>",
            "utility": "#include <utility>",
            "tuple": "#include <tuple>",
            "thread": "#include <thread>",
            "mutex": "#include <mutex>",
            "chrono": "#include <chrono>",
            "cmath": "#include <cmath>",
            "random": "#include <random>",
            "functional": "#include <functional>",
            "iomanip": "#include <iomanip>",
        }
        for header in sorted(required_headers):
            if header in header_map and header_map[header] not in includes:
                includes.append(header_map[header])
        if "unordered_map" in code or "unordered_set" in code:
            includes.append("#include <unordered_map>")
            includes.append("#include <unordered_set>")
        if "queue" in code or "priority_queue" in code:
            includes.append("#include <queue>")
        if "stack" in code:
            includes.append("#include <stack>")
        return "\n".join(sorted(set(includes)))

    def _get_namespace_declarations(
        self, code: str, usage: Dict[str, bool]
    ) -> str:
        """Generate appropriate namespace declarations based on usage analysis."""
        declarations = []
        if usage["std"]:
            declarations.append("using namespace std;")
        else:
            if usage["std_selective"]:
                for item in sorted(usage["std_selective"]):
                    declarations.append(f"using std::{item};")
        for ns in sorted(usage["custom_namespaces"]):
            declarations.append(
                f"// using namespace {ns};  // Uncomment if needed"
            )
        if not declarations:
            common_items = []
            if "cout" in code and "std::cout" not in code:
                common_items.append("cout")
            if "cin" in code and "std::cin" not in code:
                common_items.append("cin")
            if "endl" in code and "std::endl" not in code:
                common_items.append("endl")
            if "string" in code and "std::string" not in code:
                common_items.append("string")
            if "vector" in code and "std::vector" not in code:
                common_items.append("vector")
            for item in common_items:
                declarations.append(f"using std::{item};")
        return "\n".join(
            declarations
        ) if declarations else "using namespace std;"

    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent C++ code with proper formatting."""
        indent = " " * spaces
        lines = code.split("\n")
        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append(indent + line)
            else:
                indented_lines.append("")
        return "\n".join(indented_lines)


cpp = CppCompiler(
    CompilerConfig(
        compile_flags=[
            "-std=c++17",
            "-O2",
            "-Wall",
            "-Wextra",
            "-fstack-protector-strong",
        ],
        enable_security=True,
        default_timeout=30.0,
    )
)
