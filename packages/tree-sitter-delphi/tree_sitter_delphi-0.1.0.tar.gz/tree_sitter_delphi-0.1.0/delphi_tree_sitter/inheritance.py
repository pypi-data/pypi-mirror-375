"""
Inheritance and visibility system matching Delphi patterns.

This module provides proper inheritance hierarchies, scope management,
and visibility controls that match the Delphi tree-sitter implementation.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Callable, Type, TypeVar, Generic
from .class_structure import TTSBaseClass, TTSNode, TTSQuery, TTSQueryCursor, TTSTree, TTSParser
from .types import Point, Range, Input, InputEncoding, SymbolType, Quantifier, QueryError
from .exceptions import TreeSitterException

# Type variables for generic inheritance
T = TypeVar('T')
TNode = TypeVar('TNode', bound='TTSNode')
TTree = TypeVar('TTree', bound='TTSTree')
TParser = TypeVar('TParser', bound='TTSParser')
TQuery = TypeVar('TQuery', bound='TTSQuery')
TCursor = TypeVar('TCursor', bound='TTSQueryCursor')


class TTSComponent(ABC):
    """
    Abstract base component class (matching Delphi component patterns).
    
    This provides the base functionality for all tree-sitter components
    with proper inheritance and visibility.
    """
    
    def __init__(self):
        """Initialize the component."""
        self._owner: Optional['TTSComponent'] = None
        self._components: List['TTSComponent'] = []
        self._initialized = False
        self._destroyed = False
    
    # Protected methods (matching Delphi protected section)
    def _set_owner(self, owner: 'TTSComponent'):
        """Set the owner component (protected method)."""
        self._owner = owner
    
    def _add_component(self, component: 'TTSComponent'):
        """Add a child component (protected method)."""
        if component not in self._components:
            self._components.append(component)
            component._set_owner(self)
    
    def _remove_component(self, component: 'TTSComponent'):
        """Remove a child component (protected method)."""
        if component in self._components:
            self._components.remove(component)
            component._set_owner(None)
    
    def _initialize_component(self):
        """Initialize the component (protected method)."""
        if not self._initialized:
            self._initialized = True
    
    def _destroy_component(self):
        """Destroy the component (protected method)."""
        if not self._destroyed:
            # Destroy child components first
            for component in self._components[:]:
                component._destroy_component()
            self._components.clear()
            self._destroyed = True
    
    # Public methods (matching Delphi public section)
    def get_owner(self) -> Optional['TTSComponent']:
        """Get the owner component (public method)."""
        return self._owner
    
    def get_components(self) -> List['TTSComponent']:
        """Get child components (public method)."""
        return self._components.copy()
    
    def is_initialized(self) -> bool:
        """Check if component is initialized (public method)."""
        return self._initialized
    
    def is_destroyed(self) -> bool:
        """Check if component is destroyed (public method)."""
        return self._destroyed
    
    def __del__(self):
        """Destructor (matching Delphi destructor pattern)."""
        if not self._destroyed:
            self._destroy_component()


class TTSNodeComponent(TTSComponent):
    """
    Node component class (matching Delphi node component patterns).
    
    This provides node-specific functionality with proper inheritance.
    """
    
    def __init__(self, node: Optional[TTSNode] = None):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            node: Optional node to wrap
        """
        super().__init__()
        self._node: Optional[TTSNode] = node
        self._initialize_component()
    
    # Protected methods (matching Delphi protected section)
    def _get_node(self) -> Optional[TTSNode]:
        """Get the wrapped node (protected method)."""
        return self._node
    
    def _set_node(self, node: TTSNode):
        """Set the wrapped node (protected method)."""
        self._node = node
    
    # Public methods (matching Delphi public section)
    def get_node(self) -> Optional[TTSNode]:
        """Get the wrapped node (public method)."""
        return self._get_node()
    
    def set_node(self, node: TTSNode):
        """Set the wrapped node (public method)."""
        self._set_node(node)
    
    def has_node(self) -> bool:
        """Check if component has a node (public method)."""
        return self._node is not None


