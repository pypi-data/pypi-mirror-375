"""
Tests for the Language class.
"""

import pytest
from delphi_tree_sitter import Language


class TestLanguage:
    """Test cases for the Language class."""
    
    def test_language_initialization(self):
        """Test that a language can be initialized."""
        language = Language()
        assert language is not None
    
    def test_language_version(self):
        """Test getting the language version."""
        language = Language()
        version = language.version
        assert isinstance(version, int)
        assert version >= 0
    
    def test_field_count(self):
        """Test getting the field count."""
        language = Language()
        field_count = language.field_count
        assert isinstance(field_count, int)
        assert field_count >= 0
    
    def test_symbol_count(self):
        """Test getting the symbol count."""
        language = Language()
        symbol_count = language.symbol_count
        assert isinstance(symbol_count, int)
        assert symbol_count >= 0
    
    def test_field_name_for_id(self):
        """Test getting field name for ID."""
        language = Language()
        field_name = language.field_name_for_id(0)
        # Should return None for invalid ID
        assert field_name is None
    
    def test_field_id_for_name(self):
        """Test getting field ID for name."""
        language = Language()
        field_id = language.field_id_for_name("nonexistent")
        # Should return None for invalid name
        assert field_id is None
    
    def test_symbol_name(self):
        """Test getting symbol name."""
        language = Language()
        symbol_name = language.symbol_name(0)
        # Should return None for invalid ID
        assert symbol_name is None
    
    def test_symbol_for_name(self):
        """Test getting symbol for name."""
        language = Language()
        symbol_id = language.symbol_for_name("nonexistent")
        # Should return None for invalid name
        assert symbol_id is None
