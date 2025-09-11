"""
Forward declarations and mutually dependent classes.

This module provides proper forward declarations and handles mutually
dependent classes that match the Delphi tree-sitter implementation.
"""

from typing import Optional, List, Dict, Any, Union, Callable, Type, TypeVar, Generic, ForwardRef
from abc import ABC, abstractmethod
from .types import Point, Range, Input, InputEncoding, SymbolType, Quantifier, QueryError
from .exceptions import TreeSitterException

# Forward declarations using ForwardRef (matching Delphi forward declarations)
TTSNode = ForwardRef('TTSNode')
TTSTree = ForwardRef('TTSTree')
TTSParser = ForwardRef('TTSParser')
TTSTreeCursor = ForwardRef('TTSTreeCursor')
TTSQuery = ForwardRef('TTSQuery')
TTSQueryCursor = ForwardRef('TTSQueryCursor')
TTSLanguage = ForwardRef('TTSLanguage')
TTSInput = ForwardRef('TTSInput')
TTSLogger = ForwardRef('TTSLogger')
TTSAllocator = ForwardRef('TTSAllocator')
TTSQueryMatch = ForwardRef('TTSQueryMatch')
TTSQueryCapture = ForwardRef('TTSQueryCapture')
TTSQueryPredicateStep = ForwardRef('TTSQueryPredicateStep')
TTSLookAheadIterator = ForwardRef('TTSLookAheadIterator')
TTSWasmEngine = ForwardRef('TTSWasmEngine')
TTSWasmStore = ForwardRef('TTSWasmStore')
TTSWasmParser = ForwardRef('TTSWasmParser')

# Type aliases for forward references
PTSLanguage = ForwardRef('PTSLanguage')
PTSParser = ForwardRef('PTSParser')
PTSTree = ForwardRef('PTSTree')
PTSTreeCursor = ForwardRef('PTSTreeCursor')
PTSQuery = ForwardRef('PTSQuery')
PTSQueryCursor = ForwardRef('PTSQueryCursor')
PTSInput = ForwardRef('PTSInput')
PTSLogger = ForwardRef('PTSLogger')
PTSAllocator = ForwardRef('PTSAllocator')
PTSQueryMatch = ForwardRef('PTSQueryMatch')
PTSQueryCapture = ForwardRef('PTSQueryCapture')
PTSQueryPredicateStep = ForwardRef('PTSQueryPredicateStep')
PTSLookAheadIterator = ForwardRef('PTSLookAheadIterator')
PTSWasmEngine = ForwardRef('PTSWasmEngine')
PTSWasmStore = ForwardRef('PTSWasmStore')
PTSWasmParser = ForwardRef('PTSWasmParser')

# Function pointer types (matching Delphi function pointer patterns)
PTSGetLanguageFunc = Callable[[], PTSLanguage]
TTSParseReadFunction = Callable[[int, Point, int], bytes]
TTSInputReadFunction = Callable[[int, Point, int], bytes]
TTSInputSeekFunction = Callable[[int, Point], None]
TTSLoggerFunction = Callable[[str, int, int, int, int], None]
TTSAllocatorAllocateFunction = Callable[[int], Any]
TTSAllocatorFreeFunction = Callable[[Any], None]

# Enum types (matching Delphi enum patterns)
TSFieldId = int
TSSymbol = int
TSSymbolType = SymbolType
TSStateId = int
TSInputEncoding = InputEncoding
TSQueryError = QueryError
TSQuantifier = Quantifier
TSQueryPredicateStepType = int
TSWasmErrorKind = int

# Array types (matching Delphi array patterns)
TSQueryPredicateStepArray = List[TTSQueryPredicateStep]
TSQueryCaptureArray = List[TTSQueryCapture]
TSInputEditArray = List[Any]
TSRangeArray = List[Range]
TSNodeArray = List[TTSNode]
TSStringArray = List[str]
TSFieldIdArray = List[TSFieldId]
TSSymbolArray = List[TSSymbol]