class TTSTreeViewNode(TTSNodeComponent):
    """
    Tree view node class (matching Delphi TTSTreeViewNode inheritance).
    
    This class inherits from TTreeNode in Delphi, providing tree view
    functionality with proper inheritance and visibility.
    """
    
    def __init__(self, node: Optional[TTSNode] = None, text: str = ""):
        """
        Constructor (matching Delphi constructor pattern).
        
        Args:
            node: Optional node to wrap
            text: Display text for the tree view
        """
        super().__init__(node)
        self._text = text
        self._has_children = False
        self._expanded = False
        self._selected = False
    
    # Protected methods (matching Delphi protected section)
    def _get_text(self) -> str:
        """Get display text (protected method)."""
        return self._text
    
    def _set_text(self, text: str):
        """Set display text (protected method)."""
        self._text = text
    
    def _get_has_children(self) -> bool:
        """Get has children flag (protected method)."""
        return self._has_children
    
    def _set_has_children(self, has_children: bool):
        """Set has children flag (protected method)."""
        self._has_children = has_children
    
    def _get_expanded(self) -> bool:
        """Get expanded flag (protected method)."""
        return self._expanded
    
    def _set_expanded(self, expanded: bool):
        """Set expanded flag (protected method)."""
        self._expanded = expanded
    
    def _get_selected(self) -> bool:
        """Get selected flag (protected method)."""
        return self._selected
    
    def _set_selected(self, selected: bool):
        """Set selected flag (protected method)."""
        self._selected = selected
    
    # Public methods (matching Delphi public section)
    def get_text(self) -> str:
        """Get display text (public method)."""
        return self._get_text()
    
    def set_text(self, text: str):
        """Set display text (public method)."""
        self._set_text(text)
    
    def has_children(self) -> bool:
        """Check if node has children (public method)."""
        return self._get_has_children()
    
    def set_has_children(self, has_children: bool):
        """Set has children flag (public method)."""
        self._set_has_children(has_children)
    
    def is_expanded(self) -> bool:
        """Check if node is expanded (public method)."""
        return self._get_expanded()
    
    def set_expanded(self, expanded: bool):
        """Set expanded flag (public method)."""
        self._set_expanded(expanded)
    
    def is_selected(self) -> bool:
        """Check if node is selected (public method)."""
        return self._get_selected()
    
    def set_selected(self, selected: bool):
        """Set selected flag (public method)."""
        self._set_selected(selected)
    
    def update_from_node(self):
        """Update properties from the wrapped node (public method)."""
        if self._node is not None:
            # Update text from node type
            self._text = self._node.type if hasattr(self._node, 'type') else "Unknown"
            # Update has children from node
            self._has_children = (self._node.child_count() > 0 if hasattr(self._node, 'child_count') else False)


