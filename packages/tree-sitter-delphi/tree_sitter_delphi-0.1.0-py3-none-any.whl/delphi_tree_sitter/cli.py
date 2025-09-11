"""
Command-line interface for delphi-tree-sitter.
"""

import argparse
import sys
from typing import Optional
from .parser import Parser
from .language import Language


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Delphi Tree Sitter - Parse and analyze code with tree-sitter"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse source code")
    parse_parser.add_argument("file", help="Source file to parse")
    parse_parser.add_argument("--language", help="Language library path")
    parse_parser.add_argument("--output", help="Output file (default: stdout)")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query syntax tree")
    query_parser.add_argument("file", help="Source file to query")
    query_parser.add_argument("query", help="Tree-sitter query string")
    query_parser.add_argument("--language", help="Language library path")
    
    args = parser.parse_args()
    
    if args.command == "parse":
        parse_file(args.file, args.language, args.output)
    elif args.command == "query":
        query_file(args.file, args.query, args.language)
    else:
        parser.print_help()


def parse_file(file_path: str, language_path: Optional[str], output_path: Optional[str]) -> None:
    """Parse a source file and output the syntax tree."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        
        parser = Parser()
        
        if language_path:
            # In a real implementation, you would load the language
            # language = Language.from_library(language_path)
            # parser.set_language(language)
            pass
        
        # tree = parser.parse(source_code)
        # output = format_tree(tree.root_node)
        
        output = f"Parsed {file_path} (placeholder output)"
        
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)
            
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def query_file(file_path: str, query_string: str, language_path: Optional[str]) -> None:
    """Query a source file with a tree-sitter query."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        
        parser = Parser()
        
        if language_path:
            # In a real implementation, you would load the language
            # language = Language.from_library(language_path)
            # parser.set_language(language)
            pass
        
        # tree = parser.parse(source_code)
        # query = Query(language, query_string)
        # cursor = QueryCursor()
        # cursor.execute(query, tree.root_node)
        
        print(f"Querying {file_path} with query: {query_string}")
        print("(placeholder output)")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_tree(node, indent: int = 0) -> str:
    """Format a syntax tree for display."""
    # This is a placeholder implementation
    return "  " * indent + f"{node.type}\n"


if __name__ == "__main__":
    main()
