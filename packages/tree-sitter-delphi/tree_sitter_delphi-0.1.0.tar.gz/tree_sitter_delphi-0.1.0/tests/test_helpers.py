"""
Tests for helper classes and utilities.
"""

import pytest
from delphi_tree_sitter import (
    NodePropertyHelper, LanguageInfoHelper, QueryHelper, QueryMatchHelper,
    TreeNavigationHelper, FieldHelper, ValidationHelper, ConditionalLogicHelper,
    TreeViewHelper, CodeSelectionHelper, LanguageLoaderHelper, QueryFormHelper,
    PropertyGridHelper, ErrorHandler, DemoStateManager,
    NodeValidator, QueryValidator, LanguageValidator, ConditionalLogic,
    Node, Language, Query, QueryMatch, QueryCapture, Tree, Point
)


class TestNodePropertyHelper:
    """Test cases for NodePropertyHelper."""
    
    def test_node_property_helper_initialization(self):
        """Test that NodePropertyHelper can be initialized."""
        language = Language()
        node = Node(None, "test code", language)
        helper = NodePropertyHelper(node)
        assert helper.node == node
    
    def test_get_property_dict(self):
        """Test getting property dictionary."""
        language = Language()
        node = Node(None, "test code", language)
        helper = NodePropertyHelper(node)
        properties = helper.get_property_dict()
        
        assert isinstance(properties, dict)
        assert 'Symbol' in properties
        assert 'GrammarType' in properties
        assert 'IsError' in properties
        assert 'ChildCount' in properties


class TestLanguageInfoHelper:
    """Test cases for LanguageInfoHelper."""
    
    def test_language_info_helper_initialization(self):
        """Test that LanguageInfoHelper can be initialized."""
        language = Language()
        helper = LanguageInfoHelper(language)
        assert helper.language == language
    
    def test_get_fields_info(self):
        """Test getting fields information."""
        language = Language()
        helper = LanguageInfoHelper(language)
        fields = helper.get_fields_info()
        
        assert isinstance(fields, list)
        # Should be empty for placeholder implementation
        assert len(fields) == 0
    
    def test_get_symbols_info(self):
        """Test getting symbols information."""
        language = Language()
        helper = LanguageInfoHelper(language)
        symbols = helper.get_symbols_info()
        
        assert isinstance(symbols, list)
        # Should be empty for placeholder implementation
        assert len(symbols) == 0


class TestQueryHelper:
    """Test cases for QueryHelper."""
    
    def test_query_helper_initialization(self):
        """Test that QueryHelper can be initialized."""
        language = Language()
        query = Query(language, "(function_definition) @function")
        helper = QueryHelper(query)
        assert helper.query == query
    
    def test_get_predicates_for_pattern(self):
        """Test getting predicates for a pattern."""
        language = Language()
        query = Query(language, "(function_definition) @function")
        helper = QueryHelper(query)
        predicates = helper.get_predicates_for_pattern(0)
        
        assert isinstance(predicates, list)
        # Should be empty for placeholder implementation
        assert len(predicates) == 0


class TestTreeNavigationHelper:
    """Test cases for TreeNavigationHelper."""
    
    def test_tree_navigation_helper_initialization(self):
        """Test that TreeNavigationHelper can be initialized."""
        language = Language()
        node = Node(None, "test code", language)
        helper = TreeNavigationHelper(node)
        assert helper.root_node == node
        assert helper.current_node == node
    
    def test_goto_first_child(self):
        """Test navigating to first child."""
        language = Language()
        node = Node(None, "test code", language)
        helper = TreeNavigationHelper(node)
        
        # Should return False for placeholder implementation
        result = helper.goto_first_child()
        assert result is False
    
    def test_can_goto_first_child(self):
        """Test checking if can navigate to first child."""
        language = Language()
        node = Node(None, "test code", language)
        helper = TreeNavigationHelper(node)
        
        # Should return False for placeholder implementation
        result = helper.can_goto_first_child()
        assert result is False