class TTSForwardDeclaration:
    """
    Base class for forward declarations (matching Delphi forward declaration patterns).
    
    This class provides the base functionality for all forward-declared classes
    with proper type checking and resolution.
    """
    
    def __init__(self, name: str):
        """
        Initialize the forward declaration.
        
        Args:
            name: The name of the forward-declared class
        """
        self._name = name
        self._resolved = False
        self._resolved_class: Optional[Type] = None
    
    def get_name(self) -> str:
        """Get the forward declaration name."""
        return self._name
    
    def is_resolved(self) -> bool:
        """Check if the forward declaration is resolved."""
        return self._resolved
    
    def resolve(self, resolved_class: Type):
        """
        Resolve the forward declaration.
        
        Args:
            resolved_class: The resolved class type
        """
        self._resolved_class = resolved_class
        self._resolved = True
    
    def get_resolved_class(self) -> Optional[Type]:
        """Get the resolved class."""
        return self._resolved_class


class TTSMutuallyDependent:
    """
    Base class for mutually dependent classes (matching Delphi mutually dependent patterns).
    
    This class provides the base functionality for classes that have
    circular dependencies and need special handling.
    """
    
    def __init__(self):
        """Initialize the mutually dependent class."""
        self._dependencies: List['TTSMutuallyDependent'] = []
        self._resolved_dependencies: Dict[str, 'TTSMutuallyDependent'] = {}
        self._initialized = False
    
    def add_dependency(self, dependency: 'TTSMutuallyDependent'):
        """
        Add a dependency.
        
        Args:
            dependency: The dependency to add
        """
        if dependency not in self._dependencies:
            self._dependencies.append(dependency)
    
    def remove_dependency(self, dependency: 'TTSMutuallyDependent'):
        """
        Remove a dependency.
        
        Args:
            dependency: The dependency to remove
        """
        if dependency in self._dependencies:
            self._dependencies.remove(dependency)
    
    def get_dependencies(self) -> List['TTSMutuallyDependent']:
        """Get all dependencies."""
        return self._dependencies.copy()
    
    def resolve_dependency(self, name: str, dependency: 'TTSMutuallyDependent'):
        """
        Resolve a dependency by name.
        
        Args:
            name: The name of the dependency
            dependency: The dependency to resolve
        """
        self._resolved_dependencies[name] = dependency
    
    def get_resolved_dependency(self, name: str) -> Optional['TTSMutuallyDependent']:
        """
        Get a resolved dependency by name.
        
        Args:
            name: The name of the dependency
            
        Returns:
            The resolved dependency, or None if not found
        """
        return self._resolved_dependencies.get(name)
    
    def is_initialized(self) -> bool:
        """Check if the class is initialized."""
        return self._initialized
    
    def initialize(self):
        """Initialize the class."""
        if not self._initialized:
            self._initialized = True


