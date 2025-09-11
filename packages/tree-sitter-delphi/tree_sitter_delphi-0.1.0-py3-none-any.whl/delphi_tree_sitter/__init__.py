"""
Delphi Tree Sitter Python Library

A Python library for working with tree-sitter parsers, providing
bindings and utilities for parsing and analyzing code with tree-sitter.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .parser import Parser
from .tree import Tree, Node, TreeCursor, InputEdit
from .language import Language
from .query import Query, QueryCursor, QueryMatch, QueryCapture, QueryPredicateStep
from .types import Point, Range, Input, InputEncoding, SymbolType, Quantifier, QueryError
from .exceptions import TreeSitterException, TreeSitterParseError, TreeSitterQueryError, TreeSitterLanguageError, TreeSitterLibraryError
from .lookahead import LookAheadIterator
from .wasm import WasmEngine, WasmStore, WasmParser, WasmError, WasmErrorKind
from .utils import Logger, Allocator, TreeSitterConfig, TreeWalker, QueryBuilder, create_input_from_string, create_input_from_file, create_input_from_callback, point_to_string, range_to_string, create_range, create_point
from .helpers import NodePropertyHelper, LanguageInfoHelper, QueryHelper, QueryMatchHelper, TreeNavigationHelper, FieldHelper, ValidationHelper, ConditionalLogicHelper
from .demo_utils import TreeViewHelper, CodeSelectionHelper, LanguageLoaderHelper, QueryFormHelper, PropertyGridHelper, ErrorHandler, DemoStateManager
from .validation import NodeValidator, QueryValidator, LanguageValidator, ConditionalLogic
from .class_structure import (
    TTSLanguageHelper, TTSQueryMatchHelper, TTSNodeHelper, TTSPointHelper,
    TTSBaseClass, TTSParser, TTSTree, TTSTreeCursor, TTSQuery, TTSQueryCursor,
    TTSNode, TTSPoint, TTSInputEncoding, TTSQueryError, TTSQuantifier,
    TTSQueryPredicateStep, TTSQueryPredicateStepType, TTSQueryPredicateStepArray,
    TTSQueryCapture, TTSQueryCaptureArray, TTSQueryMatch, PTSGetLanguageFunc,
    TTSParseReadFunction
)
from .inheritance import (
    TTSComponent, TTSNodeComponent, TTSTreeViewNode, TTSForm, TDTSMainForm,
    TDTSLanguageForm, TDTSQueryForm, show_language_info, show_query_form, create_main_form
)
from .forward_declarations import (
    TTSForwardDeclaration, TTSMutuallyDependent, FORWARD_DECLARATIONS,
    register_forward_declaration, resolve_forward_declaration, get_forward_declaration
)

__all__ = [
    # Core classes
    "Parser",
    "Tree", 
    "Node",
    "TreeCursor",
    "Language",
    "Query",
    "QueryCursor",
    "QueryMatch",
    "QueryCapture",
    "QueryPredicateStep",
    
    # Types and enums
    "Point",
    "Range",
    "Input",
    "InputEncoding",
    "SymbolType",
    "Quantifier",
    "QueryError",
    "InputEdit",
    
    # Exceptions
    "TreeSitterException",
    "TreeSitterParseError",
    "TreeSitterQueryError",
    "TreeSitterLanguageError",
    "TreeSitterLibraryError",
    
    # Advanced features
    "LookAheadIterator",
    "WasmEngine",
    "WasmStore",
    "WasmParser",
    "WasmError",
    "WasmErrorKind",
    
    # Utilities
    "Logger",
    "Allocator",
    "TreeSitterConfig",
    "TreeWalker",
    "QueryBuilder",
    
    # Utility functions
    "create_input_from_string",
    "create_input_from_file",
    "create_input_from_callback",
    "point_to_string",
    "range_to_string",
    "create_range",
    "create_point",
    
    # Helper classes
    "NodePropertyHelper",
    "LanguageInfoHelper",
    "QueryHelper",
    "QueryMatchHelper",
    "TreeNavigationHelper",
    "FieldHelper",
    "ValidationHelper",
    "ConditionalLogicHelper",
    
    # Demo utilities
    "TreeViewHelper",
    "CodeSelectionHelper",
    "LanguageLoaderHelper",
    "QueryFormHelper",
    "PropertyGridHelper",
    "ErrorHandler",
    "DemoStateManager",
    
    # Validation classes
    "NodeValidator",
    "QueryValidator",
    "LanguageValidator",
    "ConditionalLogic",
    
    # Class structure classes
    "TTSLanguageHelper",
    "TTSQueryMatchHelper",
    "TTSNodeHelper",
    "TTSPointHelper",
    "TTSBaseClass",
    "TTSParser",
    "TTSTree",
    "TTSTreeCursor",
    "TTSQuery",
    "TTSQueryCursor",
    "TTSNode",
    "TTSPoint",
    "TTSInputEncoding",
    "TTSQueryError",
    "TTSQuantifier",
    "TTSQueryPredicateStep",
    "TTSQueryPredicateStepType",
    "TTSQueryPredicateStepArray",
    "TTSQueryCapture",
    "TTSQueryCaptureArray",
    "TTSQueryMatch",
    "PTSGetLanguageFunc",
    "TTSParseReadFunction",
    
    # Inheritance classes
    "TTSComponent",
    "TTSNodeComponent",
    "TTSTreeViewNode",
    "TTSForm",
    "TDTSMainForm",
    "TDTSLanguageForm",
    "TDTSQueryForm",
    "show_language_info",
    "show_query_form",
    "create_main_form",
    
    # Forward declaration classes
    "TTSForwardDeclaration",
    "TTSMutuallyDependent",
    "FORWARD_DECLARATIONS",
    "register_forward_declaration",
    "resolve_forward_declaration",
    "get_forward_declaration",
]