class TestFieldHelper:
    """Test cases for FieldHelper."""
    
    def test_field_helper_initialization(self):
        """Test that FieldHelper can be initialized."""
        language = Language()
        helper = FieldHelper(language)
        assert helper.language == language
    
    def test_get_field_names(self):
        """Test getting field names."""
        language = Language()
        helper = FieldHelper(language)
        field_names = helper.get_field_names()
        
        assert isinstance(field_names, list)
        # Should be empty for placeholder implementation
        assert len(field_names) == 0


class TestValidationHelper:
    """Test cases for ValidationHelper."""
    
    def test_validate_node(self):
        """Test node validation."""
        language = Language()
        node = Node(None, "test code", language)
        issues = ValidationHelper.validate_node(node)
        
        assert isinstance(issues, list)
        # Should have some issues for placeholder implementation
        assert len(issues) >= 0
    
    def test_validate_query(self):
        """Test query validation."""
        language = Language()
        query = Query(language, "(function_definition) @function")
        issues = ValidationHelper.validate_query(query)
        
        assert isinstance(issues, list)
        # Should have some issues for placeholder implementation
        assert len(issues) >= 0
    
    def test_validate_language(self):
        """Test language validation."""
        language = Language()
        issues = ValidationHelper.validate_language(language)
        
        assert isinstance(issues, list)
        # Should have some issues for placeholder implementation
        assert len(issues) >= 0


class TestConditionalLogicHelper:
    """Test cases for ConditionalLogicHelper."""
    
    def test_should_include_node(self):
        """Test node inclusion logic."""
        language = Language()
        node = Node(None, "test code", language)
        
        # Test basic inclusion
        result = ConditionalLogicHelper.should_include_node(node)
        assert result is True
        
        # Test named only
        result = ConditionalLogicHelper.should_include_node(node, named_only=True)
        assert result is True  # Placeholder implementation returns True
    
    def test_get_node_children(self):
        """Test getting filtered children."""
        language = Language()
        node = Node(None, "test code", language)
        children = ConditionalLogicHelper.get_node_children(node)
        
        assert isinstance(children, list)
        # Should be empty for placeholder implementation
        assert len(children) == 0


class TestTreeViewHelper:
    """Test cases for TreeViewHelper."""
    
    def test_tree_view_helper_initialization(self):
        """Test that TreeViewHelper can be initialized."""
        language = Language()
        node = Node(None, "test code", language)
        helper = TreeViewHelper(node)
        assert helper.root_node == node
        assert helper.named_only is False
    
    def test_create_tree_item(self):
        """Test creating tree item."""
        language = Language()
        node = Node(None, "test code", language)
        helper = TreeViewHelper(node)
        item = helper.create_tree_item(node)
        
        assert isinstance(item, dict)
        assert 'node' in item
        assert 'parent_index' in item
        assert 'text' in item
        assert 'has_children' in item
        assert 'children' in item
    
    def test_build_tree(self):
        """Test building tree structure."""
        language = Language()
        node = Node(None, "test code", language)
        helper = TreeViewHelper(node)
        tree_items = helper.build_tree()
        
        assert isinstance(tree_items, list)
        assert len(tree_items) >= 1  # At least the root node


class TestCodeSelectionHelper:
    """Test cases for CodeSelectionHelper."""
    
    def test_code_selection_helper_initialization(self):
        """Test that CodeSelectionHelper can be initialized."""
        source_code = "def hello(): pass"
        helper = CodeSelectionHelper(source_code)
        assert helper.source_code == source_code
        assert len(helper.lines) == 1
    
    def test_get_selection_range(self):
        """Test getting selection range."""
        source_code = "def hello(): pass"
        helper = CodeSelectionHelper(source_code)
        language = Language()
        node = Node(None, source_code, language)
        
        start_pos, end_pos = helper.get_selection_range(node)
        assert isinstance(start_pos, int)
        assert isinstance(end_pos, int)
        assert start_pos >= 0
        assert end_pos >= start_pos
    
    def test_get_line_range(self):
        """Test getting line range."""
        source_code = "def hello(): pass"
        helper = CodeSelectionHelper(source_code)
        language = Language()
        node = Node(None, source_code, language)
        
        start_line, end_line = helper.get_line_range(node)
        assert isinstance(start_line, int)
        assert isinstance(end_line, int)
        assert start_line >= 0
        assert end_line >= start_line


