"""
Tree Sitter Parser implementation for Python.
"""

import ctypes
import os
from typing import Optional, Callable, Any, List
from .language import Language
from .tree import Tree
from .types import Input, InputEncoding, Range
from .exceptions import TreeSitterException, TreeSitterParseError


class Parser:
    """
    A Tree Sitter parser that can parse source code into syntax trees.
    """
    
    def __init__(self):
        """Initialize a new parser."""
        self._parser = None
        self._language = None
        self._timeout_micros = 0
        self._cancellation_flag = None
        self._logger = None
        self._included_ranges: List[Range] = []
        self._load_library()
    
    def _load_library(self):
        """Load the tree-sitter library."""
        # Try to load tree-sitter library from common locations
        library_paths = [
            "tree-sitter.dll",  # Windows
            "libtree-sitter.so",  # Linux
            "libtree-sitter.dylib",  # macOS
        ]
        
        for path in library_paths:
            try:
                self._lib = ctypes.CDLL(path)
                break
            except OSError:
                continue
        else:
            raise TreeSitterException("Could not load tree-sitter library")
    
    def set_language(self, language: Language) -> None:
        """
        Set the language that the parser should use for parsing.
        
        Args:
            language: The language to use for parsing
            
        Raises:
            TreeSitterException: If language version is incompatible
        """
        self._language = language
        # Implementation would depend on the actual tree-sitter C API
        # In real implementation: ts_parser_set_language(self._parser, language._language_ptr)
    
    def get_language(self) -> Optional[Language]:
        """
        Get the parser's current language.
        
        Returns:
            The current language, or None if no language is set
        """
        return self._language
    
    def parse_string(self, source_code: str, old_tree: Optional[Tree] = None) -> Tree:
        """
        Parse source code from a string.
        
        Args:
            source_code: The source code to parse
            old_tree: Optional previous tree for incremental parsing
            
        Returns:
            A new syntax tree
            
        Raises:
            TreeSitterParseError: If parsing fails
        """
        if self._language is None:
            raise TreeSitterParseError("No language set. Call set_language() first.")
        
        if not source_code:
            raise TreeSitterParseError("Cannot parse empty string")
        
        # This is a placeholder implementation
        # The actual implementation would use ts_parser_parse_string_encoding
        return Tree(source_code, self._language)
    
    def parse_string_encoding(self, 
                            source_code: str, 
                            encoding: InputEncoding = InputEncoding.UTF8,
                            old_tree: Optional[Tree] = None) -> Tree:
        """
        Parse source code from a string with specified encoding.
        
        Args:
            source_code: The source code to parse
            encoding: Text encoding (UTF8 or UTF16)
            old_tree: Optional previous tree for incremental parsing
            
        Returns:
            A new syntax tree
        """
        if self._language is None:
            raise TreeSitterParseError("No language set. Call set_language() first.")
        
        # This is a placeholder implementation
        return Tree(source_code, self._language)
    
    def parse(self, input_config: Input, old_tree: Optional[Tree] = None) -> Tree:
        """
        Parse source code using an input configuration.
        
        Args:
            input_config: Input configuration with read function
            old_tree: Optional previous tree for incremental parsing
            
        Returns:
            A new syntax tree
        """
        if self._language is None:
            raise TreeSitterParseError("No language set. Call set_language() first.")
        
        # This is a placeholder implementation
        # The actual implementation would use ts_parser_parse
        return Tree("", self._language)
    
    def reset(self) -> None:
        """
        Reset the parser to start the next parse from the beginning.
        
        This is useful when you want to parse a different document
        or when a previous parse was cancelled.
        """
        # Implementation would call ts_parser_reset(self._parser)
        pass
    
    def set_timeout_micros(self, timeout_micros: int) -> None:
        """
        Set the maximum duration in microseconds that parsing should be allowed to take.
        
        Args:
            timeout_micros: Maximum parsing time in microseconds
        """
        self._timeout_micros = timeout_micros
        # Implementation would call ts_parser_set_timeout_micros(self._parser, timeout_micros)
    
    def get_timeout_micros(self) -> int:
        """
        Get the current timeout setting.
        
        Returns:
            Current timeout in microseconds
        """
        return self._timeout_micros
    
    def set_cancellation_flag(self, flag: Optional[ctypes.c_size_t]) -> None:
        """
        Set the parser's cancellation flag pointer.
        
        Args:
            flag: Pointer to cancellation flag, or None to disable
        """
        self._cancellation_flag = flag
        # Implementation would call ts_parser_set_cancellation_flag(self._parser, flag)
    
    def get_cancellation_flag(self) -> Optional[ctypes.c_size_t]:
        """
        Get the parser's current cancellation flag pointer.
        
        Returns:
            Current cancellation flag pointer, or None if not set
        """
        return self._cancellation_flag
    
    def set_logger(self, logger) -> None:
        """
        Set the logger that the parser should use during parsing.
        
        Args:
            logger: Logger object with log method
        """
        self._logger = logger
        # Implementation would call ts_parser_set_logger(self._parser, logger)
    
    def get_logger(self):
        """
        Get the parser's current logger.
        
        Returns:
            Current logger, or None if not set
        """
        return self._logger
    
    def set_included_ranges(self, ranges: List[Range]) -> None:
        """
        Set the ranges of text that the parser should include when parsing.
        
        Args:
            ranges: List of ranges to include, or empty list for entire document
            
        Raises:
            TreeSitterException: If ranges are invalid (overlapping or not ordered)
        """
        # Validate ranges
        if ranges:
            for i in range(len(ranges) - 1):
                if ranges[i].end_byte > ranges[i + 1].start_byte:
                    raise TreeSitterException("Ranges must be ordered and non-overlapping")
        
        self._included_ranges = ranges
        # Implementation would call ts_parser_set_included_ranges(self._parser, ranges, len(ranges))
    
    def get_included_ranges(self) -> List[Range]:
        """
        Get the ranges of text that the parser will include when parsing.
        
        Returns:
            List of included ranges
        """
        return self._included_ranges.copy()
    
    def print_dot_graphs(self, file_descriptor: int) -> None:
        """
        Set the file descriptor to which the parser should write debugging graphs.
        
        Args:
            file_descriptor: File descriptor for DOT graph output, or negative to disable
        """
        # Implementation would call ts_parser_print_dot_graphs(self._parser, file_descriptor)
        pass
    
    def __del__(self):
        """Clean up parser resources."""
        if self._parser is not None:
            # Implementation would call ts_parser_delete(self._parser)
            pass