class TTSNode(TTSMutuallyDependent):
    """
    Tree-sitter node class (matching Delphi TTSNode).
    
    This class has mutual dependencies with TTSTree and TTSParser.
    """
    
    def __init__(self, node_ptr: Any, source_code: str, language: PTSLanguage):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            node_ptr: Pointer to the tree-sitter node
            source_code: Source code
            language: Language used for parsing
        """
        super().__init__()
        self._node_ptr = node_ptr
        self._source_code = source_code
        self._language = language
        self._tree: Optional[TTSTree] = None
        self._parser: Optional[TTSParser] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the node."""
        super().initialize()
    
    # Properties (matching Delphi property patterns)
    @property
    def type(self) -> str:
        """Get node type."""
        return "unknown"  # Implementation would get actual type
    
    @property
    def symbol(self) -> TSSymbol:
        """Get node symbol."""
        return 0  # Implementation would get actual symbol
    
    @property
    def grammar_type(self) -> str:
        """Get grammar type."""
        return "unknown"  # Implementation would get actual grammar type
    
    @property
    def grammar_symbol(self) -> TSSymbol:
        """Get grammar symbol."""
        return 0  # Implementation would get actual grammar symbol
    
    @property
    def start_byte(self) -> int:
        """Get start byte."""
        return 0  # Implementation would get actual start byte
    
    @property
    def end_byte(self) -> int:
        """Get end byte."""
        return 0  # Implementation would get actual end byte
    
    @property
    def start_point(self) -> Point:
        """Get start point."""
        return Point(0, 0)  # Implementation would get actual start point
    
    @property
    def end_point(self) -> Point:
        """Get end point."""
        return Point(0, 0)  # Implementation would get actual end point
    
    @property
    def text(self) -> str:
        """Get node text."""
        return ""  # Implementation would get actual text
    
    # Methods (matching Delphi method patterns)
    def is_null(self) -> bool:
        """Check if node is null."""
        return self._node_ptr is None
    
    def is_named(self) -> bool:
        """Check if node is named."""
        return False  # Implementation would check actual named status
    
    def is_missing(self) -> bool:
        """Check if node is missing."""
        return False  # Implementation would check actual missing status
    
    def is_extra(self) -> bool:
        """Check if node is extra."""
        return False  # Implementation would check actual extra status
    
    def has_changes(self) -> bool:
        """Check if node has changes."""
        return False  # Implementation would check actual changes status
    
    def has_error(self) -> bool:
        """Check if node has error."""
        return False  # Implementation would check actual error status
    
    def is_error(self) -> bool:
        """Check if node is error."""
        return False  # Implementation would check actual error status
    
    def parse_state(self) -> TSStateId:
        """Get parse state."""
        return 0  # Implementation would get actual parse state
    
    def next_parse_state(self) -> TSStateId:
        """Get next parse state."""
        return 0  # Implementation would get actual next parse state
    
    def parent(self) -> Optional[TTSNode]:
        """Get parent node."""
        return None  # Implementation would get actual parent
    
    def child(self, index: int) -> Optional[TTSNode]:
        """Get child by index."""
        return None  # Implementation would get actual child
    
    def child_count(self) -> int:
        """Get child count."""
        return 0  # Implementation would get actual child count
    
    def named_child(self, index: int) -> Optional[TTSNode]:
        """Get named child by index."""
        return None  # Implementation would get actual named child
    
    def named_child_count(self) -> int:
        """Get named child count."""
        return 0  # Implementation would get actual named child count
    
    def child_by_field_name(self, field_name: str) -> Optional[TTSNode]:
        """Get child by field name."""
        return None  # Implementation would get actual child by field name
    
    def child_by_field_id(self, field_id: TSFieldId) -> Optional[TTSNode]:
        """Get child by field ID."""
        return None  # Implementation would get actual child by field ID
    
    def field_name_for_child(self, child_index: int) -> Optional[str]:
        """Get field name for child."""
        return None  # Implementation would get actual field name
    
    def next_sibling(self) -> Optional[TTSNode]:
        """Get next sibling."""
        return None  # Implementation would get actual next sibling
    
    def prev_sibling(self) -> Optional[TTSNode]:
        """Get previous sibling."""
        return None  # Implementation would get actual previous sibling
    
    def next_named_sibling(self) -> Optional[TTSNode]:
        """Get next named sibling."""
        return None  # Implementation would get actual next named sibling
    
    def prev_named_sibling(self) -> Optional[TTSNode]:
        """Get previous named sibling."""
        return None  # Implementation would get actual previous named sibling
    
    def first_child_for_byte(self, byte: int) -> Optional[TTSNode]:
        """Get first child for byte."""
        return None  # Implementation would get actual first child for byte
    
    def first_named_child_for_byte(self, byte: int) -> Optional[TTSNode]:
        """Get first named child for byte."""
        return None  # Implementation would get actual first named child for byte
    
    def descendant_count(self) -> int:
        """Get descendant count."""
        return 0  # Implementation would get actual descendant count
    
    def descendant_for_byte_range(self, start_byte: int, end_byte: int) -> Optional[TTSNode]:
        """Get descendant for byte range."""
        return None  # Implementation would get actual descendant for byte range
    
    def descendant_for_point_range(self, start_point: Point, end_point: Point) -> Optional[TTSNode]:
        """Get descendant for point range."""
        return None  # Implementation would get actual descendant for point range
    
    def named_descendant_for_byte_range(self, start_byte: int, end_byte: int) -> Optional[TTSNode]:
        """Get named descendant for byte range."""
        return None  # Implementation would get actual named descendant for byte range
    
    def named_descendant_for_point_range(self, start_point: Point, end_point: Point) -> Optional[TTSNode]:
        """Get named descendant for point range."""
        return None  # Implementation would get actual named descendant for point range
    
    def edit(self, edit: Any) -> TTSNode:
        """Edit the node."""
        return self  # Implementation would perform actual edit
    
    def equals(self, other: TTSNode) -> bool:
        """Check if nodes are equal."""
        return self._node_ptr == other._node_ptr
    
    def to_string(self) -> str:
        """Get string representation."""
        return f"TTSNode({self.type})"
    
    def children(self) -> List[TTSNode]:
        """Get all children."""
        return []  # Implementation would get actual children
    
    def named_children(self) -> List[TTSNode]:
        """Get all named children."""
        return []  # Implementation would get actual named children
    
    def walk(self) -> TTSTreeCursor:
        """Get tree cursor for walking."""
        return TTSTreeCursor(self)  # Implementation would create actual cursor
    
    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, TTSNode):
            return False
        return self.equals(other)
    
    def __str__(self) -> str:
        """Get string representation."""
        return self.to_string()
    
    # Mutual dependency methods
    def set_tree(self, tree: TTSTree):
        """Set the associated tree."""
        self._tree = tree
        self.resolve_dependency("tree", tree)
    
    def get_tree(self) -> Optional[TTSTree]:
        """Get the associated tree."""
        return self._tree
    
    def set_parser(self, parser: TTSParser):
        """Set the associated parser."""
        self._parser = parser
        self.resolve_dependency("parser", parser)
    
    def get_parser(self) -> Optional[TTSParser]:
        """Get the associated parser."""
        return self._parser


