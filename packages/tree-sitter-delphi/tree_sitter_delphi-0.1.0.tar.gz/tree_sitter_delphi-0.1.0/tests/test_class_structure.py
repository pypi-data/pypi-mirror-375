"""
Tests for class structure, inheritance, and forward declarations.
"""

import pytest
from delphi_tree_sitter import (
    TTSLanguageHelper, TTSQueryMatchHelper, TTSNodeHelper, TTSPointHelper,
    TTSBaseClass, TTSParser, TTSTree, TTSTreeCursor, TTSQuery, TTSQueryCursor,
    TTSNode, TTSPoint, TTSInputEncoding, TTSQueryError, TTSQuantifier,
    TTSQueryPredicateStep, TTSQueryPredicateStepType, TTSQueryPredicateStepArray,
    TTSQueryCapture, TTSQueryCaptureArray, TTSQueryMatch, PTSGetLanguageFunc,
    TTSParseReadFunction,
    TTSComponent, TTSNodeComponent, TTSTreeViewNode, TTSForm, TDTSMainForm,
    TDTSLanguageForm, TDTSQueryForm, show_language_info, show_query_form, create_main_form,
    TTSForwardDeclaration, TTSMutuallyDependent, FORWARD_DECLARATIONS,
    register_forward_declaration, resolve_forward_declaration, get_forward_declaration
)


class TestTTSLanguageHelper:
    """Test cases for TTSLanguageHelper."""
    
    def test_language_helper_initialization(self):
        """Test that TTSLanguageHelper can be initialized."""
        language = None  # Placeholder
        helper = TTSLanguageHelper(language)
        assert helper._language == language
    
    def test_language_helper_methods(self):
        """Test TTSLanguageHelper methods."""
        language = None  # Placeholder
        helper = TTSLanguageHelper(language)
        
        # Test public methods
        assert isinstance(helper.version(), int)
        assert isinstance(helper.field_count(), int)
        assert isinstance(helper.symbol_count(), int)
        assert isinstance(helper.next_state(0, 0), int)
        
        # Test properties
        assert isinstance(helper.field_name, dict)
        assert isinstance(helper.field_id, dict)
        assert isinstance(helper.symbol_name, dict)
        assert isinstance(helper.symbol_for_name, dict)
        assert isinstance(helper.symbol_type, dict)


class TestTTSQueryMatchHelper:
    """Test cases for TTSQueryMatchHelper."""
    
    def test_query_match_helper_initialization(self):
        """Test that TTSQueryMatchHelper can be initialized."""
        match = None  # Placeholder
        helper = TTSQueryMatchHelper(match)
        assert helper._match == match
    
    def test_query_match_helper_methods(self):
        """Test TTSQueryMatchHelper methods."""
        match = None  # Placeholder
        helper = TTSQueryMatchHelper(match)
        
        captures = helper.captures_array()
        assert isinstance(captures, list)


class TestTTSNodeHelper:
    """Test cases for TTSNodeHelper."""
    
    def test_node_helper_initialization(self):
        """Test that TTSNodeHelper can be initialized."""
        node = None  # Placeholder
        helper = TTSNodeHelper(node)
        assert helper._node == node
    
    def test_node_helper_methods(self):
        """Test TTSNodeHelper methods."""
        node = None  # Placeholder
        helper = TTSNodeHelper(node)
        
        # Test basic methods
        assert isinstance(helper.language(), type(None))
        assert isinstance(helper.node_type(), str)
        assert isinstance(helper.symbol(), int)
        assert isinstance(helper.grammar_type(), str)
        assert isinstance(helper.grammar_symbol(), int)
        
        # Test boolean methods
        assert isinstance(helper.is_null(), bool)
        assert isinstance(helper.is_error(), bool)
        assert isinstance(helper.has_error(), bool)
        assert isinstance(helper.has_changes(), bool)
        assert isinstance(helper.is_extra(), bool)
        assert isinstance(helper.is_missing(), bool)
        assert isinstance(helper.is_named(), bool)
        
        # Test navigation methods
        assert isinstance(helper.parent(), type(None))
        assert isinstance(helper.child(0), type(None))
        assert isinstance(helper.child_count(), int)
        assert isinstance(helper.named_child(0), type(None))
        assert isinstance(helper.named_child_count(), int)
        assert isinstance(helper.next_sibling(), type(None))
        assert isinstance(helper.prev_sibling(), type(None))
        assert isinstance(helper.next_named_sibling(), type(None))
        assert isinstance(helper.prev_named_sibling(), type(None))
        
        # Test position methods
        assert isinstance(helper.start_byte(), int)
        assert isinstance(helper.start_point(), type(None))
        assert isinstance(helper.end_byte(), int)
        assert isinstance(helper.end_point(), type(None))
        
        # Test field methods
        assert isinstance(helper.child_by_field("test"), type(None))
        assert isinstance(helper.child_by_field_id(0), type(None))
        assert isinstance(helper.field_name_for_child(0), type(None))
        
        # Test other methods
        assert isinstance(helper.descendant_count(), int)
        assert isinstance(helper.to_string(), str)


