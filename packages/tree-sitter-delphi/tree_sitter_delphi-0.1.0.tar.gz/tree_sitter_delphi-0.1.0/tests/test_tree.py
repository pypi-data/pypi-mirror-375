"""
Tests for the Tree and Node classes.
"""

import pytest
from delphi_tree_sitter import Tree, Node, Language


class TestNode:
    """Test cases for the Node class."""
    
    def test_node_initialization(self):
        """Test that a node can be initialized."""
        language = Language()
        node = Node(None, "test code", language)
        assert node is not None
    
    def test_node_type(self):
        """Test getting the node type."""
        language = Language()
        node = Node(None, "test code", language)
        assert node.type == "unknown"  # Placeholder value
    
    def test_node_text(self):
        """Test getting the node text."""
        language = Language()
        source_code = "def hello(): pass"
        node = Node(None, source_code, language)
        # Since start_byte and end_byte are 0, text should be empty
        assert node.text == ""
    
    def test_node_start_end_byte(self):
        """Test getting start and end byte positions."""
        language = Language()
        node = Node(None, "test code", language)
        assert node.start_byte == 0
        assert node.end_byte == 0
    
    def test_node_start_end_point(self):
        """Test getting start and end points."""
        language = Language()
        node = Node(None, "test code", language)
        assert node.start_point == (0, 0)
        assert node.end_point == (0, 0)
    
    def test_child_count(self):
        """Test getting child count."""
        language = Language()
        node = Node(None, "test code", language)
        assert node.child_count() == 0
    
    def test_named_child_count(self):
        """Test getting named child count."""
        language = Language()
        node = Node(None, "test code", language)
        assert node.named_child_count() == 0
    
    def test_children_iteration(self):
        """Test iterating over children."""
        language = Language()
        node = Node(None, "test code", language)
        children = list(node.children())
        assert len(children) == 0
    
    def test_named_children_iteration(self):
        """Test iterating over named children."""
        language = Language()
        node = Node(None, "test code", language)
        named_children = list(node.named_children())
        assert len(named_children) == 0


class TestTree:
    """Test cases for the Tree class."""
    
    def test_tree_initialization(self):
        """Test that a tree can be initialized."""
        language = Language()
        tree = Tree(None, "test code", language)
        assert tree is not None
    
    def test_tree_root_node(self):
        """Test getting the root node."""
        language = Language()
        tree = Tree(None, "test code", language)
        root = tree.root_node
        assert root is not None
        assert isinstance(root, Node)
    
    def test_tree_edit(self):
        """Test editing a tree."""
        from delphi_tree_sitter import InputEdit, Point
        language = Language()
        tree = Tree(None, "test code", language)
        # Should not raise an exception
        tree.edit(InputEdit(0, 4, 4, Point(0, 0), Point(0, 4), Point(0, 4)))


class TestTreeCursor:
    """Test cases for the TreeCursor class."""
    
    def test_cursor_initialization(self):
        """Test that a cursor can be initialized."""
        language = Language()
        node = Node(None, "test code", language)
        cursor = node.walk()
        assert cursor is not None
    
    def test_cursor_current_node(self):
        """Test getting the current node."""
        language = Language()
        node = Node(None, "test code", language)
        cursor = node.walk()
        assert cursor.current_node == node
    
    def test_cursor_navigation(self):
        """Test cursor navigation methods."""
        language = Language()
        node = Node(None, "test code", language)
        cursor = node.walk()
        
        # These should return False since there are no children
        assert cursor.goto_first_child() is False
        assert cursor.goto_next_sibling() is False
        assert cursor.goto_parent() is False
