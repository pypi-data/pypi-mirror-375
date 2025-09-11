"""
Helper classes and utilities for tree-sitter operations.

This module provides additional helper classes and utilities that are commonly
used in tree-sitter applications, based on patterns found in the VCL demo.
"""

from typing import Optional, List, Dict, Any, Callable, Union, Tuple
from .tree import Node, Tree, TreeCursor
from .language import Language
from .query import Query, QueryCursor, QueryMatch, QueryCapture
from .types import Point, Range, SymbolType, Quantifier, QueryError
from .exceptions import TreeSitterException


class NodePropertyHelper:
    """Helper class for accessing node properties in a structured way."""
    
    def __init__(self, node: Node):
        """
        Initialize with a node.
        
        Args:
            node: The node to provide properties for
        """
        self.node = node
    
    @property
    def symbol_info(self) -> str:
        """Get formatted symbol information."""
        if self.node._language:
            symbol_name = self.node._language.symbol_name(self.node.symbol)
            return f"{self.node.symbol} ({symbol_name})"
        return str(self.node.symbol)
    
    @property
    def grammar_symbol_info(self) -> str:
        """Get formatted grammar symbol information."""
        if self.node._language:
            symbol_name = self.node._language.symbol_name(self.node.grammar_symbol)
            return f"{self.node.grammar_symbol} ({symbol_name})"
        return str(self.node.grammar_symbol)
    
    @property
    def start_point_str(self) -> str:
        """Get start point as string."""
        return str(self.node.start_point)
    
    @property
    def end_point_str(self) -> str:
        """Get end point as string."""
        return str(self.node.end_point)
    
    @property
    def is_error_str(self) -> str:
        """Get error status as string."""
        return str(self.node.is_error())
    
    @property
    def has_error_str(self) -> str:
        """Get has error status as string."""
        return str(self.node.has_error())
    
    @property
    def is_extra_str(self) -> str:
        """Get extra status as string."""
        return str(self.node.is_extra())
    
    @property
    def is_missing_str(self) -> str:
        """Get missing status as string."""
        return str(self.node.is_missing())
    
    @property
    def is_named_str(self) -> str:
        """Get named status as string."""
        return str(self.node.is_named())
    
    def get_property_dict(self) -> Dict[str, str]:
        """Get all properties as a dictionary."""
        return {
            'Symbol': self.symbol_info,
            'GrammarType': self.node.grammar_type,
            'GrammarSymbol': self.grammar_symbol_info,
            'IsError': self.is_error_str,
            'HasError': self.has_error_str,
            'IsExtra': self.is_extra_str,
            'IsMissing': self.is_missing_str,
            'IsNamed': self.is_named_str,
            'ChildCount': str(self.node.child_count()),
            'NamedChildCount': str(self.node.named_child_count()),
            'StartByte': str(self.node.start_byte),
            'StartPoint': self.start_point_str,
            'EndByte': str(self.node.end_byte),
            'EndPoint': self.end_point_str,
            'DescendantCount': str(self.node.descendant_count()),
        }


class LanguageInfoHelper:
    """Helper class for accessing language information."""
    
    def __init__(self, language: Language):
        """
        Initialize with a language.
        
        Args:
            language: The language to provide information for
        """
        self.language = language
    
    @property
    def field_count_str(self) -> str:
        """Get field count as string."""
        return f"Fields: {self.language.field_count}"
    
    @property
    def symbol_count_str(self) -> str:
        """Get symbol count as string."""
        return f"Symbols: {self.language.symbol_count}"
    
    @property
    def version_str(self) -> str:
        """Get version as string."""
        return f"Version: {self.language.version}"
    
    def get_fields_info(self) -> List[Dict[str, Any]]:
        """Get information about all fields."""
        fields = []
        for i in range(1, self.language.field_count + 1):
            field_name = self.language.field_name_for_id(i)
            fields.append({
                'id': i,
                'name': field_name or f"Field_{i}",
            })
        return fields
    
    def get_symbols_info(self) -> List[Dict[str, Any]]:
        """Get information about all symbols."""
        symbols = []
        for i in range(1, self.language.symbol_count + 1):
            symbol_name = self.language.symbol_name(i)
            symbol_type = self.language.symbol_type(i)
            symbols.append({
                'id': i,
                'name': symbol_name or f"Symbol_{i}",
                'type': symbol_type.name if hasattr(symbol_type, 'name') else str(symbol_type),
            })
        return symbols