class TestTTSPointHelper:
    """Test cases for TTSPointHelper."""
    
    def test_point_helper_initialization(self):
        """Test that TTSPointHelper can be initialized."""
        point = None  # Placeholder
        helper = TTSPointHelper(point)
        assert helper._point == point
    
    def test_point_helper_methods(self):
        """Test TTSPointHelper methods."""
        point = None  # Placeholder
        helper = TTSPointHelper(point)
        
        text = helper.to_string()
        assert isinstance(text, str)


class TestTTSBaseClass:
    """Test cases for TTSBaseClass."""
    
    def test_base_class_initialization(self):
        """Test that TTSBaseClass can be initialized."""
        # TTSBaseClass is abstract, so we can't instantiate it directly
        # But we can test its functionality through subclasses
        pass
    
    def test_base_class_methods(self):
        """Test TTSBaseClass methods through subclasses."""
        # Test through TTSParser which inherits from TTSBaseClass
        parser = TTSParser()
        assert isinstance(parser.is_initialized(), bool)
        assert isinstance(parser.is_destroyed(), bool)
        
        # Test destructor
        parser.destroy()
        assert parser.is_destroyed() is True


class TestTTSParser:
    """Test cases for TTSParser."""
    
    def test_parser_initialization(self):
        """Test that TTSParser can be initialized."""
        parser = TTSParser()
        assert parser is not None
        assert parser.is_initialized() is True
        assert parser.is_destroyed() is False
    
    def test_parser_methods(self):
        """Test TTSParser methods."""
        parser = TTSParser()
        
        # Test basic methods
        parser.reset()
        assert parser.get_timeout_micros() == 0
        assert parser.get_cancellation_flag() is None
        assert parser.get_logger() is None
        assert isinstance(parser.get_included_ranges(), list)
        
        # Test property access
        assert parser.language is None
        parser.language = None  # Test setter
        
        # Test parsing methods
        tree = parser.parse_string("test code")
        assert isinstance(tree, TTSTree)
        
        tree2 = parser.parse_string_encoding("test code", TTSInputEncoding.UTF8)
        assert isinstance(tree2, TTSTree)
        
        # Test other methods
        parser.set_timeout_micros(1000)
        assert parser.get_timeout_micros() == 1000
        
        parser.set_cancellation_flag(True)
        assert parser.get_cancellation_flag() is True
        
        parser.set_logger(None)
        assert parser.get_logger() is None
        
        parser.set_included_ranges([])
        assert isinstance(parser.get_included_ranges(), list)
        
        parser.print_dot_graphs(True)
    
    def test_parser_destructor(self):
        """Test TTSParser destructor."""
        parser = TTSParser()
        parser.destroy()
        assert parser.is_destroyed() is True


