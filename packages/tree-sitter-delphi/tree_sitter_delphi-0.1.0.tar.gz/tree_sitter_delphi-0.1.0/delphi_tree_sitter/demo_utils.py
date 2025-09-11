"""
Demo-specific utilities and helpers.

This module provides utilities that are specifically useful for creating
demo applications and GUI interfaces for tree-sitter, based on patterns
found in the VCL demo.
"""

from typing import Optional, List, Dict, Any, Callable, Tuple
from .tree import Node, Tree, TreeCursor
from .language import Language
from .query import Query, QueryCursor, QueryMatch
from .types import Point, Range
from .helpers import NodePropertyHelper, LanguageInfoHelper, QueryHelper, QueryMatchHelper


class TreeViewHelper:
    """Helper class for creating tree view representations of syntax trees."""
    
    def __init__(self, root_node: Node, named_only: bool = False):
        """
        Initialize with a root node.
        
        Args:
            root_node: The root node to create tree view for
            named_only: Whether to only show named nodes
        """
        self.root_node = root_node
        self.named_only = named_only
        self.tree_items = []
    
    def create_tree_item(self, node: Node, parent_index: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a tree item representation of a node.
        
        Args:
            node: The node to create item for
            parent_index: Index of parent item, or None for root
            
        Returns:
            Dictionary representing the tree item
        """
        item = {
            'node': node,
            'parent_index': parent_index,
            'text': self._get_node_display_text(node),
            'has_children': self._has_children(node),
            'children': [],
        }
        
        index = len(self.tree_items)
        self.tree_items.append(item)
        
        if parent_index is not None:
            self.tree_items[parent_index]['children'].append(index)
        
        return item
    
    def _get_node_display_text(self, node: Node) -> str:
        """Get display text for a node."""
        if self.named_only and not node.is_named():
            return f"[{node.type}]"
        
        # Check if node has field information
        # This would need to be implemented with actual field data
        return node.type
    
    def _has_children(self, node: Node) -> bool:
        """Check if node has children."""
        if self.named_only:
            return node.named_child_count() > 0
        else:
            return node.child_count() > 0
    
    def build_tree(self) -> List[Dict[str, Any]]:
        """Build the complete tree structure."""
        self.tree_items = []
        self._build_node(self.root_node, None)
        return self.tree_items
    
    def _build_node(self, node: Node, parent_index: Optional[int]):
        """Recursively build tree items for a node and its children."""
        item_index = len(self.tree_items)
        self.create_tree_item(node, parent_index)
        
        # Add children
        if self.named_only:
            children = [node.named_child(i) for i in range(node.named_child_count())]
        else:
            children = [node.child(i) for i in range(node.child_count())]
        
        for child in children:
            if child and not child.is_null():
                self._build_node(child, item_index)


class CodeSelectionHelper:
    """Helper class for managing code selection based on node positions."""
    
    def __init__(self, source_code: str):
        """
        Initialize with source code.
        
        Args:
            source_code: The source code to work with
        """
        self.source_code = source_code
        self.lines = source_code.split('\n')
    
    def get_selection_range(self, node: Node) -> Tuple[int, int]:
        """
        Get selection range for a node.
        
        Args:
            node: The node to get selection for
            
        Returns:
            Tuple of (start_pos, end_pos) in characters
        """
        start_point = node.start_point
        end_point = node.end_point
        
        # Calculate start position
        start_pos = self._point_to_char_position(start_point)
        
        # Calculate end position
        end_pos = self._point_to_char_position(end_point)
        
        return start_pos, end_pos
    
    def _point_to_char_position(self, point: Point) -> int:
        """Convert a point to character position."""
        char_pos = 0
        
        # Add characters from previous lines
        for i in range(point.row):
            if i < len(self.lines):
                char_pos += len(self.lines[i]) + 1  # +1 for newline
        
        # Add characters from current line
        if point.row < len(self.lines):
            char_pos += min(point.column, len(self.lines[point.row]))
        
        return char_pos
    
    def get_line_range(self, node: Node) -> Tuple[int, int]:
        """
        Get line range for a node.
        
        Args:
            node: The node to get line range for
            
        Returns:
            Tuple of (start_line, end_line) (0-based)
        """
        return node.start_point.row, node.end_point.row
    
    def get_text_for_node(self, node: Node) -> str:
        """Get the text content for a node."""
        start_pos, end_pos = self.get_selection_range(node)
        return self.source_code[start_pos:end_pos]


class LanguageLoaderHelper:
    """Helper class for loading languages from shared libraries."""
    
    def __init__(self):
        """Initialize the language loader."""
        self.loaded_languages = {}
    
    def load_language(self, language_name: str, library_path: Optional[str] = None) -> Language:
        """
        Load a language from a shared library.
        
        Args:
            language_name: Name of the language (e.g., 'python', 'javascript')
            library_path: Optional path to the library file
            
        Returns:
            The loaded language
            
        Raises:
            TreeSitterException: If loading fails
        """
        if language_name in self.loaded_languages:
            return self.loaded_languages[language_name]
        
        # Generate library path if not provided
        if library_path is None:
            library_path = f"tree-sitter-{language_name}"
        
        # Generate API function name
        api_name = f"tree_sitter_{language_name}"
        
        try:
            language = Language.from_library(library_path, api_name)
            self.loaded_languages[language_name] = language
            return language
        except Exception as e:
            raise TreeSitterException(f"Failed to load language '{language_name}': {e}")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available language names."""
        return list(self.loaded_languages.keys())
    
    def is_language_loaded(self, language_name: str) -> bool:
        """Check if a language is loaded."""
        return language_name in self.loaded_languages


class QueryFormHelper:
    """Helper class for managing query forms and operations."""
    
    def __init__(self, tree: Tree):
        """
        Initialize with a tree.
        
        Args:
            tree: The tree to query against
        """
        self.tree = tree
        self.current_query = None
        self.current_cursor = None
        self.current_match = None
    
    def create_query(self, query_string: str) -> Tuple[bool, str, Optional[Query]]:
        """
        Create a query from a string.
        
        Args:
            query_string: The query string
            
        Returns:
            Tuple of (success, message, query)
        """
        try:
            language = self.tree.language()
            query = Query(language, query_string)
            self.current_query = query
            return True, "Query created successfully", query
        except Exception as e:
            return False, f"Query error: {e}", None
    
    def execute_query(self) -> bool:
        """
        Execute the current query.
        
        Returns:
            True if successful, False otherwise
        """
        if self.current_query is None:
            return False
        
        try:
            self.current_cursor = QueryCursor()
            self.current_cursor.execute(self.current_query, self.tree.root_node)
            return True
        except Exception as e:
            return False
    
    def get_next_match(self) -> Optional[QueryMatch]:
        """
        Get the next match from the query.
        
        Returns:
            The next match, or None if no more matches
        """
        if self.current_cursor is None:
            return None
        
        match = self.current_cursor.next_match()
        if match:
            self.current_match = match
        return match
    
    def get_match_info(self, match: QueryMatch) -> Dict[str, Any]:
        """
        Get information about a match.
        
        Args:
            match: The match to get info for
            
        Returns:
            Dictionary with match information
        """
        helper = QueryMatchHelper(match)
        return {
            'match_info': helper.match_info_str,
            'captures': helper.get_captures_info(),
        }
    
    def clear_query(self):
        """Clear the current query and cursor."""
        self.current_query = None
        self.current_cursor = None
        self.current_match = None


class PropertyGridHelper:
    """Helper class for managing property grids."""
    
    def __init__(self):
        """Initialize the property grid helper."""
        self.properties = {}
    
    def set_node_properties(self, node: Node):
        """
        Set properties for a node.
        
        Args:
            node: The node to set properties for
        """
        helper = NodePropertyHelper(node)
        self.properties = helper.get_property_dict()
    
    def get_property_value(self, property_name: str) -> str:
        """
        Get a property value.
        
        Args:
            property_name: Name of the property
            
        Returns:
            The property value, or empty string if not found
        """
        return self.properties.get(property_name, "")
    
    def get_all_properties(self) -> Dict[str, str]:
        """Get all properties."""
        return self.properties.copy()
    
    def clear_properties(self):
        """Clear all properties."""
        self.properties = {}


class ErrorHandler:
    """Helper class for handling errors and exceptions."""
    
    @staticmethod
    def handle_parse_error(error: Exception) -> str:
        """
        Handle parse errors.
        
        Args:
            error: The parse error
            
        Returns:
            Formatted error message
        """
        return f"Parse error: {str(error)}"
    
    @staticmethod
    def handle_query_error(error: Exception) -> str:
        """
        Handle query errors.
        
        Args:
            error: The query error
            
        Returns:
            Formatted error message
        """
        return f"Query error: {str(error)}"
    
    @staticmethod
    def handle_language_error(error: Exception) -> str:
        """
        Handle language errors.
        
        Args:
            error: The language error
            
        Returns:
            Formatted error message
        """
        return f"Language error: {str(error)}"
    
    @staticmethod
    def format_error_message(error_type: str, message: str, details: Optional[str] = None) -> str:
        """
        Format an error message.
        
        Args:
            error_type: Type of error
            message: Error message
            details: Optional additional details
            
        Returns:
            Formatted error message
        """
        formatted = f"[{error_type}] {message}"
        if details:
            formatted += f"\nDetails: {details}"
        return formatted


class DemoStateManager:
    """Helper class for managing demo application state."""
    
    def __init__(self):
        """Initialize the state manager."""
        self.current_tree = None
        self.current_language = None
        self.current_parser = None
        self.current_query = None
        self.edit_changed = False
        self.named_nodes_only = False
    
    def set_tree(self, tree: Tree):
        """Set the current tree."""
        self.current_tree = tree
    
    def get_tree(self) -> Optional[Tree]:
        """Get the current tree."""
        return self.current_tree
    
    def set_language(self, language: Language):
        """Set the current language."""
        self.current_language = language
    
    def get_language(self) -> Optional[Language]:
        """Get the current language."""
        return self.current_language
    
    def set_parser(self, parser):
        """Set the current parser."""
        self.current_parser = parser
    
    def get_parser(self):
        """Get the current parser."""
        return self.current_parser
    
    def set_query(self, query: Query):
        """Set the current query."""
        self.current_query = query
    
    def get_query(self) -> Optional[Query]:
        """Get the current query."""
        return self.current_query
    
    def set_edit_changed(self, changed: bool):
        """Set the edit changed flag."""
        self.edit_changed = changed
    
    def is_edit_changed(self) -> bool:
        """Check if edit has changed."""
        return self.edit_changed
    
    def set_named_nodes_only(self, named_only: bool):
        """Set the named nodes only flag."""
        self.named_nodes_only = named_only
    
    def is_named_nodes_only(self) -> bool:
        """Check if named nodes only is enabled."""
        return self.named_nodes_only
    
    def reset(self):
        """Reset all state."""
        self.current_tree = None
        self.current_language = None
        self.current_parser = None
        self.current_query = None
        self.edit_changed = False
        self.named_nodes_only = False
