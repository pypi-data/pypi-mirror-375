"""
Class structure and inheritance patterns matching Delphi implementation.

This module provides proper class structure, inheritance, scope, visibility,
and forward declarations that match the Delphi tree-sitter implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Callable, Type, TypeVar, Generic
from .types import Point, Range, Input, InputEncoding, SymbolType, Quantifier, QueryError
from .exceptions import TreeSitterException

# Forward declarations and type aliases (matching Delphi patterns)
T = TypeVar('T')
PTSLanguage = Any  # Forward declaration
TTSLanguage = Any  # Forward declaration
PTSParser = Any    # Forward declaration
PTSTree = Any      # Forward declaration
PTSTreeCursor = Any # Forward declaration
PTSQuery = Any     # Forward declaration
PTSQueryCursor = Any # Forward declaration
TSTreeCursor = Any # Forward declaration
TSNode = Any       # Forward declaration
TSPoint = Any      # Forward declaration
TSFieldId = int
TSSymbol = int
TSSymbolType = SymbolType
TSStateId = int
TSInputEncoding = InputEncoding
TSQueryError = QueryError
TSQuantifier = Quantifier
TSQueryPredicateStep = Any
TSQueryPredicateStepType = int
TSQueryPredicateStepArray = List[TSQueryPredicateStep]
TSQueryCapture = Any
TSQueryCaptureArray = List[TSQueryCapture]
TSQueryMatch = Any

# Forward declaration classes (matching Delphi forward declarations)
class TTSNode:
    """Forward declaration for TTSNode (matching Delphi pattern)."""
    pass

class TTSPoint:
    """Forward declaration for TTSPoint (matching Delphi pattern)."""
    pass

# Type aliases (matching Delphi type aliases)
TTSInputEncoding = TSInputEncoding
TTSQueryError = TSQueryError
TTSQuantifier = TSQuantifier
TTSQueryPredicateStep = TSQueryPredicateStep
TTSQueryPredicateStepType = TSQueryPredicateStepType
TTSQueryPredicateStepArray = TSQueryPredicateStepArray
TTSQueryCapture = TSQueryCapture
TTSQueryCaptureArray = TSQueryCaptureArray
TTSQueryMatch = TSQueryMatch

# Function pointer types (matching Delphi patterns)
PTSGetLanguageFunc = Callable[[], PTSLanguage]
TTSParseReadFunction = Callable[[int, Point, int], bytes]


class TTSLanguageHelper:
    """
    Record helper for TTSLanguage (matching Delphi TTSLanguageHelper).
    
    This class provides helper methods for language operations,
    similar to Delphi's record helper pattern.
    """
    
    def __init__(self, language: 'TTSLanguage'):
        """
        Initialize the language helper.
        
        Args:
            language: The language to provide helpers for
        """
        self._language = language
    
    # Private helper methods (matching Delphi private section)
    def _get_field_name(self, field_id: TSFieldId) -> str:
        """Get field name by ID."""
        return self._language.field_name_for_id(field_id)
    
    def _get_field_id(self, field_name: str) -> TSFieldId:
        """Get field ID by name."""
        return self._language.field_id_for_name(field_name)
    
    def _get_symbol_name(self, symbol: TSSymbol) -> str:
        """Get symbol name by ID."""
        return self._language.symbol_name(symbol)
    
    def _get_symbol_for_name(self, symbol_name: str, is_named: bool) -> TSSymbol:
        """Get symbol ID by name."""
        return self._language.symbol_for_name(symbol_name, is_named)
    
    def _get_symbol_type(self, symbol: TSSymbol) -> TSSymbolType:
        """Get symbol type."""
        return self._language.symbol_type(symbol)
    
    # Public methods (matching Delphi public section)
    def version(self) -> int:
        """Get language version."""
        return self._language.version
    
    def field_count(self) -> int:
        """Get field count."""
        return self._language.field_count
    
    def symbol_count(self) -> int:
        """Get symbol count."""
        return self._language.symbol_count
    
    def next_state(self, state: TSStateId, symbol: TSSymbol) -> TSStateId:
        """Get next state."""
        return self._language.next_state(state, symbol)
    
    # Properties (matching Delphi property syntax)
    @property
    def field_name(self) -> Dict[TSFieldId, str]:
        """Field name property."""
        return {i: self._get_field_name(i) for i in range(1, self.field_count() + 1)}
    
    @property
    def field_id(self) -> Dict[str, TSFieldId]:
        """Field ID property."""
        return {self._get_field_name(i): i for i in range(1, self.field_count() + 1)}
    
    @property
    def symbol_name(self) -> Dict[TSSymbol, str]:
        """Symbol name property."""
        return {i: self._get_symbol_name(i) for i in range(1, self.symbol_count() + 1)}
    
    @property
    def symbol_for_name(self) -> Dict[str, TSSymbol]:
        """Symbol for name property."""
        return {self._get_symbol_name(i): i for i in range(1, self.symbol_count() + 1)}
    
    @property
    def symbol_type(self) -> Dict[TSSymbol, TSSymbolType]:
        """Symbol type property."""
        return {i: self._get_symbol_type(i) for i in range(1, self.symbol_count() + 1)}


class TTSQueryMatchHelper:
    """
    Record helper for TTSQueryMatch (matching Delphi TTSQueryMatchHelper).
    
    This class provides helper methods for query match operations.
    """
    
    def __init__(self, match: 'TSQueryMatch'):
        """
        Initialize the query match helper.
        
        Args:
            match: The query match to provide helpers for
        """
        self._match = match
    
    def captures_array(self) -> TSQueryCaptureArray:
        """Get captures as array."""
        return self._match.captures


class TTSNodeHelper:
    """
    Record helper for TTSNode (matching Delphi TTSNodeHelper pattern).
    
    This class provides helper methods for node operations.
    """
    
    def __init__(self, node: 'TSNode'):
        """
        Initialize the node helper.
        
        Args:
            node: The node to provide helpers for
        """
        self._node = node
    
    def language(self) -> PTSLanguage:
        """Get node language."""
        return self._node.language()
    
    def node_type(self) -> str:
        """Get node type."""
        return self._node.type
    
    def symbol(self) -> TSSymbol:
        """Get node symbol."""
        return self._node.symbol
    
    def grammar_type(self) -> str:
        """Get grammar type."""
        return self._node.grammar_type
    
    def grammar_symbol(self) -> TSSymbol:
        """Get grammar symbol."""
        return self._node.grammar_symbol
    
    def is_null(self) -> bool:
        """Check if node is null."""
        return self._node.is_null()
    
    def is_error(self) -> bool:
        """Check if node is error."""
        return self._node.is_error()
    
    def has_error(self) -> bool:
        """Check if node has error."""
        return self._node.has_error()
    
    def has_changes(self) -> bool:
        """Check if node has changes."""
        return self._node.has_changes()
    
    def is_extra(self) -> bool:
        """Check if node is extra."""
        return self._node.is_extra()
    
    def is_missing(self) -> bool:
        """Check if node is missing."""
        return self._node.is_missing()
    
    def is_named(self) -> bool:
        """Check if node is named."""
        return self._node.is_named()
    
    def parent(self) -> 'TSNode':
        """Get parent node."""
        return self._node.parent()
    
    def to_string(self) -> str:
        """Get string representation."""
        return self._node.to_string()
    
    def child_count(self) -> int:
        """Get child count."""
        return self._node.child_count()
    
    def child(self, index: int) -> 'TSNode':
        """Get child by index."""
        return self._node.child(index)
    
    def next_sibling(self) -> 'TSNode':
        """Get next sibling."""
        return self._node.next_sibling()
    
    def prev_sibling(self) -> 'TSNode':
        """Get previous sibling."""
        return self._node.prev_sibling()
    
    def named_child_count(self) -> int:
        """Get named child count."""
        return self._node.named_child_count()
    
    def named_child(self, index: int) -> 'TSNode':
        """Get named child by index."""
        return self._node.named_child(index)
    
    def next_named_sibling(self) -> 'TSNode':
        """Get next named sibling."""
        return self._node.next_named_sibling()
    
    def prev_named_sibling(self) -> 'TSNode':
        """Get previous named sibling."""
        return self._node.prev_named_sibling()
    
    def start_byte(self) -> int:
        """Get start byte."""
        return self._node.start_byte
    
    def start_point(self) -> TSPoint:
        """Get start point."""
        return self._node.start_point
    
    def end_byte(self) -> int:
        """Get end byte."""
        return self._node.end_byte
    
    def end_point(self) -> TSPoint:
        """Get end point."""
        return self._node.end_point
    
    def child_by_field(self, field_name: str) -> 'TSNode':
        """Get child by field name."""
        return self._node.child_by_field_name(field_name)
    
    def child_by_field_id(self, field_id: TSFieldId) -> 'TSNode':
        """Get child by field ID."""
        return self._node.child_by_field_id(field_id)
    
    def descendant_count(self) -> int:
        """Get descendant count."""
        return self._node.descendant_count()
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, TTSNodeHelper):
            return False
        return self._node.equals(other._node)


class TTSPointHelper:
    """
    Record helper for TTSPoint (matching Delphi TTSPointHelper).
    
    This class provides helper methods for point operations.
    """
    
    def __init__(self, point: TSPoint):
        """
        Initialize the point helper.
        
        Args:
            point: The point to provide helpers for
        """
        self._point = point
    
    def to_string(self) -> str:
        """Get string representation."""
        return f"({self._point.row}, {self._point.column})"


class TTSBaseClass(ABC):
    """
    Base class for all tree-sitter classes (matching Delphi inheritance patterns).
    
    This provides common functionality and proper inheritance structure.
    """
    
    def __init__(self):
        """Initialize base class."""
        self._initialized = False
        self._destroyed = False
    
    def __del__(self):
        """Destructor (matching Delphi destructor pattern)."""
        if not self._destroyed:
            self.destroy()
    
    @abstractmethod
    def destroy(self):
        """Destroy the object (matching Delphi destructor pattern)."""
        self._destroyed = True
    
    def is_initialized(self) -> bool:
        """Check if object is initialized."""
        return self._initialized
    
    def is_destroyed(self) -> bool:
        """Check if object is destroyed."""
        return self._destroyed


class TTSParser(TTSBaseClass):
    """
    Tree-sitter parser class (matching Delphi TTSParser).
    
    This class provides proper inheritance, scope, and visibility
    matching the Delphi implementation.
    """
    
    def __init__(self):
        """
        Constructor (matching Delphi constructor pattern).
        
        Raises:
            TreeSitterException: If initialization fails
        """
        super().__init__()
        self._parser: Optional[PTSParser] = None
        self._language: Optional[PTSLanguage] = None
        self._create()
        self._initialized = True
    
    def _create(self):
        """Create the parser (private method)."""
        # Implementation would create the actual parser
        self._parser = None
    
    def destroy(self):
        """Destroy the parser (matching Delphi destructor)."""
        if self._parser is not None:
            # Implementation would destroy the actual parser
            self._parser = None
        super().destroy()
    
    # Private methods (matching Delphi strict private section)
    def _get_language(self) -> Optional[PTSLanguage]:
        """Get language (private getter)."""
        return self._language
    
    def _set_language(self, value: PTSLanguage):
        """Set language (private setter)."""
        self._language = value
        # Implementation would set the language on the parser
    
    # Public methods (matching Delphi public section)
    def reset(self):
        """Reset the parser."""
        if not self._initialized:
            raise TreeSitterException("Parser not initialized")
        # Implementation would reset the parser
    
    def parse_string(self, source: str, old_tree: Optional['TTSTree'] = None) -> 'TTSTree':
        """
        Parse string (matching Delphi method signature).
        
        Args:
            source: Source code to parse
            old_tree: Optional old tree for incremental parsing
            
        Returns:
            New syntax tree
            
        Raises:
            TreeSitterException: If parsing fails
        """
        if not self._initialized:
            raise TreeSitterException("Parser not initialized")
        # Implementation would parse the string
        return TTSTree(None, source, self._language)
    
    def parse(self, parse_function: TTSParseReadFunction, 
              encoding: TSInputEncoding, old_tree: Optional['TTSTree'] = None) -> 'TTSTree':
        """
        Parse with function (matching Delphi method signature).
        
        Args:
            parse_function: Function to read input
            encoding: Input encoding
            old_tree: Optional old tree for incremental parsing
            
        Returns:
            New syntax tree
        """
        if not self._initialized:
            raise TreeSitterException("Parser not initialized")
        # Implementation would parse with the function
        return TTSTree(None, "", self._language)
    
    # Properties (matching Delphi property syntax)
    @property
    def parser(self) -> Optional[PTSParser]:
        """Parser property (read-only)."""
        return self._parser
    
    @property
    def language(self) -> Optional[PTSLanguage]:
        """Language property (matching Delphi property)."""
        return self._get_language()
    
    @language.setter
    def language(self, value: PTSLanguage):
        """Language property setter."""
        self._set_language(value)


class TTSTree(TTSBaseClass):
    """
    Tree-sitter tree class (matching Delphi TTSTree).
    
    This class provides proper inheritance and visibility.
    """
    
    def __init__(self, tree: PTSTree, source_code: str, language: PTSLanguage):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            tree: Tree-sitter tree pointer
            source_code: Source code
            language: Language used for parsing
        """
        super().__init__()
        self._tree: PTSTree = tree
        self._source_code = source_code
        self._language = language
        self._initialized = True
    
    def destroy(self):
        """Destroy the tree (matching Delphi destructor)."""
        if self._tree is not None:
            # Implementation would destroy the actual tree
            self._tree = None
        super().destroy()
    
    # Public methods (matching Delphi public section)
    def language(self) -> PTSLanguage:
        """Get language (matching Delphi method)."""
        return self._language
    
    def root_node(self) -> 'TTSNode':
        """Get root node (matching Delphi method)."""
        # Implementation would get the actual root node
        return TTSNode(None, self._source_code, self._language)
    
    def tree_nil_safe(self) -> Optional[PTSTree]:
        """Get tree nil safe (matching Delphi method)."""
        return self._tree if self._tree is not None else None
    
    def clone(self) -> 'TTSTree':
        """Clone the tree (matching Delphi method)."""
        # Implementation would clone the actual tree
        return TTSTree(self._tree, self._source_code, self._language)
    
    # Properties (matching Delphi property syntax)
    @property
    def tree(self) -> PTSTree:
        """Tree property (read-only)."""
        return self._tree


