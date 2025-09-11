"""
Validation and conditional logic helpers for tree-sitter.

This module provides comprehensive validation and conditional logic
functionality based on patterns found in the VCL demo.
"""

from typing import Optional, List, Dict, Any, Callable, Union, Tuple
from .tree import Node, Tree, TreeCursor
from .language import Language
from .query import Query, QueryCursor, QueryMatch
from .types import Point, Range, SymbolType, Quantifier, QueryError
from .exceptions import TreeSitterException, TreeSitterParseError, TreeSitterQueryError


class NodeValidator:
    """Validator for tree-sitter nodes."""
    
    @staticmethod
    def validate_node_integrity(node: Node) -> List[str]:
        """
        Validate node integrity and return any issues.
        
        Args:
            node: The node to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Basic null check
        if node.is_null():
            issues.append("Node is null")
            return issues  # No point checking further if null
        
        # Check byte positions
        if node.start_byte > node.end_byte:
            issues.append(f"Invalid byte range: start_byte ({node.start_byte}) > end_byte ({node.end_byte})")
        
        # Check point positions
        start_point = node.start_point
        end_point = node.end_point
        
        if start_point.row > end_point.row:
            issues.append(f"Invalid point range: start_row ({start_point.row}) > end_row ({end_point.row})")
        elif (start_point.row == end_point.row and 
              start_point.column > end_point.column):
            issues.append(f"Invalid point range: start_col ({start_point.column}) > end_col ({end_point.column}) on same row")
        
        # Check for negative positions
        if node.start_byte < 0:
            issues.append(f"Negative start_byte: {node.start_byte}")
        
        if node.end_byte < 0:
            issues.append(f"Negative end_byte: {node.end_byte}")
        
        if start_point.row < 0:
            issues.append(f"Negative start_row: {start_point.row}")
        
        if start_point.column < 0:
            issues.append(f"Negative start_column: {start_point.column}")
        
        if end_point.row < 0:
            issues.append(f"Negative end_row: {end_point.row}")
        
        if end_point.column < 0:
            issues.append(f"Negative end_column: {end_point.column}")
        
        # Check child counts
        child_count = node.child_count()
        named_child_count = node.named_child_count()
        
        if child_count < 0:
            issues.append(f"Negative child_count: {child_count}")
        
        if named_child_count < 0:
            issues.append(f"Negative named_child_count: {named_child_count}")
        
        if named_child_count > child_count:
            issues.append(f"named_child_count ({named_child_count}) > child_count ({child_count})")
        
        # Check descendant count
        descendant_count = node.descendant_count()
        if descendant_count < 1:
            issues.append(f"Invalid descendant_count: {descendant_count} (should be >= 1)")
        
        return issues
    
    @staticmethod
    def validate_node_consistency(node: Node, source_code: str) -> List[str]:
        """
        Validate node consistency with source code.
        
        Args:
            node: The node to validate
            source_code: The source code the node represents
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if node.is_null():
            return issues
        
        # Check if byte positions are within source code bounds
        if node.end_byte > len(source_code.encode('utf-8')):
            issues.append(f"end_byte ({node.end_byte}) exceeds source code length ({len(source_code.encode('utf-8'))})")
        
        # Check if text extraction works
        try:
            node_text = node.text
            if not isinstance(node_text, str):
                issues.append("Node text is not a string")
        except Exception as e:
            issues.append(f"Error extracting node text: {e}")
        
        return issues
    
    @staticmethod
    def validate_node_hierarchy(node: Node) -> List[str]:
        """
        Validate node hierarchy consistency.
        
        Args:
            node: The node to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if node.is_null():
            return issues
        
        # Check parent-child relationships
        parent = node.parent()
        if parent and not parent.is_null():
            # Check if this node is actually a child of its parent
            found_as_child = False
            for i in range(parent.child_count()):
                child = parent.child(i)
                if child and child.equals(node):
                    found_as_child = True
                    break
            
            if not found_as_child:
                issues.append("Node not found as child of its parent")
        
        # Check child-parent relationships
        child_count = node.child_count()
        for i in range(child_count):
            child = node.child(i)
            if child and not child.is_null():
                child_parent = child.parent()
                if not child_parent or not child_parent.equals(node):
                    issues.append(f"Child {i} does not have this node as parent")
        
        return issues


class QueryValidator:
    """Validator for tree-sitter queries."""
    
    @staticmethod
    def validate_query_syntax(query_string: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Validate query syntax.
        
        Args:
            query_string: The query string to validate
            
        Returns:
            Tuple of (is_valid, error_message, error_offset)
        """
        if not query_string or not query_string.strip():
            return False, "Query string is empty", 0
        
        # Basic syntax checks
        if query_string.count('(') != query_string.count(')'):
            return False, "Mismatched parentheses", 0
        
        if query_string.count('[') != query_string.count(']'):
            return False, "Mismatched square brackets", 0
        
        # Check for basic patterns
        if '@' in query_string and not any(c.isalnum() for c in query_string.split('@')[1:]):
            return False, "Invalid capture name after @", query_string.find('@')
        
        return True, None, None
    
    @staticmethod
    def validate_query_against_language(query: Query, language: Language) -> List[str]:
        """
        Validate query against a language.
        
        Args:
            query: The query to validate
            language: The language to validate against
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check if query has patterns
        if query.pattern_count == 0:
            issues.append("Query has no patterns")
        
        # Validate each pattern
        for i in range(query.pattern_count):
            pattern_issues = QueryValidator._validate_pattern(query, language, i)
            issues.extend([f"Pattern {i}: {issue}" for issue in pattern_issues])
        
        # Check captures
        for i in range(query.capture_count):
            capture_name = query.capture_name_for_id(i)
            if not capture_name:
                issues.append(f"Capture {i} has no name")
        
        return issues
    
    @staticmethod
    def _validate_pattern(query: Query, language: Language, pattern_index: int) -> List[str]:
        """Validate a specific pattern."""
        issues = []
        
        # Check predicates
        predicates = query.predicates_for_pattern(pattern_index)
        if not predicates:
            issues.append("No predicates")
        
        # Validate predicate steps
        for i, step in enumerate(predicates):
            if step.type == 1:  # Capture
                capture_name = query.capture_name_for_id(step.value_id)
                if not capture_name:
                    issues.append(f"Predicate step {i}: Invalid capture ID {step.value_id}")
            elif step.type == 2:  # String
                string_value = query.string_value_for_id(step.value_id)
                if not string_value:
                    issues.append(f"Predicate step {i}: Invalid string ID {step.value_id}")
        
        return issues


class LanguageValidator:
    """Validator for tree-sitter languages."""
    
    @staticmethod
    def validate_language(language: Language) -> List[str]:
        """
        Validate a language.
        
        Args:
            language: The language to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check version
        if language.version == 0:
            issues.append("Language version is 0")
        
        # Check field count
        if language.field_count == 0:
            issues.append("Language has no fields")
        
        # Check symbol count
        if language.symbol_count == 0:
            issues.append("Language has no symbols")
        
        # Validate fields
        for i in range(1, language.field_count + 1):
            field_name = language.field_name_for_id(i)
            if not field_name:
                issues.append(f"Field {i} has no name")
            
            # Check if field ID lookup works
            field_id = language.field_id_for_name(field_name)
            if field_id != i:
                issues.append(f"Field '{field_name}' ID mismatch: expected {i}, got {field_id}")
        
        # Validate symbols
        for i in range(1, language.symbol_count + 1):
            symbol_name = language.symbol_name(i)
            if not symbol_name:
                issues.append(f"Symbol {i} has no name")
            
            # Check symbol type
            symbol_type = language.symbol_type(i)
            if not isinstance(symbol_type, SymbolType):
                issues.append(f"Symbol {i} has invalid type: {symbol_type}")
        
        return issues