class TestTTSTree:
    """Test cases for TTSTree."""
    
    def test_tree_initialization(self):
        """Test that TTSTree can be initialized."""
        tree = TTSTree(None, "test code", None)
        assert tree is not None
        assert tree.is_initialized() is True
        assert tree.is_destroyed() is False
    
    def test_tree_methods(self):
        """Test TTSTree methods."""
        tree = TTSTree(None, "test code", None)
        
        # Test basic methods
        assert isinstance(tree.language(), type(None))
        assert isinstance(tree.root_node, TTSNode)
        assert isinstance(tree.root_node_with_offset(0, None), TTSNode)
        assert isinstance(tree.included_ranges(), list)
        assert isinstance(tree.get_changed_ranges(tree), list)
        
        # Test other methods
        tree.print_dot_graph("test.dot")
        copy = tree.copy()
        assert isinstance(copy, TTSTree)
    
    def test_tree_destructor(self):
        """Test TTSTree destructor."""
        tree = TTSTree(None, "test code", None)
        tree.destroy()
        assert tree.is_destroyed() is True


class TestTTSTreeCursor:
    """Test cases for TTSTreeCursor."""
    
    def test_tree_cursor_initialization(self):
        """Test that TTSTreeCursor can be initialized."""
        node = TTSNode(None, "test code", None)
        cursor = TTSTreeCursor(node)
        assert cursor is not None
        assert cursor.is_initialized() is True
        assert cursor.is_destroyed() is False
    
    def test_tree_cursor_methods(self):
        """Test TTSTreeCursor methods."""
        node = TTSNode(None, "test code", None)
        cursor = TTSTreeCursor(node)
        
        # Test properties
        assert isinstance(cursor.current_node, TTSNode)
        assert isinstance(cursor.current_field_name, str)
        assert isinstance(cursor.current_field_id, int)
        assert isinstance(cursor.current_depth, int)
        assert isinstance(cursor.current_descendant_index, int)
        
        # Test navigation methods
        assert isinstance(cursor.goto_parent(), bool)
        assert isinstance(cursor.goto_next_sibling(), bool)
        assert isinstance(cursor.goto_prev_sibling(), bool)
        assert isinstance(cursor.goto_first_child(), bool)
        assert isinstance(cursor.goto_last_child(), bool)
        assert isinstance(cursor.goto_first_child_for_byte(0), int)
        assert isinstance(cursor.goto_first_child_for_point(None), int)
        
        # Test other methods
        cursor.reset(node)
        cursor.reset_to(cursor)
        cursor.goto_descendant(0)
        copy = cursor.copy()
        assert isinstance(copy, TTSTreeCursor)
    
    def test_tree_cursor_destructor(self):
        """Test TTSTreeCursor destructor."""
        node = TTSNode(None, "test code", None)
        cursor = TTSTreeCursor(node)
        cursor.destroy()
        assert cursor.is_destroyed() is True


class TestTTSQuery:
    """Test cases for TTSQuery."""
    
    def test_query_initialization(self):
        """Test that TTSQuery can be initialized."""
        query = TTSQuery(None, "test query", 0, TTSQueryError.NONE)
        assert query is not None
        assert query.is_initialized() is True
        assert query.is_destroyed() is False
    
    def test_query_methods(self):
        """Test TTSQuery methods."""
        query = TTSQuery(None, "test query", 0, TTSQueryError.NONE)
        
        # Test basic methods
        assert isinstance(query.pattern_count(), int)
        assert isinstance(query.capture_count(), int)
        assert isinstance(query.string_count(), int)
        assert isinstance(query.start_byte_for_pattern(0), int)
        assert isinstance(query.predicates_for_pattern(0), list)
        assert isinstance(query.capture_name_for_id(0), str)
        assert isinstance(query.string_value_for_id(0), str)
        assert isinstance(query.quantifier_for_capture(0, 0), TTSQuantifier)
        
        # Test property access
        assert query.query is None
    
    def test_query_destructor(self):
        """Test TTSQuery destructor."""
        query = TTSQuery(None, "test query", 0, TTSQueryError.NONE)
        query.destroy()
        assert query.is_destroyed() is True