class TTSTreeCursor(TTSBaseClass):
    """
    Tree-sitter tree cursor class (matching Delphi TTSTreeCursor).
    
    This class provides proper inheritance, overloaded constructors,
    and visibility matching the Delphi implementation.
    """
    
    def __init__(self, node: 'TTSNode', cursor_to_copy: Optional['TTSTreeCursor'] = None):
        """
        Constructor with overloads (matching Delphi constructor overloads).
        
        Args:
            node: Node to start from (for first overload)
            cursor_to_copy: Cursor to copy from (for second overload)
        """
        super().__init__()
        self._tree_cursor: TSTreeCursor = None
        self._current_node: Optional[TTSNode] = None
        
        if cursor_to_copy is not None:
            # Second overload: copy from another cursor
            self._copy_from_cursor(cursor_to_copy)
        else:
            # First overload: create from node
            self._create_from_node(node)
        
        self._initialized = True
    
    def _create_from_node(self, node: 'TTSNode'):
        """Create cursor from node (private method)."""
        self._current_node = node
        # Implementation would create the actual cursor
    
    def _copy_from_cursor(self, cursor: 'TTSTreeCursor'):
        """Copy from another cursor (private method)."""
        self._current_node = cursor._current_node
        # Implementation would copy the actual cursor
    
    def destroy(self):
        """Destroy the cursor (matching Delphi destructor)."""
        if self._tree_cursor is not None:
            # Implementation would destroy the actual cursor
            self._tree_cursor = None
        super().destroy()
    
    # Private methods (matching Delphi strict private section)
    def _get_tree_cursor(self) -> TSTreeCursor:
        """Get tree cursor (private getter)."""
        return self._tree_cursor
    
    def _get_current_node(self) -> Optional[TTSNode]:
        """Get current node (private getter)."""
        return self._current_node
    
    def _get_current_field_name(self) -> str:
        """Get current field name (private getter)."""
        return ""  # Implementation would get actual field name
    
    def _get_current_field_id(self) -> TSFieldId:
        """Get current field ID (private getter)."""
        return 0  # Implementation would get actual field ID
    
    def _get_current_depth(self) -> int:
        """Get current depth (private getter)."""
        return 0  # Implementation would get actual depth
    
    def _get_current_descendant_index(self) -> int:
        """Get current descendant index (private getter)."""
        return 0  # Implementation would get actual index
    
    # Public methods (matching Delphi public section)
    def reset(self, node: Optional['TTSNode'] = None, cursor: Optional['TTSTreeCursor'] = None):
        """
        Reset cursor (matching Delphi overloaded method).
        
        Args:
            node: Node to reset to (first overload)
            cursor: Cursor to reset to (second overload)
        """
        if cursor is not None:
            # Second overload: reset to another cursor
            self._copy_from_cursor(cursor)
        elif node is not None:
            # First overload: reset to node
            self._create_from_node(node)
    
    def goto_parent(self) -> bool:
        """Go to parent (matching Delphi method)."""
        # Implementation would move to parent
        return False
    
    def goto_next_sibling(self) -> bool:
        """Go to next sibling (matching Delphi method)."""
        # Implementation would move to next sibling
        return False
    
    def goto_prev_sibling(self) -> bool:
        """Go to previous sibling (matching Delphi method)."""
        # Implementation would move to previous sibling
        return False
    
    def goto_first_child(self) -> bool:
        """Go to first child (matching Delphi method)."""
        # Implementation would move to first child
        return False
    
    def goto_last_child(self) -> bool:
        """Go to last child (matching Delphi method)."""
        # Implementation would move to last child
        return False
    
    def goto_descendant(self, goal_descendant_index: int):
        """Go to descendant (matching Delphi method)."""
        # Implementation would move to descendant
        pass
    
    def goto_first_child_for_goal(self, goal_byte: int) -> int:
        """Go to first child for goal byte (matching Delphi overload)."""
        # Implementation would find first child for byte
        return -1
    
    def goto_first_child_for_goal_point(self, goal_point: TSPoint) -> int:
        """Go to first child for goal point (matching Delphi overload)."""
        # Implementation would find first child for point
        return -1
    
    # Properties (matching Delphi property syntax)
    @property
    def tree_cursor(self) -> TSTreeCursor:
        """Tree cursor property (read-only)."""
        return self._get_tree_cursor()
    
    @property
    def current_node(self) -> Optional[TTSNode]:
        """Current node property (read-only)."""
        return self._get_current_node()
    
    @property
    def current_field_name(self) -> str:
        """Current field name property (read-only)."""
        return self._get_current_field_name()
    
    @property
    def current_field_id(self) -> TSFieldId:
        """Current field ID property (read-only)."""
        return self._get_current_field_id()
    
    @property
    def current_descendant_index(self) -> int:
        """Current descendant index property (read-only)."""
        return self._get_current_descendant_index()
    
    @property
    def current_depth(self) -> int:
        """Current depth property (read-only)."""
        return self._get_current_depth()


