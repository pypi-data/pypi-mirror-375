"""
Type system for automatic Python to native language type conversion.
This module provides sophisticated type mapping and conversion capabilities
for seamless integration between Python and compiled languages.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, Union
from pyrex.exceptions import PyrexTypeError


@dataclass
class TypeMapping:
    """Represents a mapping between Python and native language types."""

    python_type: Type
    native_type: str
    converter: callable
    validator: Optional[callable] = None


class TypeSystem(ABC):
    """Abstract base class for language-specific type systems."""
    def __init__(self) -> None:
        self._type_mappings: Dict[Type, TypeMapping] = {}
        self._setup_type_mappings()

    @abstractmethod
    def _setup_type_mappings(self) -> None:
        """Setup type mappings for the specific language."""
        pass

    @abstractmethod
    def get_language(self) -> str:
        """Return the language name."""
        pass

    def register_type_mapping(self, mapping: TypeMapping) -> None:
        """Register a new type mapping."""
        self._type_mappings[mapping.python_type] = mapping

    def get_native_type(self, python_value: Any) -> str:
        """Get the native type string for a Python value."""
        python_type = type(python_value)
        if isinstance(python_value, (list, tuple)):
            if not python_value:
                return self._get_default_collection_type()
            element_type = self._infer_collection_element_type(python_value)
            return self._get_collection_type(element_type)
        if python_type in self._type_mappings:
            return self._type_mappings[python_type].native_type
        return self._get_fallback_type()

    def convert_to_native(self, python_value: Any) -> str:
        """Convert a Python value to its native representation."""
        python_type = type(python_value)
        if isinstance(python_value, (list, tuple)):
            return self._convert_collection(python_value)
        if python_type in self._type_mappings:
            mapping = self._type_mappings[python_type]
            if mapping.validator and not mapping.validator(python_value):
                raise PyrexTypeError(
                    f"Value validation failed for {python_type.__name__}",
                    python_type=python_type,
                    target_language=self.get_language(),
                )
            return mapping.converter(python_value)
        return self._convert_fallback(python_value)

    @abstractmethod
    def _get_default_collection_type(self) -> str:
        """Get default type for empty collections."""
        pass

    @abstractmethod
    def _get_collection_type(self, element_type: str) -> str:
        """Get collection type for given element type."""
        pass

    @abstractmethod
    def _get_fallback_type(self) -> str:
        """Get fallback type for unsupported types."""
        pass

    @abstractmethod
    def _convert_collection(self, collection: Union[list, tuple]) -> str:
        """Convert a collection to native representation."""
        pass

    @abstractmethod
    def _convert_fallback(self, value: Any) -> str:
        """Convert unsupported type to native representation."""
        pass

    def _infer_collection_element_type(
        self, collection: Union[list, tuple]
    ) -> str:
        """Infer the element type of a collection."""
        if not collection:
            return "int"
        first_element = collection[0]
        element_type = type(first_element)
        if all(type(item) == element_type for item in collection):
            if element_type in self._type_mappings:
                return self._type_mappings[element_type].native_type
        return self._get_fallback_type()


class RustTypeSystem(TypeSystem):
    """Type system for Rust language."""
    def _setup_type_mappings(self) -> None:
        """Setup Rust-specific type mappings."""
        self.register_type_mapping(
            TypeMapping(
                python_type=bool,
                native_type="bool",
                converter=lambda x: "true" if x else "false",
            )
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=int,
                native_type="isize",
                converter=lambda x: f"{x}usize" if x >= 0 else f"{x}isize", # fixed
            )
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=float,
                native_type="f64",
                converter=lambda x: f"{x}f64"
            )
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=str,
                native_type="String",
                converter=lambda x: f'"{x}".to_string()',
            )
        )

    def get_language(self) -> str:
        return "rust"

    def _get_default_collection_type(self) -> str:
        return "Vec<usize>"

    def _get_collection_type(self, element_type: str) -> str:
        return f"Vec<{element_type}>"

    def _get_fallback_type(self) -> str:
        return "String"

    def _convert_collection(self, collection: Union[list, tuple]) -> str:
        elements = []
        for item in collection:
            if isinstance(item, int):
                elements.append(
                    f"{item}usize" if item >= 0 else f"{item}isize"
                )
            else:
                elements.append(self.convert_to_native(item))
        return f"vec![{', '.join(elements)}]"

    def _convert_fallback(self, value: Any) -> str:
        return f'"{value}".to_string()'


class CTypeSystem(TypeSystem):
    """Type system for C language."""
    def _setup_type_mappings(self) -> None:
        """Setup C-specific type mappings."""
        self.register_type_mapping(
            TypeMapping(
                python_type=bool,
                native_type="bool",
                converter=lambda x: "true" if x else "false",
            )
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=int, native_type="long long", converter=str
            )
        )
        self.register_type_mapping(
            TypeMapping(python_type=float, native_type="double", converter=str)
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=str,
                native_type="char*",
                converter=lambda x: f'"{x}"'
            )
        )

    def get_language(self) -> str:
        return "c"

    def _get_default_collection_type(self) -> str:
        return "int*"

    def _get_collection_type(self, element_type: str) -> str:
        return f"{element_type}*"

    def _get_fallback_type(self) -> str:
        return "char*"

    def _convert_collection(self, collection: Union[list, tuple]) -> str:
        elements = [self.convert_to_native(item) for item in collection]
        return f"{{{', '.join(elements)}}}"

    def _convert_fallback(self, value: Any) -> str:
        return f'"{value}"'


class CppTypeSystem(TypeSystem):
    """Type system for C++ language."""
    def _setup_type_mappings(self) -> None:
        """Setup C++-specific type mappings."""
        self.register_type_mapping(
            TypeMapping(
                python_type=bool,
                native_type="bool",
                converter=lambda x: "true" if x else "false",
            )
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=int, native_type="long long", converter=str
            )
        )
        self.register_type_mapping(
            TypeMapping(python_type=float, native_type="double", converter=str)
        )
        self.register_type_mapping(
            TypeMapping(
                python_type=str,
                native_type="std::string",
                converter=lambda x: f'std::string("{x}")',
            )
        )

    def get_language(self) -> str:
        return "cpp"

    def _get_default_collection_type(self) -> str:
        return "std::vector<int>"

    def _get_collection_type(self, element_type: str) -> str:
        base_type = element_type
        if base_type == "long long":
            base_type = "int"  # type: ignore
        return f"std::vector<{base_type}>"

    def _get_fallback_type(self) -> str:
        return "std::string"

    def _convert_collection(self, collection: Union[list, tuple]) -> str:
        elements = [str(item) for item in collection]
        return f"{{{', '.join(elements)}}}"

    def _convert_fallback(self, value: Any) -> str:
        return f'std::string("{value}")'