class TTSForm(TTSComponent):
    """
    Form class (matching Delphi TForm inheritance).
    
    This class provides form functionality with proper inheritance
    and visibility matching the Delphi implementation.
    """
    
    def __init__(self):
        """Constructor (matching Delphi constructor pattern)."""
        super().__init__()
        self._caption = ""
        self._visible = False
        self._enabled = True
        self._modal_result = None
        self._on_create: Optional[Callable] = None
        self._on_destroy: Optional[Callable] = None
        self._on_show: Optional[Callable] = None
        self._on_hide: Optional[Callable] = None
    
    # Protected methods (matching Delphi protected section)
    def _get_caption(self) -> str:
        """Get form caption (protected method)."""
        return self._caption
    
    def _set_caption(self, caption: str):
        """Set form caption (protected method)."""
        self._caption = caption
    
    def _get_visible(self) -> bool:
        """Get visible flag (protected method)."""
        return self._visible
    
    def _set_visible(self, visible: bool):
        """Set visible flag (protected method)."""
        self._visible = visible
    
    def _get_enabled(self) -> bool:
        """Get enabled flag (protected method)."""
        return self._enabled
    
    def _set_enabled(self, enabled: bool):
        """Set enabled flag (protected method)."""
        self._enabled = enabled
    
    def _get_modal_result(self) -> Optional[int]:
        """Get modal result (protected method)."""
        return self._modal_result
    
    def _set_modal_result(self, result: Optional[int]):
        """Set modal result (protected method)."""
        self._modal_result = result
    
    # Public methods (matching Delphi public section)
    def get_caption(self) -> str:
        """Get form caption (public method)."""
        return self._get_caption()
    
    def set_caption(self, caption: str):
        """Set form caption (public method)."""
        self._set_caption(caption)
    
    def is_visible(self) -> bool:
        """Check if form is visible (public method)."""
        return self._get_visible()
    
    def set_visible(self, visible: bool):
        """Set visible flag (public method)."""
        self._set_visible(visible)
    
    def is_enabled(self) -> bool:
        """Check if form is enabled (public method)."""
        return self._get_enabled()
    
    def set_enabled(self, enabled: bool):
        """Set enabled flag (public method)."""
        self._set_enabled(enabled)
    
    def get_modal_result(self) -> Optional[int]:
        """Get modal result (public method)."""
        return self._get_modal_result()
    
    def set_modal_result(self, result: Optional[int]):
        """Set modal result (public method)."""
        self._set_modal_result(result)
    
    def show(self):
        """Show the form (public method)."""
        self._set_visible(True)
        if self._on_show:
            self._on_show()
    
    def hide(self):
        """Hide the form (public method)."""
        self._set_visible(False)
        if self._on_hide:
            self._on_hide()
    
    def close(self):
        """Close the form (public method)."""
        self.hide()
        self._destroy_component()
    
    # Event handlers (matching Delphi event pattern)
    def set_on_create(self, handler: Callable):
        """Set on create event handler (public method)."""
        self._on_create = handler
    
    def set_on_destroy(self, handler: Callable):
        """Set on destroy event handler (public method)."""
        self._on_destroy = handler
    
    def set_on_show(self, handler: Callable):
        """Set on show event handler (public method)."""
        self._on_show = handler
    
    def set_on_hide(self, handler: Callable):
        """Set on hide event handler (public method)."""
        self._on_hide = handler
    
    def _destroy_component(self):
        """Destroy the form (protected method)."""
        if self._on_destroy:
            self._on_destroy()
        super()._destroy_component()


class TDTSMainForm(TTSForm):
    """
    Main form class (matching Delphi TDTSMainForm inheritance).
    
    This class inherits from TForm in Delphi, providing the main
    form functionality with proper inheritance and visibility.
    """
    
    def __init__(self):
        """Constructor (matching Delphi constructor pattern)."""
        super().__init__()
        self._parser: Optional[TTSParser] = None
        self._tree: Optional[TTSTree] = None
        self._edit_changed = False
        self._named_nodes_only = False
        self._selected_node: Optional[TTSNode] = None
        self._components: Dict[str, Any] = {}
        self._initialize_form()
    
    def _initialize_form(self):
        """Initialize the form (protected method)."""
        self._caption = "Tree Sitter Demo"
        self._create_parser()
        self._setup_components()
        self._setup_event_handlers()
    
    def _create_parser(self):
        """Create the parser (protected method)."""
        self._parser = TTSParser()
        self._add_component(self._parser)
    
    def _setup_components(self):
        """Setup form components (protected method)."""
        # This would setup all the form components
        # For now, just initialize the components dictionary
        self._components = {
            'memCode': None,
            'treeView': None,
            'sgNodeProps': None,
            'cbCode': None,
            'cbFields': None,
            'btnLoad': None,
            'btnLangInfo': None,
            'btnQuery': None,
        }
    
    def _setup_event_handlers(self):
        """Setup event handlers (protected method)."""
        # This would setup all the event handlers
        pass
    
    # Protected methods (matching Delphi protected section)
    def _get_parser(self) -> Optional[TTSParser]:
        """Get the parser (protected method)."""
        return self._parser
    
    def _get_tree(self) -> Optional[TTSTree]:
        """Get the tree (protected method)."""
        return self._tree
    
    def _set_tree(self, tree: TTSTree):
        """Set the tree (protected method)."""
        self._tree = tree
    
    def _get_edit_changed(self) -> bool:
        """Get edit changed flag (protected method)."""
        return self._edit_changed
    
    def _set_edit_changed(self, changed: bool):
        """Set edit changed flag (protected method)."""
        self._edit_changed = changed
    
    def _get_named_nodes_only(self) -> bool:
        """Get named nodes only flag (protected method)."""
        return self._named_nodes_only
    
    def _set_named_nodes_only(self, named_only: bool):
        """Set named nodes only flag (protected method)."""
        self._named_nodes_only = named_only
    
    def _get_selected_node(self) -> Optional[TTSNode]:
        """Get selected node (protected method)."""
        return self._selected_node
    
    def _set_selected_node(self, node: TTSNode):
        """Set selected node (protected method)."""
        self._selected_node = node
    
    # Public methods (matching Delphi public section)
    def get_parser(self) -> Optional[TTSParser]:
        """Get the parser (public method)."""
        return self._get_parser()
    
    def get_tree(self) -> Optional[TTSTree]:
        """Get the tree (public method)."""
        return self._get_tree()
    
    def set_tree(self, tree: TTSTree):
        """Set the tree (public method)."""
        self._set_tree(tree)
    
    def is_edit_changed(self) -> bool:
        """Check if edit has changed (public method)."""
        return self._get_edit_changed()
    
    def set_edit_changed(self, changed: bool):
        """Set edit changed flag (public method)."""
        self._set_edit_changed(changed)
    
    def is_named_nodes_only(self) -> bool:
        """Check if named nodes only is enabled (public method)."""
        return self._get_named_nodes_only()
    
    def set_named_nodes_only(self, named_only: bool):
        """Set named nodes only flag (public method)."""
        self._set_named_nodes_only(named_only)
    
    def get_selected_node(self) -> Optional[TTSNode]:
        """Get selected node (public method)."""
        return self._get_selected_node()
    
    def set_selected_node(self, node: TTSNode):
        """Set selected node (public method)."""
        self._set_selected_node(node)
    
    def parse_content(self):
        """Parse content (public method)."""
        # Implementation would parse the content
        pass
    
    def load_language_parser(self, language_name: str):
        """Load language parser (public method)."""
        # Implementation would load the language parser
        pass
    
    def load_language_fields(self):
        """Load language fields (public method)."""
        # Implementation would load the language fields
        pass
    
    def fill_node_props(self, node: TTSNode):
        """Fill node properties (public method)."""
        # Implementation would fill the node properties
        pass
    
    def clear_node_props(self):
        """Clear node properties (public method)."""
        # Implementation would clear the node properties
        pass
    
    def setup_tree_node(self, tree_node: TTSTreeViewNode, ts_node: TTSNode):
        """Setup tree node (public method)."""
        # Implementation would setup the tree node
        pass