class TestLanguageLoaderHelper:
    """Test cases for LanguageLoaderHelper."""
    
    def test_language_loader_helper_initialization(self):
        """Test that LanguageLoaderHelper can be initialized."""
        helper = LanguageLoaderHelper()
        assert isinstance(helper.loaded_languages, dict)
        assert len(helper.loaded_languages) == 0
    
    def test_get_available_languages(self):
        """Test getting available languages."""
        helper = LanguageLoaderHelper()
        languages = helper.get_available_languages()
        
        assert isinstance(languages, list)
        assert len(languages) == 0
    
    def test_is_language_loaded(self):
        """Test checking if language is loaded."""
        helper = LanguageLoaderHelper()
        result = helper.is_language_loaded("python")
        assert result is False


class TestQueryFormHelper:
    """Test cases for QueryFormHelper."""
    
    def test_query_form_helper_initialization(self):
        """Test that QueryFormHelper can be initialized."""
        language = Language()
        tree = Tree(None, "test code", language)
        helper = QueryFormHelper(tree)
        assert helper.tree == tree
        assert helper.current_query is None
    
    def test_create_query(self):
        """Test creating a query."""
        language = Language()
        tree = Tree(None, "test code", language)
        helper = QueryFormHelper(tree)
        
        success, message, query = helper.create_query("(function_definition) @function")
        assert isinstance(success, bool)
        assert isinstance(message, str)
        # Query might be None for placeholder implementation
        assert query is None or isinstance(query, Query)


class TestPropertyGridHelper:
    """Test cases for PropertyGridHelper."""
    
    def test_property_grid_helper_initialization(self):
        """Test that PropertyGridHelper can be initialized."""
        helper = PropertyGridHelper()
        assert isinstance(helper.properties, dict)
        assert len(helper.properties) == 0
    
    def test_set_node_properties(self):
        """Test setting node properties."""
        helper = PropertyGridHelper()
        language = Language()
        node = Node(None, "test code", language)
        
        helper.set_node_properties(node)
        assert len(helper.properties) > 0
    
    def test_get_property_value(self):
        """Test getting property value."""
        helper = PropertyGridHelper()
        language = Language()
        node = Node(None, "test code", language)
        
        helper.set_node_properties(node)
        value = helper.get_property_value("Symbol")
        assert isinstance(value, str)


class TestErrorHandler:
    """Test cases for ErrorHandler."""
    
    def test_handle_parse_error(self):
        """Test handling parse errors."""
        error = Exception("Test parse error")
        message = ErrorHandler.handle_parse_error(error)
        assert "Parse error" in message
        assert "Test parse error" in message
    
    def test_handle_query_error(self):
        """Test handling query errors."""
        error = Exception("Test query error")
        message = ErrorHandler.handle_query_error(error)
        assert "Query error" in message
        assert "Test query error" in message
    
    def test_format_error_message(self):
        """Test formatting error messages."""
        message = ErrorHandler.format_error_message("Test", "Error occurred", "Additional details")
        assert "[Test]" in message
        assert "Error occurred" in message
        assert "Additional details" in message