class QueryHelper:
    """Helper class for query operations."""
    
    def __init__(self, query: Query):
        """
        Initialize with a query.
        
        Args:
            query: The query to provide helpers for
        """
        self.query = query
    
    @property
    def pattern_count_str(self) -> str:
        """Get pattern count as string."""
        return str(self.query.pattern_count)
    
    @property
    def capture_count_str(self) -> str:
        """Get capture count as string."""
        return str(self.query.capture_count)
    
    @property
    def string_count_str(self) -> str:
        """Get string count as string."""
        return str(self.query.string_count)
    
    @property
    def summary_str(self) -> str:
        """Get query summary as string."""
        return f"Patterns: {self.query.pattern_count}, Captures: {self.query.capture_count}, Strings: {self.query.string_count}"
    
    def get_predicates_for_pattern(self, pattern_index: int) -> List[Dict[str, Any]]:
        """Get predicate information for a pattern."""
        predicates = []
        steps = self.query.predicates_for_pattern(pattern_index)
        
        for i, step in enumerate(steps):
            predicate_info = {
                'index': i,
                'type': self._get_step_type_str(step.type),
                'value_id': step.value_id,
                'name': 'N/A',
                'quantifier': 'N/A',
            }
            
            if step.type == 1:  # TSQueryPredicateStepTypeCapture
                predicate_info['name'] = self.query.capture_name_for_id(step.value_id) or f"Capture_{step.value_id}"
                predicate_info['quantifier'] = self._get_quantifier_str(
                    self.query.quantifier_for_capture(pattern_index, step.value_id)
                )
            elif step.type == 2:  # TSQueryPredicateStepTypeString
                predicate_info['name'] = self.query.string_value_for_id(step.value_id) or f"String_{step.value_id}"
            
            predicates.append(predicate_info)
        
        return predicates
    
    def _get_step_type_str(self, step_type: int) -> str:
        """Get step type as string."""
        step_types = ['Done', 'Capture', 'String']
        return step_types[step_type] if 0 <= step_type < len(step_types) else f"Unknown_{step_type}"
    
    def _get_quantifier_str(self, quantifier: Quantifier) -> str:
        """Get quantifier as string."""
        quantifier_names = ['Zero', 'ZeroOrOne', 'ZeroOrMore', 'One', 'OneOrMore']
        return quantifier_names[quantifier] if 0 <= quantifier < len(quantifier_names) else str(quantifier)


class QueryMatchHelper:
    """Helper class for query match operations."""
    
    def __init__(self, match: QueryMatch):
        """
        Initialize with a query match.
        
        Args:
            match: The query match to provide helpers for
        """
        self.match = match
    
    @property
    def match_info_str(self) -> str:
        """Get match information as string."""
        return f"Match id = {self.match.match_id}, pattern idx = {self.match.pattern_index}"
    
    def get_captures_info(self) -> List[Dict[str, Any]]:
        """Get information about all captures in the match."""
        captures = []
        for i, capture in enumerate(self.match.captures):
            captures.append({
                'index': capture.index,
                'node_type': capture.node.type,
                'node': capture.node,
            })
        return captures


