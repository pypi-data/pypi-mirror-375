"""
Utility functions and helper classes for tree-sitter.
"""

import ctypes
from typing import Optional, Callable, Any, List, Dict
from .types import Point, Range, Input, InputEncoding
from .exceptions import TreeSitterException


class Logger:
    """Logger interface for tree-sitter."""
    
    def __init__(self, log_func: Optional[Callable[[str, str], None]] = None):
        """
        Initialize a logger.
        
        Args:
            log_func: Optional custom log function that takes (log_type, message)
        """
        self.log_func = log_func or self._default_log
    
    def _default_log(self, log_type: str, message: str) -> None:
        """Default logging function."""
        print(f"[{log_type}] {message}")
    
    def log(self, log_type: str, message: str) -> None:
        """
        Log a message.
        
        Args:
            log_type: Type of log (e.g., "parse", "lex")
            message: The message to log
        """
        self.log_func(log_type, message)


class Allocator:
    """Custom memory allocator for tree-sitter."""
    
    def __init__(self):
        """Initialize the allocator."""
        self.malloc_func = None
        self.calloc_func = None
        self.realloc_func = None
        self.free_func = None
    
    def set_allocator(self, 
                     malloc: Optional[Callable[[int], Any]] = None,
                     calloc: Optional[Callable[[int, int], Any]] = None,
                     realloc: Optional[Callable[[Any, int], Any]] = None,
                     free: Optional[Callable[[Any], None]] = None) -> None:
        """
        Set the allocation functions.
        
        Args:
            malloc: Memory allocation function
            calloc: Memory allocation and zeroing function
            realloc: Memory reallocation function
            free: Memory deallocation function
        """
        self.malloc_func = malloc
        self.calloc_func = calloc
        self.realloc_func = realloc
        self.free_func = free
        
        # Implementation would call ts_set_allocator with these functions


class TreeSitterConfig:
    """Configuration for tree-sitter library."""
    
    def __init__(self):
        """Initialize the configuration."""
        self.language_version = 14
        self.min_compatible_language_version = 13
        self.allocator = Allocator()
        self.logger = Logger()
    
    def set_allocator(self, allocator: Allocator) -> None:
        """
        Set the memory allocator.
        
        Args:
            allocator: The allocator to use
        """
        self.allocator = allocator
        allocator.set_allocator()
    
    def set_logger(self, logger: Logger) -> None:
        """
        Set the logger.
        
        Args:
            logger: The logger to use
        """
        self.logger = logger


def create_input_from_string(source_code: str, encoding: InputEncoding = InputEncoding.UTF8) -> Input:
    """
    Create an Input object from a string.
    
    Args:
        source_code: The source code string
        encoding: The text encoding
        
    Returns:
        An Input object
    """
    def read_func(byte_index: int, position: Point) -> bytes:
        if byte_index >= len(source_code.encode('utf-8')):
            return b''
        
        # Convert to bytes based on encoding
        if encoding == InputEncoding.UTF8:
            encoded = source_code.encode('utf-8')
        else:  # UTF16
            encoded = source_code.encode('utf-16le')
        
        return encoded[byte_index:]
    
    return Input(read_func, encoding=encoding)


def create_input_from_file(file_path: str, encoding: InputEncoding = InputEncoding.UTF8) -> Input:
    """
    Create an Input object from a file.
    
    Args:
        file_path: Path to the file
        encoding: The text encoding
        
    Returns:
        An Input object
    """
    def read_func(byte_index: int, position: Point) -> bytes:
        try:
            with open(file_path, 'rb') as f:
                f.seek(byte_index)
                return f.read(1024)  # Read in chunks
        except (IOError, OSError):
            return b''
    
    return Input(read_func, encoding=encoding)


def create_input_from_callback(read_callback: Callable[[int, Point], bytes], 
                              encoding: InputEncoding = InputEncoding.UTF8) -> Input:
    """
    Create an Input object from a callback function.
    
    Args:
        read_callback: Function that takes (byte_index, position) and returns bytes
        encoding: The text encoding
        
    Returns:
        An Input object
    """
    return Input(read_callback, encoding=encoding)