class TTSTree(TTSMutuallyDependent):
    """
    Tree-sitter tree class (matching Delphi TTSTree).
    
    This class has mutual dependencies with TTSNode and TTSParser.
    """
    
    def __init__(self, tree_ptr: Any, source_code: str, language: PTSLanguage):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            tree_ptr: Pointer to the tree-sitter tree
            source_code: Source code
            language: Language used for parsing
        """
        super().__init__()
        self._tree_ptr = tree_ptr
        self._source_code = source_code
        self._language = language
        self._root_node: Optional[TTSNode] = None
        self._parser: Optional[TTSParser] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the tree."""
        super().initialize()
        # Create root node with mutual dependency
        self._root_node = TTSNode(None, self._source_code, self._language)
        self._root_node.set_tree(self)
        self.resolve_dependency("root_node", self._root_node)
    
    # Properties (matching Delphi property patterns)
    @property
    def root_node(self) -> TTSNode:
        """Get root node."""
        return self._root_node
    
    # Methods (matching Delphi method patterns)
    def root_node_with_offset(self, offset_byte: int, offset_point: Point) -> TTSNode:
        """Get root node with offset."""
        return self._root_node  # Implementation would get actual root node with offset
    
    def language(self) -> PTSLanguage:
        """Get language."""
        return self._language
    
    def included_ranges(self) -> List[Range]:
        """Get included ranges."""
        return []  # Implementation would get actual included ranges
    
    def edit(self, edit: Any) -> TTSTree:
        """Edit the tree."""
        return self  # Implementation would perform actual edit
    
    def get_changed_ranges(self, old_tree: TTSTree) -> List[Range]:
        """Get changed ranges."""
        return []  # Implementation would get actual changed ranges
    
    def print_dot_graph(self, file_path: str):
        """Print dot graph."""
        pass  # Implementation would print actual dot graph
    
    def copy(self) -> TTSTree:
        """Copy the tree."""
        return TTSTree(self._tree_ptr, self._source_code, self._language)
    
    def __del__(self):
        """Destructor."""
        if self._tree_ptr is not None:
            # Implementation would destroy actual tree
            pass
    
    # Mutual dependency methods
    def set_parser(self, parser: TTSParser):
        """Set the associated parser."""
        self._parser = parser
        self.resolve_dependency("parser", parser)
        if self._root_node:
            self._root_node.set_parser(parser)
    
    def get_parser(self) -> Optional[TTSParser]:
        """Get the associated parser."""
        return self._parser