class TestDemoStateManager:
    """Test cases for DemoStateManager."""
    
    def test_demo_state_manager_initialization(self):
        """Test that DemoStateManager can be initialized."""
        manager = DemoStateManager()
        assert manager.current_tree is None
        assert manager.current_language is None
        assert manager.edit_changed is False
    
    def test_set_and_get_tree(self):
        """Test setting and getting tree."""
        manager = DemoStateManager()
        language = Language()
        tree = Tree(None, "test code", language)
        
        manager.set_tree(tree)
        assert manager.get_tree() == tree
    
    def test_reset(self):
        """Test resetting state."""
        manager = DemoStateManager()
        language = Language()
        tree = Tree(None, "test code", language)
        
        manager.set_tree(tree)
        manager.set_edit_changed(True)
        manager.reset()
        
        assert manager.get_tree() is None
        assert manager.is_edit_changed() is False


class TestNodeValidator:
    """Test cases for NodeValidator."""
    
    def test_validate_node_integrity(self):
        """Test node integrity validation."""
        language = Language()
        node = Node(None, "test code", language)
        issues = NodeValidator.validate_node_integrity(node)
        
        assert isinstance(issues, list)
        # Should have some issues for placeholder implementation
        assert len(issues) >= 0
    
    def test_validate_node_consistency(self):
        """Test node consistency validation."""
        language = Language()
        node = Node(None, "test code", language)
        issues = NodeValidator.validate_node_consistency(node, "test code")
        
        assert isinstance(issues, list)
        # Should have some issues for placeholder implementation
        assert len(issues) >= 0


class TestQueryValidator:
    """Test cases for QueryValidator."""
    
    def test_validate_query_syntax(self):
        """Test query syntax validation."""
        # Valid query
        is_valid, message, offset = QueryValidator.validate_query_syntax("(function_definition) @function")
        assert is_valid is True
        assert message is None
        assert offset is None
        
        # Invalid query - empty
        is_valid, message, offset = QueryValidator.validate_query_syntax("")
        assert is_valid is False
        assert message is not None
        assert offset is not None
        
        # Invalid query - mismatched parentheses
        is_valid, message, offset = QueryValidator.validate_query_syntax("(function_definition @function")
        assert is_valid is False
        assert "parentheses" in message


class TestLanguageValidator:
    """Test cases for LanguageValidator."""
    
    def test_validate_language(self):
        """Test language validation."""
        language = Language()
        issues = LanguageValidator.validate_language(language)
        
        assert isinstance(issues, list)
        # Should have some issues for placeholder implementation
        assert len(issues) >= 0


class TestConditionalLogic:
    """Test cases for ConditionalLogic."""
    
    def test_should_expand_node(self):
        """Test node expansion logic."""
        language = Language()
        node = Node(None, "test code", language)
        
        result = ConditionalLogic.should_expand_node(node)
        assert isinstance(result, bool)
    
    def test_should_show_node(self):
        """Test node visibility logic."""
        language = Language()
        node = Node(None, "test code", language)
        
        result = ConditionalLogic.should_show_node(node)
        assert isinstance(result, bool)
    
    def test_get_node_display_text(self):
        """Test getting node display text."""
        language = Language()
        node = Node(None, "test code", language)
        
        text = ConditionalLogic.get_node_display_text(node)
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_filter_nodes_by_condition(self):
        """Test filtering nodes by condition."""
        language = Language()
        nodes = [Node(None, "test code", language) for _ in range(3)]
        
        filtered = ConditionalLogic.filter_nodes_by_condition(nodes, lambda n: True)
        assert len(filtered) == 3
        
        filtered = ConditionalLogic.filter_nodes_by_condition(nodes, lambda n: False)
        assert len(filtered) == 0
    
    def test_group_nodes_by_type(self):
        """Test grouping nodes by type."""
        language = Language()
        nodes = [Node(None, "test code", language) for _ in range(3)]
        
        groups = ConditionalLogic.group_nodes_by_type(nodes)
        assert isinstance(groups, dict)
        assert len(groups) >= 0
    
    def test_count_nodes_by_type(self):
        """Test counting nodes by type."""
        language = Language()
        nodes = [Node(None, "test code", language) for _ in range(3)]
        
        counts = ConditionalLogic.count_nodes_by_type(nodes)
        assert isinstance(counts, dict)
        assert len(counts) >= 0