class TestTTSQueryCursor:
    """Test cases for TTSQueryCursor."""
    
    def test_query_cursor_initialization(self):
        """Test that TTSQueryCursor can be initialized."""
        cursor = TTSQueryCursor()
        assert cursor is not None
        assert cursor.is_initialized() is True
        assert cursor.is_destroyed() is False
    
    def test_query_cursor_methods(self):
        """Test TTSQueryCursor methods."""
        cursor = TTSQueryCursor()
        
        # Test basic methods
        assert isinstance(cursor.did_exceed_match_limit(), bool)
        assert isinstance(cursor.match_limit, int)
        cursor.match_limit = 100
        assert cursor.match_limit == 100
        
        # Test other methods
        cursor.execute(None, None)
        cursor.set_max_start_depth(10)
        assert isinstance(cursor.next_match(None), bool)
        assert isinstance(cursor.next_capture(None, 0), bool)
        
        # Test property access
        assert cursor.query_cursor is None
    
    def test_query_cursor_destructor(self):
        """Test TTSQueryCursor destructor."""
        cursor = TTSQueryCursor()
        cursor.destroy()
        assert cursor.is_destroyed() is True


class TestTTSNode:
    """Test cases for TTSNode."""
    
    def test_node_initialization(self):
        """Test that TTSNode can be initialized."""
        node = TTSNode(None, "test code", None)
        assert node is not None
        assert node.is_initialized() is True
        assert node.is_destroyed() is False
    
    def test_node_properties(self):
        """Test TTSNode properties."""
        node = TTSNode(None, "test code", None)
        
        # Test properties
        assert isinstance(node.type, str)
        assert isinstance(node.symbol, int)
        assert isinstance(node.grammar_type, str)
        assert isinstance(node.grammar_symbol, int)
        assert isinstance(node.start_byte, int)
        assert isinstance(node.end_byte, int)
        assert isinstance(node.start_point, type(None))
        assert isinstance(node.end_point, type(None))
        assert isinstance(node.text, str)
    
    def test_node_methods(self):
        """Test TTSNode methods."""
        node = TTSNode(None, "test code", None)
        
        # Test boolean methods
        assert isinstance(node.is_null(), bool)
        assert isinstance(node.is_named(), bool)
        assert isinstance(node.is_missing(), bool)
        assert isinstance(node.is_extra(), bool)
        assert isinstance(node.has_changes(), bool)
        assert isinstance(node.has_error(), bool)
        assert isinstance(node.is_error(), bool)
        
        # Test navigation methods
        assert isinstance(node.parent(), type(None))
        assert isinstance(node.child(0), type(None))
        assert isinstance(node.child_count(), int)
        assert isinstance(node.named_child(0), type(None))
        assert isinstance(node.named_child_count(), int)
        assert isinstance(node.next_sibling(), type(None))
        assert isinstance(node.prev_sibling(), type(None))
        assert isinstance(node.next_named_sibling(), type(None))
        assert isinstance(node.prev_named_sibling(), type(None))
        
        # Test field methods
        assert isinstance(node.child_by_field_name("test"), type(None))
        assert isinstance(node.child_by_field_id(0), type(None))
        assert isinstance(node.field_name_for_child(0), type(None))
        
        # Test other methods
        assert isinstance(node.descendant_count(), int)
        assert isinstance(node.descendant_for_byte_range(0, 10), type(None))
        assert isinstance(node.descendant_for_point_range(None, None), type(None))
        assert isinstance(node.named_descendant_for_byte_range(0, 10), type(None))
        assert isinstance(node.named_descendant_for_point_range(None, None), type(None))
        assert isinstance(node.edit(None), TTSNode)
        assert isinstance(node.equals(node), bool)
        assert isinstance(node.to_string(), str)
        assert isinstance(node.children(), list)
        assert isinstance(node.named_children(), list)
        assert isinstance(node.walk(), TTSTreeCursor)
        
        # Test string representation
        assert isinstance(str(node), str)
        assert isinstance(node.__eq__(node), bool)
    
    def test_node_mutual_dependencies(self):
        """Test TTSNode mutual dependencies."""
        node = TTSNode(None, "test code", None)
        tree = TTSTree(None, "test code", None)
        parser = TTSParser()
        
        # Test setting dependencies
        node.set_tree(tree)
        assert node.get_tree() == tree
        
        node.set_parser(parser)
        assert node.get_parser() == parser
        
        # Test getting dependencies
        assert isinstance(node.get_dependencies(), list)
        assert isinstance(node.get_resolved_dependency("tree"), TTSTree)
        assert isinstance(node.get_resolved_dependency("parser"), TTSParser)