class TreeNavigationHelper:
    """Helper class for tree navigation operations."""
    
    def __init__(self, root_node: Node):
        """
        Initialize with a root node.
        
        Args:
            root_node: The root node to navigate from
        """
        self.root_node = root_node
        self.current_node = root_node
    
    def goto_first_child(self, named_only: bool = False) -> bool:
        """
        Move to the first child.
        
        Args:
            named_only: Whether to only consider named children
            
        Returns:
            True if successful, False otherwise
        """
        if named_only:
            if self.current_node.named_child_count() > 0:
                self.current_node = self.current_node.named_child(0)
                return True
        else:
            if self.current_node.child_count() > 0:
                self.current_node = self.current_node.child(0)
                return True
        return False
    
    def goto_next_sibling(self, named_only: bool = False) -> bool:
        """
        Move to the next sibling.
        
        Args:
            named_only: Whether to only consider named siblings
            
        Returns:
            True if successful, False otherwise
        """
        if named_only:
            next_sibling = self.current_node.next_named_sibling()
        else:
            next_sibling = self.current_node.next_sibling()
        
        if next_sibling and not next_sibling.is_null():
            self.current_node = next_sibling
            return True
        return False
    
    def goto_prev_sibling(self, named_only: bool = False) -> bool:
        """
        Move to the previous sibling.
        
        Args:
            named_only: Whether to only consider named siblings
            
        Returns:
            True if successful, False otherwise
        """
        if named_only:
            prev_sibling = self.current_node.prev_named_sibling()
        else:
            prev_sibling = self.current_node.prev_sibling()
        
        if prev_sibling and not prev_sibling.is_null():
            self.current_node = prev_sibling
            return True
        return False
    
    def goto_parent(self) -> bool:
        """
        Move to the parent node.
        
        Returns:
            True if successful, False otherwise
        """
        parent = self.current_node.parent()
        if parent and not parent.is_null():
            self.current_node = parent
            return True
        return False
    
    def can_goto_first_child(self, named_only: bool = False) -> bool:
        """Check if we can move to the first child."""
        if named_only:
            return self.current_node.named_child_count() > 0
        else:
            return self.current_node.child_count() > 0
    
    def can_goto_next_sibling(self, named_only: bool = False) -> bool:
        """Check if we can move to the next sibling."""
        if named_only:
            next_sibling = self.current_node.next_named_sibling()
        else:
            next_sibling = self.current_node.next_sibling()
        return next_sibling is not None and not next_sibling.is_null()
    
    def can_goto_prev_sibling(self, named_only: bool = False) -> bool:
        """Check if we can move to the previous sibling."""
        if named_only:
            prev_sibling = self.current_node.prev_named_sibling()
        else:
            prev_sibling = self.current_node.prev_sibling()
        return prev_sibling is not None and not prev_sibling.is_null()
    
    def can_goto_parent(self) -> bool:
        """Check if we can move to the parent."""
        parent = self.current_node.parent()
        return parent is not None and not parent.is_null()


class FieldHelper:
    """Helper class for field operations."""
    
    def __init__(self, language: Language):
        """
        Initialize with a language.
        
        Args:
            language: The language to provide field helpers for
        """
        self.language = language
    
    def get_child_by_field(self, node: Node, field_name: str) -> Optional[Node]:
        """
        Get a child node by field name.
        
        Args:
            node: The node to search in
            field_name: The field name to search for
            
        Returns:
            The child node, or None if not found
        """
        return node.child_by_field_name(field_name)
    
    def get_child_by_field_id(self, node: Node, field_id: int) -> Optional[Node]:
        """
        Get a child node by field ID.
        
        Args:
            node: The node to search in
            field_id: The field ID to search for
            
        Returns:
            The child node, or None if not found
        """
        return node.child_by_field_id(field_id)
    
    def get_field_names(self) -> List[str]:
        """Get all field names."""
        field_names = []
        for i in range(1, self.language.field_count + 1):
            field_name = self.language.field_name_for_id(i)
            if field_name:
                field_names.append(field_name)
        return field_names
    
    def get_field_id(self, field_name: str) -> Optional[int]:
        """Get field ID by name."""
        return self.language.field_id_for_name(field_name)