class TDTSLanguageForm(TTSForm):
    """
    Language form class (matching Delphi TDTSLanguageForm inheritance).
    
    This class inherits from TForm in Delphi, providing language
    information form functionality.
    """
    
    def __init__(self):
        """Constructor (matching Delphi constructor pattern)."""
        super().__init__()
        self._language: Optional[Any] = None
        self._caption = "Language Information"
        self._initialize_form()
    
    def _initialize_form(self):
        """Initialize the form (protected method)."""
        self._setup_components()
        self._setup_event_handlers()
    
    def _setup_components(self):
        """Setup form components (protected method)."""
        # This would setup all the form components
        pass
    
    def _setup_event_handlers(self):
        """Setup event handlers (protected method)."""
        # This would setup all the event handlers
        pass
    
    # Protected methods (matching Delphi protected section)
    def _get_language(self) -> Optional[Any]:
        """Get the language (protected method)."""
        return self._language
    
    def _set_language(self, language: Any):
        """Set the language (protected method)."""
        self._language = language
    
    # Public methods (matching Delphi public section)
    def get_language(self) -> Optional[Any]:
        """Get the language (public method)."""
        return self._get_language()
    
    def set_language(self, language: Any):
        """Set the language (public method)."""
        self._set_language(language)
    
    def update_language(self):
        """Update language information (public method)."""
        # Implementation would update the language information
        pass