class TestTTSComponent:
    """Test cases for TTSComponent."""
    
    def test_component_initialization(self):
        """Test that TTSComponent can be initialized."""
        component = TTSComponent()
        assert component is not None
        assert component.is_initialized() is False
        assert component.is_destroyed() is False
    
    def test_component_methods(self):
        """Test TTSComponent methods."""
        component1 = TTSComponent()
        component2 = TTSComponent()
        
        # Test owner management
        assert component1.get_owner() is None
        component1._set_owner(component2)
        assert component1.get_owner() == component2
        
        # Test component management
        assert isinstance(component1.get_components(), list)
        component1._add_component(component2)
        assert component2 in component1.get_components()
        
        component1._remove_component(component2)
        assert component2 not in component1.get_components()
        
        # Test initialization
        component1._initialize_component()
        assert component1.is_initialized() is True
        
        # Test destruction
        component1._destroy_component()
        assert component1.is_destroyed() is True


class TestTTSNodeComponent:
    """Test cases for TTSNodeComponent."""
    
    def test_node_component_initialization(self):
        """Test that TTSNodeComponent can be initialized."""
        node = TTSNode(None, "test code", None)
        component = TTSNodeComponent(node)
        assert component is not None
        assert component.is_initialized() is True
        assert component.get_node() == node
        assert component.has_node() is True
    
    def test_node_component_methods(self):
        """Test TTSNodeComponent methods."""
        node = TTSNode(None, "test code", None)
        component = TTSNodeComponent(node)
        
        # Test node management
        assert component.get_node() == node
        assert component.has_node() is True
        
        new_node = TTSNode(None, "new code", None)
        component.set_node(new_node)
        assert component.get_node() == new_node


class TestTTSTreeViewNode:
    """Test cases for TTSTreeViewNode."""
    
    def test_tree_view_node_initialization(self):
        """Test that TTSTreeViewNode can be initialized."""
        node = TTSNode(None, "test code", None)
        tree_node = TTSTreeViewNode(node, "test text")
        assert tree_node is not None
        assert tree_node.is_initialized() is True
        assert tree_node.get_node() == node
        assert tree_node.get_text() == "test text"
    
    def test_tree_view_node_methods(self):
        """Test TTSTreeViewNode methods."""
        node = TTSNode(None, "test code", None)
        tree_node = TTSTreeViewNode(node, "test text")
        
        # Test text management
        assert tree_node.get_text() == "test text"
        tree_node.set_text("new text")
        assert tree_node.get_text() == "new text"
        
        # Test children management
        assert isinstance(tree_node.has_children(), bool)
        tree_node.set_has_children(True)
        assert tree_node.has_children() is True
        
        # Test expansion management
        assert isinstance(tree_node.is_expanded(), bool)
        tree_node.set_expanded(True)
        assert tree_node.is_expanded() is True
        
        # Test selection management
        assert isinstance(tree_node.is_selected(), bool)
        tree_node.set_selected(True)
        assert tree_node.is_selected() is True
        
        # Test update from node
        tree_node.update_from_node()


