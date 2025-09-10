<div align="center">

# 🚀 Pyrex

**Seamless inline Rust, C, and C++ execution inside Python — with enterprise-grade safety, performance, and simplicity**

[![PyPI](https://img.shields.io/pypi/v/pyrex?style=for-the-badge&color=blue)](https://pypi.org/project/pyrex/)
[![Python](https://img.shields.io/pypi/pyversions/pyrex?style=for-the-badge)](https://pypi.org/project/pyrex/)
[![License](https://img.shields.io/github/license/kendroooo/pyrex?style=for-the-badge)](https://github.com/kendroooo/pyrex/blob/main/LICENSE)

*Write native Rust, C, and C++ code inline with Python. Automatically compiled, cached, and sandboxed — ready for production.*

</div>

---

## ✨ Features

- 🦀 **Rust-first** – Full Rust support with automatic compilation  
- ⚡ **C & C++ support** – Modern C/C++ with type-safe bridging  
- 🔒 **Enterprise security** – Sandboxed execution, validation, and resource limits  
- 🚀 **Smart caching** – Compiles once, executes instantly on repeat  
- 🎯 **Type-safe** – Automatic Python ↔ native type conversion  
- 📊 **Detailed errors** – Rich compile/runtime diagnostics with context  
- 🔧 **Zero config** – Works out of the box, no setup needed  

---

## 🛠️ Installation

```bash
pip install pyrex
```

**Requirements:**  
You’ll need `rustc`, `gcc`/`clang`, and `g++`/`clang++` installed.

---

## 🚀 Quick Start

### Rust Example
```python
from pyrex.languages.rust import rust

result = rust.execute("""
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    println!("Sum: {}", sum);
""")
print(result)  # "Sum: 15"
```

### C Example
```python
from pyrex import c

result = c.execute("""
    int result = x * y + z;
    printf("Result: ```d\\n", result);
""", {"x": 10, "y": 20, "z": 5}, fast=True)

print(result)  # "Result: 205"
```

### C++ Example
```python
from pyrex import cpp

result = cpp.execute("""
    std::vector<int> data = numbers;
    std::sort(data.begin(), data.end());

    std::cout << "Sorted: ";
    for (int n : data) std::cout << n << " ";
    std::cout << std::endl;
""", variables={"numbers": [64, 34, 25, 12, 22, 11, 90]})
```

---

## 📚 Advanced Usage

### Custom Compiler Settings
```python
from pyrex import RustCompiler

compiler = RustCompiler(
    compile_flags=["-O", "--edition", "2021"],
    cache_dir="/tmp/pyrex_cache",
    enable_security=True
)

result = compiler.execute("""
    let result = (0..1_000_000).sum::<i64>();
    println!("Sum: {}", result);
""")
```

### Error Handling
```python
from pyrex.exceptions import PyrexCompileError, PyrexRuntimeError

try:
    rust.execute("let x = ;")  # Invalid syntax
except PyrexCompileError as e:
    print(f"Compilation failed at line {e.line_number}: {e.message}")
    print(f"Snippet:\n{e.code_snippet}")
```

---

## 🔒 Security

Pyrex enforces **enterprise-grade safety** out of the box:
- Static analysis for dangerous patterns  
- Sandboxed execution in temp directories  
- Input sanitization & type validation  
- Memory, CPU, and timeout limits  

---

## 🎯 Type Mapping

| Python Type  | Rust        | C           | C++                  |
|--------------|-------------|-------------|----------------------|
| `bool`       | `bool`      | `bool`      | `bool`              |
| `int`        | `i64`      | `long long` | `long long`          |
| `float`      | `f64`      | `double`    | `double`             |
| `str`        | `String`    | `char*`     | `std::string`        |
| `list[int]`  | `Vec<i64>`  | `int[]`     | `std::vector<int>`   |

---

## ⚡ Performance

- **First run:** Compiles & caches the binary  
- **Next runs:** Executes instantly (10–100× faster)  
- **Smart invalidation:** Cache refreshes automatically when code or variables change  

---

## 📖 API Reference

### `execute(code, variables={"key": "value"}, timeout=30.0, force_recompile=False, fast=True)`

**Parameters:**  
- `code` *(str)* – Source code to compile and run  
- `variables` *(dict, optional)* – Injected variables  
- `timeout` *(float, default=30s)* – Max runtime  
- `force_recompile` *(bool)* – Ignore cache, force rebuild 
- `fast` *(bool)*  – Skips few checks to get faster compilation

**Returns:**  
- Execution output as `str`

**Raises:**  
- `PyrexCompileError` – Compilation failed  
- `PyrexRuntimeError` – Runtime error  
- `PyrexTypeError` – Type conversion issue  
- `PyrexSecurityError` – Security violation  

---

## 🤝 Contributing

1. Fork this repository  
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes  
4. Submit a pull request 🎉  

---

## 📄 License

Licensed under the MIT License. See the [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- Built with ❤️ by Luciano Correia  
- Inspired by the need for **frictionless multi-language execution**  
- Thanks to all contributors and early testers  
