"""
Tests for the CLI module.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open
from delphi_tree_sitter.cli import parse_file, query_file


class TestCLI:
    """Test cases for the CLI module."""
    
    def test_parse_file_success(self):
        """Test parsing a file successfully."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write('def hello():\n    print("Hello, World!")')
            temp_file = f.name
        
        try:
            # Should not raise an exception
            parse_file(temp_file, None, None)
        finally:
            os.unlink(temp_file)
    
    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        with pytest.raises(SystemExit):
            parse_file("nonexistent.py", None, None)
    
    def test_parse_file_with_output(self):
        """Test parsing a file with output to file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as input_file:
            input_file.write('def hello():\n    print("Hello, World!")')
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as output_file:
            output_path = output_file.name
        
        try:
            # Should not raise an exception
            parse_file(input_path, None, output_path)
            
            # Check that output file was created
            assert os.path.exists(output_path)
        finally:
            os.unlink(input_path)
            os.unlink(output_path)
    
    def test_query_file_success(self):
        """Test querying a file successfully."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write('def hello():\n    print("Hello, World!")')
            temp_file = f.name
        
        try:
            # Should not raise an exception
            query_file(temp_file, "(function_definition) @function", None)
        finally:
            os.unlink(temp_file)
    
    def test_query_file_not_found(self):
        """Test querying a non-existent file."""
        with pytest.raises(SystemExit):
            query_file("nonexistent.py", "(function_definition) @function", None)