class TTSParser(TTSMutuallyDependent):
    """
    Tree-sitter parser class (matching Delphi TTSParser).
    
    This class has mutual dependencies with TTSTree and TTSNode.
    """
    
    def __init__(self):
        """Constructor (matching Delphi constructor pattern)."""
        super().__init__()
        self._parser_ptr = None
        self._language: Optional[PTSLanguage] = None
        self._timeout_micros = 0
        self._cancellation_flag = None
        self._logger: Optional[TTSLogger] = None
        self._included_ranges: List[Range] = []
        self._print_dot_graphs = False
        self._initialize()
    
    def _initialize(self):
        """Initialize the parser."""
        super().initialize()
        # Implementation would create actual parser
    
    # Properties (matching Delphi property patterns)
    @property
    def language(self) -> Optional[PTSLanguage]:
        """Get language."""
        return self._language
    
    @language.setter
    def language(self, value: PTSLanguage):
        """Set language."""
        self._language = value
        # Implementation would set actual language
    
    # Methods (matching Delphi method patterns)
    def parse_string(self, source: str, old_tree: Optional[TTSTree] = None) -> TTSTree:
        """Parse string."""
        tree = TTSTree(None, source, self._language)
        tree.set_parser(self)
        return tree
    
    def parse_string_encoding(self, source: str, encoding: TSInputEncoding, 
                            old_tree: Optional[TTSTree] = None) -> TTSTree:
        """Parse string with encoding."""
        return self.parse_string(source, old_tree)
    
    def parse(self, input_obj: TTSInput, old_tree: Optional[TTSTree] = None) -> TTSTree:
        """Parse with input."""
        tree = TTSTree(None, "", self._language)
        tree.set_parser(self)
        return tree
    
    def reset(self):
        """Reset parser."""
        pass  # Implementation would reset actual parser
    
    def set_timeout_micros(self, timeout: int):
        """Set timeout in microseconds."""
        self._timeout_micros = timeout
    
    def get_timeout_micros(self) -> int:
        """Get timeout in microseconds."""
        return self._timeout_micros
    
    def set_cancellation_flag(self, flag: Any):
        """Set cancellation flag."""
        self._cancellation_flag = flag
    
    def get_cancellation_flag(self) -> Any:
        """Get cancellation flag."""
        return self._cancellation_flag
    
    def set_logger(self, logger: TTSLogger):
        """Set logger."""
        self._logger = logger
    
    def get_logger(self) -> Optional[TTSLogger]:
        """Get logger."""
        return self._logger
    
    def set_included_ranges(self, ranges: List[Range]):
        """Set included ranges."""
        self._included_ranges = ranges
    
    def get_included_ranges(self) -> List[Range]:
        """Get included ranges."""
        return self._included_ranges
    
    def print_dot_graphs(self, enabled: bool):
        """Set print dot graphs."""
        self._print_dot_graphs = enabled
    
    def __del__(self):
        """Destructor."""
        if self._parser_ptr is not None:
            # Implementation would destroy actual parser
            pass


