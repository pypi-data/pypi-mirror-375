"""
Pyrex - Professional multi-language code execution for Python.
This library provides seamless integration for executing Rust, C, and C++
code directly within Python applications with enterprise-grade safety and performance.
"""

__version__ = "1.2.0"
__author__ = "Luciano Correia"
__email__ = "sudo@shiro.lol"
__description__ = "Professional inline multi-language execution for Python"
from pyrex.languages.rust import rust
from pyrex.languages.c import c
from pyrex.languages.cpp import cpp
from pyrex.exceptions import (
    PyrexError,
    PyrexCompileError,
    PyrexRuntimeError,
    PyrexTypeError,
    PyrexSecurityError,
)

__all__ = [
    "rust",
    "c",
    "cpp",
    "PyrexError",
    "PyrexCompileError",
    "PyrexRuntimeError",
    "PyrexTypeError",
    "PyrexSecurityError",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