class ConditionalLogic:
    """Helper class for conditional logic operations."""
    
    @staticmethod
    def should_expand_node(node: Node, named_only: bool = False) -> bool:
        """
        Determine if a node should be expanded in a tree view.
        
        Args:
            node: The node to check
            named_only: Whether to only consider named children
            
        Returns:
            True if the node should be expanded, False otherwise
        """
        if node.is_null():
            return False
        
        if named_only:
            return node.named_child_count() > 0
        else:
            return node.child_count() > 0
    
    @staticmethod
    def should_show_node(node: Node, named_only: bool = False, 
                        show_extra: bool = True, show_missing: bool = True) -> bool:
        """
        Determine if a node should be shown in a tree view.
        
        Args:
            node: The node to check
            named_only: Whether to only show named nodes
            show_extra: Whether to show extra nodes
            show_missing: Whether to show missing nodes
            
        Returns:
            True if the node should be shown, False otherwise
        """
        if node.is_null():
            return False
        
        if named_only and not node.is_named():
            return False
        
        if not show_extra and node.is_extra():
            return False
        
        if not show_missing and node.is_missing():
            return False
        
        return True
    
    @staticmethod
    def get_node_display_text(node: Node, show_field_info: bool = False) -> str:
        """
        Get display text for a node.
        
        Args:
            node: The node to get display text for
            show_field_info: Whether to show field information
            
        Returns:
            Display text for the node
        """
        if node.is_null():
            return "[NULL]"
        
        if node.is_error():
            return f"[ERROR: {node.type}]"
        
        if node.is_missing():
            return f"[MISSING: {node.type}]"
        
        if node.is_extra():
            return f"[EXTRA: {node.type}]"
        
        text = node.type
        
        if show_field_info:
            # This would need to be implemented with actual field data
            # For now, just return the node type
            pass
        
        return text
    
    @staticmethod
    def can_navigate_to_child(node: Node, named_only: bool = False) -> bool:
        """
        Check if we can navigate to a child node.
        
        Args:
            node: The node to check
            named_only: Whether to only consider named children
            
        Returns:
            True if we can navigate to a child, False otherwise
        """
        if node.is_null():
            return False
        
        if named_only:
            return node.named_child_count() > 0
        else:
            return node.child_count() > 0
    
    @staticmethod
    def can_navigate_to_sibling(node: Node, direction: str = "next", named_only: bool = False) -> bool:
        """
        Check if we can navigate to a sibling node.
        
        Args:
            node: The node to check
            direction: Direction to check ("next" or "prev")
            named_only: Whether to only consider named siblings
            
        Returns:
            True if we can navigate to a sibling, False otherwise
        """
        if node.is_null():
            return False
        
        if direction == "next":
            if named_only:
                sibling = node.next_named_sibling()
            else:
                sibling = node.next_sibling()
        elif direction == "prev":
            if named_only:
                sibling = node.prev_named_sibling()
            else:
                sibling = node.prev_sibling()
        else:
            return False
        
        return sibling is not None and not sibling.is_null()
    
    @staticmethod
    def can_navigate_to_parent(node: Node) -> bool:
        """
        Check if we can navigate to the parent node.
        
        Args:
            node: The node to check
            
        Returns:
            True if we can navigate to the parent, False otherwise
        """
        if node.is_null():
            return False
        
        parent = node.parent()
        return parent is not None and not parent.is_null()
    
    @staticmethod
    def filter_nodes_by_condition(nodes: List[Node], condition: Callable[[Node], bool]) -> List[Node]:
        """
        Filter nodes by a condition.
        
        Args:
            nodes: List of nodes to filter
            condition: Function that takes a node and returns True to include it
            
        Returns:
            Filtered list of nodes
        """
        return [node for node in nodes if condition(node)]
    
    @staticmethod
    def group_nodes_by_type(nodes: List[Node]) -> Dict[str, List[Node]]:
        """
        Group nodes by their type.
        
        Args:
            nodes: List of nodes to group
            
        Returns:
            Dictionary mapping node types to lists of nodes
        """
        groups = {}
        for node in nodes:
            if not node.is_null():
                node_type = node.type
                if node_type not in groups:
                    groups[node_type] = []
                groups[node_type].append(node)
        return groups
    
    @staticmethod
    def find_nodes_by_predicate(nodes: List[Node], predicate: Callable[[Node], bool]) -> List[Node]:
        """
        Find nodes that match a predicate.
        
        Args:
            nodes: List of nodes to search
            predicate: Function that takes a node and returns True if it matches
            
        Returns:
            List of matching nodes
        """
        return [node for node in nodes if predicate(node)]
    
    @staticmethod
    def count_nodes_by_type(nodes: List[Node]) -> Dict[str, int]:
        """
        Count nodes by their type.
        
        Args:
            nodes: List of nodes to count
            
        Returns:
            Dictionary mapping node types to counts
        """
        counts = {}
        for node in nodes:
            if not node.is_null():
                node_type = node.type
                counts[node_type] = counts.get(node_type, 0) + 1
        return counts