class ValidationHelper:
    """Helper class for validation operations."""
    
    @staticmethod
    def validate_node(node: Node) -> List[str]:
        """
        Validate a node and return any issues.
        
        Args:
            node: The node to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if node.is_null():
            issues.append("Node is null")
        
        if node.is_error():
            issues.append("Node is an error")
        
        if node.has_error():
            issues.append("Node has errors")
        
        if node.is_missing():
            issues.append("Node is missing")
        
        # Check for invalid byte positions
        if node.start_byte > node.end_byte:
            issues.append("Start byte is greater than end byte")
        
        # Check for invalid point positions
        if node.start_point.row > node.end_point.row:
            issues.append("Start row is greater than end row")
        elif (node.start_point.row == node.end_point.row and 
              node.start_point.column > node.end_point.column):
            issues.append("Start column is greater than end column on same row")
        
        return issues
    
    @staticmethod
    def validate_query(query: Query) -> List[str]:
        """
        Validate a query and return any issues.
        
        Args:
            query: The query to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if query.pattern_count == 0:
            issues.append("Query has no patterns")
        
        if query.capture_count == 0:
            issues.append("Query has no captures")
        
        # Validate each pattern
        for i in range(query.pattern_count):
            predicates = query.predicates_for_pattern(i)
            if not predicates:
                issues.append(f"Pattern {i} has no predicates")
        
        return issues
    
    @staticmethod
    def validate_language(language: Language) -> List[str]:
        """
        Validate a language and return any issues.
        
        Args:
            language: The language to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if language.version == 0:
            issues.append("Language version is 0")
        
        if language.field_count == 0:
            issues.append("Language has no fields")
        
        if language.symbol_count == 0:
            issues.append("Language has no symbols")
        
        return issues


class ConditionalLogicHelper:
    """Helper class for conditional logic operations."""
    
    @staticmethod
    def should_include_node(node: Node, named_only: bool = False, 
                          exclude_extra: bool = False, exclude_missing: bool = False) -> bool:
        """
        Determine if a node should be included based on conditions.
        
        Args:
            node: The node to check
            named_only: Whether to only include named nodes
            exclude_extra: Whether to exclude extra nodes
            exclude_missing: Whether to exclude missing nodes
            
        Returns:
            True if the node should be included, False otherwise
        """
        if node.is_null():
            return False
        
        if named_only and not node.is_named():
            return False
        
        if exclude_extra and node.is_extra():
            return False
        
        if exclude_missing and node.is_missing():
            return False
        
        return True
    
    @staticmethod
    def get_node_children(node: Node, named_only: bool = False, 
                         exclude_extra: bool = False, exclude_missing: bool = False) -> List[Node]:
        """
        Get children of a node based on conditions.
        
        Args:
            node: The node to get children from
            named_only: Whether to only get named children
            exclude_extra: Whether to exclude extra children
            exclude_missing: Whether to exclude missing children
            
        Returns:
            List of filtered children
        """
        children = []
        
        if named_only:
            for child in node.named_children():
                if ConditionalLogicHelper.should_include_node(child, named_only, exclude_extra, exclude_missing):
                    children.append(child)
        else:
            for child in node.children():
                if ConditionalLogicHelper.should_include_node(child, named_only, exclude_extra, exclude_missing):
                    children.append(child)
        
        return children
    
    @staticmethod
    def filter_nodes_by_type(nodes: List[Node], node_types: List[str], 
                           include: bool = True) -> List[Node]:
        """
        Filter nodes by type.
        
        Args:
            nodes: List of nodes to filter
            node_types: List of node types to filter by
            include: Whether to include or exclude the specified types
            
        Returns:
            Filtered list of nodes
        """
        filtered = []
        for node in nodes:
            if include and node.type in node_types:
                filtered.append(node)
            elif not include and node.type not in node_types:
                filtered.append(node)
        return filtered
    
    @staticmethod
    def filter_nodes_by_predicate(nodes: List[Node], predicate: Callable[[Node], bool]) -> List[Node]:
        """
        Filter nodes by a predicate function.
        
        Args:
            nodes: List of nodes to filter
            predicate: Function that takes a node and returns True to include it
            
        Returns:
            Filtered list of nodes
        """
        return [node for node in nodes if predicate(node)]