class TestTTSForm:
    """Test cases for TTSForm."""
    
    def test_form_initialization(self):
        """Test that TTSForm can be initialized."""
        form = TTSForm()
        assert form is not None
        assert form.is_initialized() is False
        assert form.is_destroyed() is False
    
    def test_form_methods(self):
        """Test TTSForm methods."""
        form = TTSForm()
        
        # Test caption management
        assert isinstance(form.get_caption(), str)
        form.set_caption("Test Form")
        assert form.get_caption() == "Test Form"
        
        # Test visibility management
        assert isinstance(form.is_visible(), bool)
        form.set_visible(True)
        assert form.is_visible() is True
        
        # Test enabled management
        assert isinstance(form.is_enabled(), bool)
        form.set_enabled(False)
        assert form.is_enabled() is False
        
        # Test modal result management
        assert form.get_modal_result() is None
        form.set_modal_result(1)
        assert form.get_modal_result() == 1
        
        # Test show/hide
        form.show()
        assert form.is_visible() is True
        
        form.hide()
        assert form.is_visible() is False
        
        # Test event handlers
        def test_handler():
            pass
        
        form.set_on_create(test_handler)
        form.set_on_destroy(test_handler)
        form.set_on_show(test_handler)
        form.set_on_hide(test_handler)
        
        # Test close
        form.close()
        assert form.is_destroyed() is True


class TestTDTSMainForm:
    """Test cases for TDTSMainForm."""
    
    def test_main_form_initialization(self):
        """Test that TDTSMainForm can be initialized."""
        form = TDTSMainForm()
        assert form is not None
        assert form.is_initialized() is False
        assert form.is_destroyed() is False
    
    def test_main_form_methods(self):
        """Test TDTSMainForm methods."""
        form = TDTSMainForm()
        
        # Test parser management
        assert isinstance(form.get_parser(), TTSParser)
        
        # Test tree management
        assert form.get_tree() is None
        tree = TTSTree(None, "test code", None)
        form.set_tree(tree)
        assert form.get_tree() == tree
        
        # Test edit changed management
        assert isinstance(form.is_edit_changed(), bool)
        form.set_edit_changed(True)
        assert form.is_edit_changed() is True
        
        # Test named nodes only management
        assert isinstance(form.is_named_nodes_only(), bool)
        form.set_named_nodes_only(True)
        assert form.is_named_nodes_only() is True
        
        # Test selected node management
        assert form.get_selected_node() is None
        node = TTSNode(None, "test code", None)
        form.set_selected_node(node)
        assert form.get_selected_node() == node
        
        # Test other methods
        form.parse_content()
        form.load_language_parser("python")
        form.load_language_fields()
        form.fill_node_props(node)
        form.clear_node_props()
        
        tree_node = TTSTreeViewNode(node, "test")
        form.setup_tree_node(tree_node, node)


class TestTDTSLanguageForm:
    """Test cases for TDTSLanguageForm."""
    
    def test_language_form_initialization(self):
        """Test that TDTSLanguageForm can be initialized."""
        form = TDTSLanguageForm()
        assert form is not None
        assert form.is_initialized() is False
        assert form.is_destroyed() is False
    
    def test_language_form_methods(self):
        """Test TDTSLanguageForm methods."""
        form = TDTSLanguageForm()
        
        # Test language management
        assert form.get_language() is None
        form.set_language(None)
        assert form.get_language() is None
        
        # Test other methods
        form.update_language()


class TestTDTSQueryForm:
    """Test cases for TDTSQueryForm."""
    
    def test_query_form_initialization(self):
        """Test that TDTSQueryForm can be initialized."""
        form = TDTSQueryForm()
        assert form is not None
        assert form.is_initialized() is False
        assert form.is_destroyed() is False
    
    def test_query_form_methods(self):
        """Test TDTSQueryForm methods."""
        form = TDTSQueryForm()
        
        # Test tree management
        assert form.get_tree() is None
        tree = TTSTree(None, "test code", None)
        form.set_tree(tree)
        assert form.get_tree() == tree
        
        # Test query management
        assert form.get_query() is None
        query = TTSQuery(None, "test query", 0, TTSQueryError.NONE)
        form.set_query(query)
        assert form.get_query() == query
        
        # Test query cursor management
        assert form.get_query_cursor() is None
        cursor = TTSQueryCursor()
        form.set_query_cursor(cursor)
        assert form.get_query_cursor() == cursor
        
        # Test current match management
        assert form.get_current_match() is None
        form.set_current_match(None)
        assert form.get_current_match() is None
        
        # Test other methods
        form.clear_query()
        form.clear_matches()
        form.clear_predicates()
        form.tree_deleted()
        form.new_tree_generated(tree)


