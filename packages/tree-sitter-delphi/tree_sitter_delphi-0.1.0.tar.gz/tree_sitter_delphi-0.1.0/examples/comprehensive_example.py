"""
Comprehensive example demonstrating the delphi-tree-sitter Python library.

This example shows how to use all the major features of the library.
"""

import sys
import os

# Add the parent directory to the path so we can import delphi_tree_sitter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from delphi_tree_sitter import (
    Parser, Language, Tree, Node, TreeCursor, Query, QueryCursor,
    Point, Range, Input, InputEncoding, SymbolType, Quantifier,
    TreeSitterException, TreeSitterParseError, TreeSitterQueryError,
    LookAheadIterator, WasmEngine, WasmStore, WasmParser,
    Logger, Allocator, TreeSitterConfig, TreeWalker, QueryBuilder,
    create_input_from_string, create_input_from_file, create_point, create_range
)


def basic_parsing_example():
    """Demonstrate basic parsing functionality."""
    print("=== Basic Parsing Example ===")
    
    try:
        # Create a parser
        parser = Parser()
        
        # Load a language (this would normally load from a shared library)
        # language = Language.from_library("path/to/language.so", "tree_sitter_python")
        language = Language()  # Placeholder for demo
        
        # Set the language
        parser.set_language(language)
        
        # Parse some source code
        source_code = """
def hello_world():
    print("Hello, World!")
    return 42

class Example:
    def __init__(self):
        self.value = 0
"""
        
        tree = parser.parse_string(source_code)
        root = tree.root_node
        
        print(f"Root node type: {root.type}")
        print(f"Root node text: {root.text[:50]}...")
        print(f"Number of children: {root.child_count()}")
        print(f"Number of named children: {root.named_child_count()}")
        
    except TreeSitterException as e:
        print(f"Error: {e}")


def tree_navigation_example():
    """Demonstrate tree navigation."""
    print("\n=== Tree Navigation Example ===")
    
    try:
        # Create a simple tree structure
        parser = Parser()
        language = Language()
        parser.set_language(language)
        
        source_code = "def example(): pass"
        tree = parser.parse_string(source_code)
        root = tree.root_node
        
        # Navigate the tree
        print("Tree structure:")
        def print_node(node, indent=0):
            print("  " * indent + f"- {node.type}")
            for child in node.children():
                print_node(child, indent + 1)
        
        print_node(root)
        
        # Use a tree cursor for more efficient navigation
        cursor = root.walk()
        print(f"\nCursor at: {cursor.current_node.type}")
        
        if cursor.goto_first_child():
            print(f"First child: {cursor.current_node.type}")
        
    except TreeSitterException as e:
        print(f"Error: {e}")


def query_example():
    """Demonstrate query functionality."""
    print("\n=== Query Example ===")
    
    try:
        # Create a parser and parse some code
        parser = Parser()
        language = Language()
        parser.set_language(language)
        
        source_code = """
def function_one():
    return 1

def function_two():
    return 2

class MyClass:
    def method_one(self):
        pass
"""
        
        tree = parser.parse_string(source_code)
        root = tree.root_node
        
        # Create a query to find function definitions
        query_string = """
(function_definition
  name: (identifier) @function_name
  body: (block) @function_body)
"""
        
        query = Query(language, query_string)
        cursor = QueryCursor()
        cursor.execute(query, root)
        
        print("Query results:")
        while True:
            match = cursor.next_match()
            if match is None:
                break
            
            print(f"Pattern {match.pattern_id} matched:")
            for capture in match.captures:
                print(f"  {capture.index}: {capture.node.type}")
        
    except TreeSitterException as e:
        print(f"Error: {e}")


def advanced_features_example():
    """Demonstrate advanced features."""
    print("\n=== Advanced Features Example ===")
    
    try:
        # Tree walker example
        parser = Parser()
        language = Language()
        parser.set_language(language)
        
        source_code = """
def outer_function():
    def inner_function():
        return "nested"
    return inner_function()
"""
        
        tree = parser.parse_string(source_code)
        root = tree.root_node
        
        # Use tree walker to find all function definitions
        walker = TreeWalker(root)
        functions = walker.find_nodes_by_type("function_definition")
        
        print(f"Found {len(functions)} function definitions")
        for func in functions:
            print(f"  - Function at {func.start_point}")
        
        # Query builder example
        builder = QueryBuilder()
        query_string = builder.add_capture("function", "function_definition").build()
        print(f"Built query: {query_string}")
        
    except TreeSitterException as e:
        print(f"Error: {e}")


def error_handling_example():
    """Demonstrate error handling."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Try to parse invalid code
        parser = Parser()
        language = Language()
        parser.set_language(language)
        
        # This should work (placeholder implementation)
        tree = parser.parse_string("def valid(): pass")
        print("Valid code parsed successfully")
        
        # Try to create an invalid query
        try:
            query = Query(language, "invalid query syntax")
            print("Query created (placeholder implementation)")
        except TreeSitterQueryError as e:
            print(f"Query error: {e}")
        
    except TreeSitterParseError as e:
        print(f"Parse error: {e}")
    except TreeSitterException as e:
        print(f"General error: {e}")


def utility_functions_example():
    """Demonstrate utility functions."""
    print("\n=== Utility Functions Example ===")
    
    # Create points and ranges
    start_point = create_point(0, 0)
    end_point = create_point(5, 10)
    range_obj = create_range(start_point, end_point, 0, 50)
    
    print(f"Start point: {start_point}")
    print(f"End point: {end_point}")
    print(f"Range: {range_obj}")
    
    # Create input from string
    input_obj = create_input_from_string("def example(): pass")
    print(f"Input encoding: {input_obj.encoding}")
    
    # Test input reading
    data = input_obj.read_func(0, start_point)
    print(f"Read {len(data)} bytes from input")


def configuration_example():
    """Demonstrate configuration options."""
    print("\n=== Configuration Example ===")
    
    # Create a custom logger
    def custom_log(log_type: str, message: str):
        print(f"[CUSTOM {log_type.upper()}] {message}")
    
    logger = Logger(custom_log)
    logger.log("parse", "Starting parse operation")
    
    # Create configuration
    config = TreeSitterConfig()
    config.set_logger(logger)
    
    print("Configuration set up successfully")


def main():
    """Run all examples."""
    print("Delphi Tree Sitter Python Library - Comprehensive Example")
    print("=" * 60)
    
    basic_parsing_example()
    tree_navigation_example()
    query_example()
    advanced_features_example()
    error_handling_example()
    utility_functions_example()
    configuration_example()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("\nNote: This is a placeholder implementation.")
    print("To use with real tree-sitter functionality, you would need to:")
    print("1. Load actual tree-sitter shared libraries")
    print("2. Implement the ctypes bindings to the C API")
    print("3. Load language grammars from shared libraries")


if __name__ == "__main__":
    main()
