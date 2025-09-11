"""
Tests for the Query and QueryCursor classes.
"""

import pytest
from delphi_tree_sitter import Query, QueryCursor, Language, Node


class TestQuery:
    """Test cases for the Query class."""
    
    def test_query_initialization(self):
        """Test that a query can be initialized."""
        language = Language()
        query_string = "(function_definition) @function"
        query = Query(language, query_string)
        assert query is not None
    
    def test_query_capture_count(self):
        """Test getting the capture count."""
        language = Language()
        query_string = "(function_definition) @function"
        query = Query(language, query_string)
        assert query.capture_count == 0  # Placeholder value
    
    def test_query_pattern_count(self):
        """Test getting the pattern count."""
        language = Language()
        query_string = "(function_definition) @function"
        query = Query(language, query_string)
        assert query.pattern_count == 0  # Placeholder value
    
    def test_capture_name_for_id(self):
        """Test getting capture name for ID."""
        language = Language()
        query = Query(language, "(function_definition) @function")
        capture_name = query.capture_name_for_id(0)
        assert capture_name is None  # Placeholder implementation
    
    def test_capture_quantifier_for_id(self):
        """Test getting capture quantifier for ID."""
        language = Language()
        query = Query(language, "(function_definition) @function")
        quantifier = query.capture_quantifier_for_id(0, 0)
        assert quantifier == ""  # Placeholder implementation


class TestQueryCursor:
    """Test cases for the QueryCursor class."""
    
    def test_cursor_initialization(self):
        """Test that a query cursor can be initialized."""
        cursor = QueryCursor()
        assert cursor is not None
    
    def test_execute_query(self):
        """Test executing a query."""
        language = Language()
        node = Node(None, "test code", language)
        query = Query(language, "(function_definition) @function")
        cursor = QueryCursor()
        
        # Should not raise an exception
        cursor.execute(query, node)
    
    def test_next_match(self):
        """Test getting the next match."""
        language = Language()
        node = Node(None, "test code", language)
        query = Query(language, "(function_definition) @function")
        cursor = QueryCursor()
        cursor.execute(query, node)
        
        # Should return None since there are no matches
        match = cursor.next_match()
        assert match is None
    
    def test_remove_match(self):
        """Test removing a match."""
        cursor = QueryCursor()
        # Should not raise an exception
        cursor.remove_match(0)
    
    def test_set_point_range(self):
        """Test setting point range."""
        cursor = QueryCursor()
        # Should not raise an exception
        cursor.set_point_range((0, 0), (1, 0))
    
    def test_set_byte_range(self):
        """Test setting byte range."""
        cursor = QueryCursor()
        # Should not raise an exception
        cursor.set_byte_range(0, 10)


class TestQueryMatch:
    """Test cases for the QueryMatch class."""
    
    def test_match_initialization(self):
        """Test that a query match can be initialized."""
        from delphi_tree_sitter.query import QueryMatch
        
        language = Language()
        node = Node(None, "test code", language)
        captures = {"function": node}
        
        match = QueryMatch(0, captures)
        assert match.pattern_id == 0
        assert match.captures == captures