def point_to_string(point: Point) -> str:
    """
    Convert a point to a string representation.
    
    Args:
        point: The point to convert
        
    Returns:
        String representation of the point
    """
    return f"({point.row}, {point.column})"


def range_to_string(range_obj: Range) -> str:
    """
    Convert a range to a string representation.
    
    Args:
        range_obj: The range to convert
        
    Returns:
        String representation of the range
    """
    return f"{point_to_string(range_obj.start_point)}-{point_to_string(range_obj.end_point)}"


def create_range(start_point: Point, end_point: Point, start_byte: int, end_byte: int) -> Range:
    """
    Create a range from points and byte positions.
    
    Args:
        start_point: Start point
        end_point: End point
        start_byte: Start byte position
        end_byte: End byte position
        
    Returns:
        A Range object
    """
    return Range(start_point, end_point, start_byte, end_byte)


def create_point(row: int, column: int) -> Point:
    """
    Create a point from row and column.
    
    Args:
        row: Row number (0-based)
        column: Column number (0-based)
        
    Returns:
        A Point object
    """
    return Point(row, column)


class TreeWalker:
    """Utility class for walking syntax trees."""
    
    def __init__(self, root_node):
        """
        Initialize a tree walker.
        
        Args:
            root_node: The root node to start walking from
        """
        self.root_node = root_node
    
    def walk_preorder(self, callback: Callable[[Any], bool]) -> None:
        """
        Walk the tree in pre-order (depth-first).
        
        Args:
            callback: Function called for each node, returns True to continue, False to stop
        """
        def _walk(node):
            if not callback(node):
                return False
            
            for child in node.children():
                if not _walk(child):
                    return False
            
            return True
        
        _walk(self.root_node)
    
    def walk_postorder(self, callback: Callable[[Any], bool]) -> None:
        """
        Walk the tree in post-order (depth-first).
        
        Args:
            callback: Function called for each node, returns True to continue, False to stop
        """
        def _walk(node):
            for child in node.children():
                if not _walk(child):
                    return False
            
            return callback(node)
        
        _walk(self.root_node)
    
    def find_nodes_by_type(self, node_type: str) -> List[Any]:
        """
        Find all nodes of a specific type.
        
        Args:
            node_type: The node type to search for
            
        Returns:
            List of matching nodes
        """
        matches = []
        
        def callback(node):
            if node.type == node_type:
                matches.append(node)
            return True
        
        self.walk_preorder(callback)
        return matches
    
    def find_nodes_by_predicate(self, predicate: Callable[[Any], bool]) -> List[Any]:
        """
        Find all nodes that match a predicate.
        
        Args:
            predicate: Function that takes a node and returns True if it matches
            
        Returns:
            List of matching nodes
        """
        matches = []
        
        def callback(node):
            if predicate(node):
                matches.append(node)
            return True
        
        self.walk_preorder(callback)
        return matches


class QueryBuilder:
    """Utility class for building tree-sitter queries."""
    
    def __init__(self):
        """Initialize a query builder."""
        self.patterns = []
        self.captures = {}
    
    def add_pattern(self, pattern: str) -> 'QueryBuilder':
        """
        Add a pattern to the query.
        
        Args:
            pattern: The pattern string
            
        Returns:
            Self for method chaining
        """
        self.patterns.append(pattern)
        return self
    
    def add_capture(self, name: str, pattern: str) -> 'QueryBuilder':
        """
        Add a capture to the query.
        
        Args:
            name: The capture name
            pattern: The pattern to capture
            
        Returns:
            Self for method chaining
        """
        self.captures[name] = pattern
        return self
    
    def build(self) -> str:
        """
        Build the final query string.
        
        Returns:
            The complete query string
        """
        query_parts = []
        
        # Add patterns
        for pattern in self.patterns:
            query_parts.append(pattern)
        
        # Add captures
        for name, pattern in self.captures.items():
            query_parts.append(f"({pattern}) @{name}")
        
        return "\n".join(query_parts)