class TTSTreeCursor(TTSMutuallyDependent):
    """
    Tree-sitter tree cursor class (matching Delphi TTSTreeCursor).
    
    This class has mutual dependencies with TTSNode and TTSTree.
    """
    
    def __init__(self, node: TTSNode, cursor_to_copy: Optional['TTSTreeCursor'] = None):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            node: Node to start from
            cursor_to_copy: Optional cursor to copy from
        """
        super().__init__()
        self._cursor_ptr = None
        self._current_node = node
        self._current_field_name = ""
        self._current_field_id = 0
        self._current_depth = 0
        self._current_descendant_index = 0
        self._initialize()
    
    def _initialize(self):
        """Initialize the cursor."""
        super().initialize()
        # Implementation would create actual cursor
    
    # Properties (matching Delphi property patterns)
    @property
    def current_node(self) -> TTSNode:
        """Get current node."""
        return self._current_node
    
    @property
    def current_field_name(self) -> str:
        """Get current field name."""
        return self._current_field_name
    
    @property
    def current_field_id(self) -> TSFieldId:
        """Get current field ID."""
        return self._current_field_id
    
    @property
    def current_depth(self) -> int:
        """Get current depth."""
        return self._current_depth
    
    @property
    def current_descendant_index(self) -> int:
        """Get current descendant index."""
        return self._current_descendant_index
    
    # Methods (matching Delphi method patterns)
    def reset(self, node: Optional[TTSNode] = None, cursor: Optional['TTSTreeCursor'] = None):
        """Reset cursor."""
        if node is not None:
            self._current_node = node
        elif cursor is not None:
            self._current_node = cursor._current_node
        # Implementation would reset actual cursor
    
    def reset_to(self, cursor: 'TTSTreeCursor'):
        """Reset to another cursor."""
        self._current_node = cursor._current_node
        # Implementation would reset actual cursor
    
    def goto_parent(self) -> bool:
        """Go to parent."""
        return False  # Implementation would go to actual parent
    
    def goto_next_sibling(self) -> bool:
        """Go to next sibling."""
        return False  # Implementation would go to actual next sibling
    
    def goto_prev_sibling(self) -> bool:
        """Go to previous sibling."""
        return False  # Implementation would go to actual previous sibling
    
    def goto_first_child(self) -> bool:
        """Go to first child."""
        return False  # Implementation would go to actual first child
    
    def goto_last_child(self) -> bool:
        """Go to last child."""
        return False  # Implementation would go to actual last child
    
    def goto_descendant(self, goal_descendant_index: int):
        """Go to descendant."""
        pass  # Implementation would go to actual descendant
    
    def goto_first_child_for_byte(self, goal_byte: int) -> int:
        """Go to first child for byte."""
        return -1  # Implementation would go to actual first child for byte
    
    def goto_first_child_for_point(self, goal_point: Point) -> int:
        """Go to first child for point."""
        return -1  # Implementation would go to actual first child for point
    
    def copy(self) -> 'TTSTreeCursor':
        """Copy the cursor."""
        return TTSTreeCursor(self._current_node, self)
    
    def __del__(self):
        """Destructor."""
        if self._cursor_ptr is not None:
            # Implementation would destroy actual cursor
            pass


# Forward declaration registry (matching Delphi forward declaration management)
FORWARD_DECLARATIONS: Dict[str, TTSForwardDeclaration] = {}

def register_forward_declaration(name: str) -> TTSForwardDeclaration:
    """
    Register a forward declaration.
    
    Args:
        name: The name of the forward declaration
        
    Returns:
        The forward declaration object
    """
    if name not in FORWARD_DECLARATIONS:
        FORWARD_DECLARATIONS[name] = TTSForwardDeclaration(name)
    return FORWARD_DECLARATIONS[name]

def resolve_forward_declaration(name: str, resolved_class: Type):
    """
    Resolve a forward declaration.
    
    Args:
        name: The name of the forward declaration
        resolved_class: The resolved class type
    """
    if name in FORWARD_DECLARATIONS:
        FORWARD_DECLARATIONS[name].resolve(resolved_class)

def get_forward_declaration(name: str) -> Optional[TTSForwardDeclaration]:
    """
    Get a forward declaration.
    
    Args:
        name: The name of the forward declaration
        
    Returns:
        The forward declaration object, or None if not found
    """
    return FORWARD_DECLARATIONS.get(name)

# Register all forward declarations
register_forward_declaration("TTSNode")
register_forward_declaration("TTSTree")
register_forward_declaration("TTSParser")
register_forward_declaration("TTSTreeCursor")
register_forward_declaration("TTSQuery")
register_forward_declaration("TTSQueryCursor")
register_forward_declaration("TTSLanguage")
register_forward_declaration("TTSInput")
register_forward_declaration("TTSLogger")
register_forward_declaration("TTSAllocator")
register_forward_declaration("TTSQueryMatch")
register_forward_declaration("TTSQueryCapture")
register_forward_declaration("TTSQueryPredicateStep")
register_forward_declaration("TTSLookAheadIterator")
register_forward_declaration("TTSWasmEngine")
register_forward_declaration("TTSWasmStore")
register_forward_declaration("TTSWasmParser")

# Resolve forward declarations
resolve_forward_declaration("TTSNode", TTSNode)
resolve_forward_declaration("TTSTree", TTSTree)
resolve_forward_declaration("TTSParser", TTSParser)
resolve_forward_declaration("TTSTreeCursor", TTSTreeCursor)