class TTSQuery(TTSBaseClass):
    """
    Tree-sitter query class (matching Delphi TTSQuery).
    
    This class provides proper inheritance and visibility.
    """
    
    def __init__(self, language: PTSLanguage, source: str, 
                 error_offset: int, error_type: TSQueryError):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            language: Language for the query
            source: Query source string
            error_offset: Error offset (by reference)
            error_type: Error type (by reference)
        """
        super().__init__()
        self._query: Optional[PTSQuery] = None
        self._language = language
        self._source = source
        self._error_offset = error_offset
        self._error_type = error_type
        self._create()
        self._initialized = True
    
    def _create(self):
        """Create the query (private method)."""
        # Implementation would create the actual query
        self._query = None
    
    def destroy(self):
        """Destroy the query (matching Delphi destructor)."""
        if self._query is not None:
            # Implementation would destroy the actual query
            self._query = None
        super().destroy()
    
    # Public methods (matching Delphi public section)
    def pattern_count(self) -> int:
        """Get pattern count (matching Delphi method)."""
        return 0  # Implementation would get actual count
    
    def capture_count(self) -> int:
        """Get capture count (matching Delphi method)."""
        return 0  # Implementation would get actual count
    
    def string_count(self) -> int:
        """Get string count (matching Delphi method)."""
        return 0  # Implementation would get actual count
    
    def start_byte_for_pattern(self, pattern_index: int) -> int:
        """Get start byte for pattern (matching Delphi method)."""
        return 0  # Implementation would get actual byte
    
    def predicates_for_pattern(self, pattern_index: int) -> TSQueryPredicateStepArray:
        """Get predicates for pattern (matching Delphi method)."""
        return []  # Implementation would get actual predicates
    
    def capture_name_for_id(self, capture_index: int) -> str:
        """Get capture name for ID (matching Delphi method)."""
        return ""  # Implementation would get actual name
    
    def string_value_for_id(self, string_index: int) -> str:
        """Get string value for ID (matching Delphi method)."""
        return ""  # Implementation would get actual value
    
    def quantifier_for_capture(self, pattern_index: int, capture_index: int) -> TSQuantifier:
        """Get quantifier for capture (matching Delphi method)."""
        return TSQuantifier.ONE  # Implementation would get actual quantifier
    
    # Properties (matching Delphi property syntax)
    @property
    def query(self) -> Optional[PTSQuery]:
        """Query property (read-only)."""
        return self._query


class TTSQueryCursor(TTSBaseClass):
    """
    Tree-sitter query cursor class (matching Delphi TTSQueryCursor).
    
    This class provides proper inheritance and visibility.
    """
    
    def __init__(self):
        """Constructor (matching Delphi constructor pattern)."""
        super().__init__()
        self._query_cursor: Optional[PTSQueryCursor] = None
        self._match_limit: int = 0
        self._create()
        self._initialized = True
    
    def _create(self):
        """Create the query cursor (private method)."""
        # Implementation would create the actual cursor
        self._query_cursor = None
    
    def destroy(self):
        """Destroy the query cursor (matching Delphi destructor)."""
        if self._query_cursor is not None:
            # Implementation would destroy the actual cursor
            self._query_cursor = None
        super().destroy()
    
    # Private methods (matching Delphi strict private section)
    def _get_match_limit(self) -> int:
        """Get match limit (private getter)."""
        return self._match_limit
    
    def _set_match_limit(self, value: int):
        """Set match limit (private setter)."""
        self._match_limit = value
        # Implementation would set the actual limit
    
    # Public methods (matching Delphi public section)
    def execute(self, query: TTSQuery, node: 'TTSNode'):
        """Execute query (matching Delphi method)."""
        # Implementation would execute the query
        pass
    
    def did_exceed_match_limit(self) -> bool:
        """Check if exceeded match limit (matching Delphi method)."""
        return False  # Implementation would check actual limit
    
    def set_max_start_depth(self, max_start_depth: int):
        """Set max start depth (matching Delphi method)."""
        # Implementation would set the actual depth
        pass
    
    def next_match(self, match: TSQueryMatch) -> bool:
        """Get next match (matching Delphi method)."""
        return False  # Implementation would get actual match
    
    def next_capture(self, match: TSQueryMatch, capture_index: int) -> bool:
        """Get next capture (matching Delphi method)."""
        return False  # Implementation would get actual capture
    
    # Properties (matching Delphi property syntax)
    @property
    def query_cursor(self) -> Optional[PTSQueryCursor]:
        """Query cursor property (read-only)."""
        return self._query_cursor
    
    @property
    def match_limit(self) -> int:
        """Match limit property (matching Delphi property)."""
        return self._get_match_limit()
    
    @match_limit.setter
    def match_limit(self, value: int):
        """Match limit property setter."""
        self._set_match_limit(value)

