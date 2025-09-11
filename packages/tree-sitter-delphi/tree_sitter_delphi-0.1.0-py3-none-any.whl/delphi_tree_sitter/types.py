"""
Type definitions and enums for tree-sitter.
"""

from enum import IntEnum
from typing import NamedTuple, Callable, Optional, Any
from ctypes import c_void_p


class InputEncoding(IntEnum):
    """Input encoding types."""
    UTF8 = 0
    UTF16 = 1


class SymbolType(IntEnum):
    """Symbol types."""
    REGULAR = 0
    ANONYMOUS = 1
    AUXILIARY = 2


class Quantifier(IntEnum):
    """Query quantifiers."""
    ZERO = 0
    ZERO_OR_ONE = 1
    ZERO_OR_MORE = 2
    ONE = 3
    ONE_OR_MORE = 4


class QueryError(IntEnum):
    """Query error types."""
    NONE = 0
    SYNTAX = 1
    NODE_TYPE = 2
    FIELD = 3
    CAPTURE = 4
    STRUCTURE = 5
    LANGUAGE = 6


class Point(NamedTuple):
    """A point in source code (row, column)."""
    row: int
    column: int
    
    def __str__(self) -> str:
        return f"({self.row}, {self.column})"


class Range(NamedTuple):
    """A range in source code."""
    start_point: Point
    end_point: Point
    start_byte: int
    end_byte: int


class Input:
    """Input configuration for parsing."""
    
    def __init__(self, 
                 read_func: Callable[[int, Point], bytes],
                 payload: Optional[Any] = None,
                 encoding: InputEncoding = InputEncoding.UTF8):
        """
        Initialize input configuration.
        
        Args:
            read_func: Function that takes (byte_index, position) and returns bytes
            payload: Optional payload to pass to read function
            encoding: Text encoding
        """
        self.read_func = read_func
        self.payload = payload
        self.encoding = encoding


class QueryCapture:
    """A captured node in a query match."""
    
    def __init__(self, node: 'Node', index: int):
        """
        Initialize a query capture.
        
        Args:
            node: The captured node
            index: The capture index
        """
        self.node = node
        self.index = index


class QueryMatch:
    """A match from a tree-sitter query."""
    
    def __init__(self, 
                 pattern_index: int, 
                 captures: list[QueryCapture],
                 match_id: int = 0):
        """
        Initialize a query match.
        
        Args:
            pattern_index: The pattern index that matched
            captures: List of captured nodes
            match_id: Unique match identifier
        """
        self.pattern_index = pattern_index
        self.captures = captures
        self.match_id = match_id
    
    def get_capture_by_name(self, name: str) -> Optional[QueryCapture]:
        """Get a capture by name."""
        # This would need to be implemented with actual query data
        return None
    
    def get_capture_by_index(self, index: int) -> Optional[QueryCapture]:
        """Get a capture by index."""
        if 0 <= index < len(self.captures):
            return self.captures[index]
        return None


# Type aliases for compatibility
TSPoint = Point
TSRange = Range
TSInput = Input
TSInputEncoding = InputEncoding
TSSymbolType = SymbolType
TSQuantifier = Quantifier
TSQueryError = QueryError
TSQueryCapture = QueryCapture
TSQueryMatch = QueryMatch