class TestGlobalFunctions:
    """Test cases for global functions."""
    
    def test_show_language_info(self):
        """Test show_language_info function."""
        show_language_info(None)
    
    def test_show_query_form(self):
        """Test show_query_form function."""
        tree = TTSTree(None, "test code", None)
        show_query_form(tree)
    
    def test_create_main_form(self):
        """Test create_main_form function."""
        form = create_main_form()
        assert isinstance(form, TDTSMainForm)


class TestTTSForwardDeclaration:
    """Test cases for TTSForwardDeclaration."""
    
    def test_forward_declaration_initialization(self):
        """Test that TTSForwardDeclaration can be initialized."""
        declaration = TTSForwardDeclaration("TestClass")
        assert declaration is not None
        assert declaration.get_name() == "TestClass"
        assert declaration.is_resolved() is False
        assert declaration.get_resolved_class() is None
    
    def test_forward_declaration_resolution(self):
        """Test TTSForwardDeclaration resolution."""
        declaration = TTSForwardDeclaration("TestClass")
        
        # Test resolution
        class TestClass:
            pass
        
        declaration.resolve(TestClass)
        assert declaration.is_resolved() is True
        assert declaration.get_resolved_class() == TestClass


class TestTTSMutuallyDependent:
    """Test cases for TTSMutuallyDependent."""
    
    def test_mutually_dependent_initialization(self):
        """Test that TTSMutuallyDependent can be initialized."""
        dependent = TTSMutuallyDependent()
        assert dependent is not None
        assert dependent.is_initialized() is False
        assert isinstance(dependent.get_dependencies(), list)
        assert isinstance(dependent._resolved_dependencies, dict)
    
    def test_mutually_dependent_methods(self):
        """Test TTSMutuallyDependent methods."""
        dependent1 = TTSMutuallyDependent()
        dependent2 = TTSMutuallyDependent()
        
        # Test dependency management
        assert isinstance(dependent1.get_dependencies(), list)
        dependent1.add_dependency(dependent2)
        assert dependent2 in dependent1.get_dependencies()
        
        dependent1.remove_dependency(dependent2)
        assert dependent2 not in dependent1.get_dependencies()
        
        # Test dependency resolution
        dependent1.resolve_dependency("test", dependent2)
        assert dependent1.get_resolved_dependency("test") == dependent2
        assert dependent1.get_resolved_dependency("nonexistent") is None
        
        # Test initialization
        dependent1.initialize()
        assert dependent1.is_initialized() is True


class TestForwardDeclarationRegistry:
    """Test cases for forward declaration registry."""
    
    def test_register_forward_declaration(self):
        """Test register_forward_declaration function."""
        declaration = register_forward_declaration("TestClass")
        assert isinstance(declaration, TTSForwardDeclaration)
        assert declaration.get_name() == "TestClass"
        
        # Test that it's added to the registry
        assert "TestClass" in FORWARD_DECLARATIONS
    
    def test_resolve_forward_declaration(self):
        """Test resolve_forward_declaration function."""
        class TestClass:
            pass
        
        resolve_forward_declaration("TestClass", TestClass)
        declaration = get_forward_declaration("TestClass")
        assert declaration is not None
        assert declaration.is_resolved() is True
        assert declaration.get_resolved_class() == TestClass
    
    def test_get_forward_declaration(self):
        """Test get_forward_declaration function."""
        declaration = get_forward_declaration("TTSNode")
        assert declaration is not None
        assert declaration.get_name() == "TTSNode"
        
        # Test nonexistent declaration
        declaration = get_forward_declaration("NonexistentClass")
        assert declaration is None