class TDTSQueryForm(TTSForm):
    """
    Query form class (matching Delphi TDTSQueryForm inheritance).
    
    This class inherits from TForm in Delphi, providing query
    form functionality.
    """
    
    def __init__(self):
        """Constructor (matching Delphi constructor pattern)."""
        super().__init__()
        self._tree: Optional[TTSTree] = None
        self._query: Optional[TTSQuery] = None
        self._query_cursor: Optional[TTSQueryCursor] = None
        self._current_match: Optional[Any] = None
        self._caption = "Query Form"
        self._initialize_form()
    
    def _initialize_form(self):
        """Initialize the form (protected method)."""
        self._setup_components()
        self._setup_event_handlers()
    
    def _setup_components(self):
        """Setup form components (protected method)."""
        # This would setup all the form components
        pass
    
    def _setup_event_handlers(self):
        """Setup event handlers (protected method)."""
        # This would setup all the event handlers
        pass
    
    # Protected methods (matching Delphi protected section)
    def _get_tree(self) -> Optional[TTSTree]:
        """Get the tree (protected method)."""
        return self._tree
    
    def _set_tree(self, tree: TTSTree):
        """Set the tree (protected method)."""
        self._tree = tree
    
    def _get_query(self) -> Optional[TTSQuery]:
        """Get the query (protected method)."""
        return self._query
    
    def _set_query(self, query: TTSQuery):
        """Set the query (protected method)."""
        self._query = query
    
    def _get_query_cursor(self) -> Optional[TTSQueryCursor]:
        """Get the query cursor (protected method)."""
        return self._query_cursor
    
    def _set_query_cursor(self, cursor: TTSQueryCursor):
        """Set the query cursor (protected method)."""
        self._query_cursor = cursor
    
    def _get_current_match(self) -> Optional[Any]:
        """Get the current match (protected method)."""
        return self._current_match
    
    def _set_current_match(self, match: Any):
        """Set the current match (protected method)."""
        self._current_match = match
    
    # Public methods (matching Delphi public section)
    def get_tree(self) -> Optional[TTSTree]:
        """Get the tree (public method)."""
        return self._get_tree()
    
    def set_tree(self, tree: TTSTree):
        """Set the tree (public method)."""
        self._set_tree(tree)
    
    def get_query(self) -> Optional[TTSQuery]:
        """Get the query (public method)."""
        return self._get_query()
    
    def set_query(self, query: TTSQuery):
        """Set the query (public method)."""
        self._set_query(query)
    
    def get_query_cursor(self) -> Optional[TTSQueryCursor]:
        """Get the query cursor (public method)."""
        return self._get_query_cursor()
    
    def set_query_cursor(self, cursor: TTSQueryCursor):
        """Set the query cursor (public method)."""
        self._set_query_cursor(cursor)
    
    def get_current_match(self) -> Optional[Any]:
        """Get the current match (public method)."""
        return self._get_current_match()
    
    def set_current_match(self, match: Any):
        """Set the current match (public method)."""
        self._set_current_match(match)
    
    def clear_query(self):
        """Clear the query (public method)."""
        # Implementation would clear the query
        pass
    
    def clear_matches(self):
        """Clear matches (public method)."""
        # Implementation would clear the matches
        pass
    
    def clear_predicates(self):
        """Clear predicates (public method)."""
        # Implementation would clear the predicates
        pass
    
    def tree_deleted(self):
        """Handle tree deletion (public method)."""
        # Implementation would handle tree deletion
        pass
    
    def new_tree_generated(self, tree: TTSTree):
        """Handle new tree generation (public method)."""
        # Implementation would handle new tree generation
        pass


# Global form instances (matching Delphi global variables)
DTSMainForm: Optional[TDTSMainForm] = None
DTSLanguageForm: Optional[TDTSLanguageForm] = None
DTSQueryForm: Optional[TDTSQueryForm] = None


def show_language_info(language: Any):
    """
    Show language info form (matching Delphi procedure).
    
    Args:
        language: The language to show info for
    """
    global DTSLanguageForm
    
    if DTSLanguageForm is None:
        DTSLanguageForm = TDTSLanguageForm()
    
    DTSLanguageForm.set_language(language)
    DTSLanguageForm.update_language()
    DTSLanguageForm.show()


def show_query_form(tree: TTSTree):
    """
    Show query form (matching Delphi procedure).
    
    Args:
        tree: The tree to query against
    """
    global DTSQueryForm
    
    if DTSQueryForm is None:
        DTSQueryForm = TDTSQueryForm()
    
    DTSQueryForm.set_tree(tree)
    DTSQueryForm.show()


def create_main_form() -> TDTSMainForm:
    """
    Create main form (matching Delphi procedure).
    
    Returns:
        The created main form
    """
    global DTSMainForm
    
    if DTSMainForm is None:
        DTSMainForm = TDTSMainForm()
    
    return DTSMainForm
