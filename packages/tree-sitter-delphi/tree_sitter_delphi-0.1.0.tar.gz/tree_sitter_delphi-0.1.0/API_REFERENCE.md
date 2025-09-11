# Delphi Tree Sitter Python Library - API Reference

This document provides a comprehensive reference for the delphi-tree-sitter Python library, which provides Python bindings for the tree-sitter parsing library.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Types and Enums](#types-and-enums)
3. [Exceptions](#exceptions)
4. [Advanced Features](#advanced-features)
5. [Utility Functions](#utility-functions)
6. [Examples](#examples)

## Core Classes

### Parser

The main class for parsing source code into syntax trees.

```python
from delphi_tree_sitter import Parser, Language

parser = Parser()
language = Language.from_library("path/to/language.so", "tree_sitter_python")
parser.set_language(language)
tree = parser.parse_string(source_code)
```

#### Methods

- `set_language(language: Language) -> None`: Set the language for parsing
- `get_language() -> Optional[Language]`: Get the current language
- `parse_string(source_code: str, old_tree: Optional[Tree] = None) -> Tree`: Parse source code from a string
- `parse_string_encoding(source_code: str, encoding: InputEncoding, old_tree: Optional[Tree] = None) -> Tree`: Parse with specified encoding
- `parse(input_config: Input, old_tree: Optional[Tree] = None) -> Tree`: Parse using input configuration
- `reset() -> None`: Reset the parser
- `set_timeout_micros(timeout_micros: int) -> None`: Set parsing timeout
- `get_timeout_micros() -> int`: Get current timeout
- `set_cancellation_flag(flag: Optional[ctypes.c_size_t]) -> None`: Set cancellation flag
- `get_cancellation_flag() -> Optional[ctypes.c_size_t]`: Get cancellation flag
- `set_logger(logger) -> None`: Set logger
- `get_logger()`: Get current logger
- `set_included_ranges(ranges: List[Range]) -> None`: Set included ranges
- `get_included_ranges() -> List[Range]`: Get included ranges
- `print_dot_graphs(file_descriptor: int) -> None`: Set DOT graph output

### Language

Represents a tree-sitter language grammar.

```python
from delphi_tree_sitter import Language

# Load from shared library
language = Language.from_library("path/to/language.so", "tree_sitter_python")

# Load from WebAssembly
language = Language.from_wasm(wasm_store, "python", wasm_data)
```

#### Properties

- `version: int`: Language version
- `field_count: int`: Number of fields
- `symbol_count: int`: Number of symbols
- `state_count: int`: Number of valid states

#### Methods

- `field_name_for_id(field_id: int) -> Optional[str]`: Get field name by ID
- `field_id_for_name(field_name: str) -> Optional[int]`: Get field ID by name
- `symbol_name(symbol_id: int) -> Optional[str]`: Get symbol name by ID
- `symbol_for_name(symbol_name: str, is_named: bool = True) -> Optional[int]`: Get symbol ID by name
- `symbol_type(symbol_id: int) -> SymbolType`: Get symbol type
- `next_state(state_id: int, symbol_id: int) -> int`: Get next parse state
- `is_wasm() -> bool`: Check if language is from WebAssembly
- `copy() -> Language`: Create a copy

### Tree

Represents a syntax tree.

```python
from delphi_tree_sitter import Tree

tree = parser.parse_string(source_code)
root = tree.root_node
```

#### Properties

- `root_node: Node`: The root node of the tree

#### Methods

- `root_node_with_offset(offset_bytes: int, offset_extent: Point) -> Node`: Get root node with offset
- `language() -> Language`: Get the language used to parse this tree
- `included_ranges() -> List[Range]`: Get included ranges
- `edit(edit: InputEdit) -> None`: Edit the tree
- `get_changed_ranges(old_tree: Tree) -> List[Range]`: Get changed ranges
- `print_dot_graph(file_descriptor: int) -> None`: Print DOT graph
- `copy() -> Tree`: Create a shallow copy

### Node

Represents a node in a syntax tree.

```python
node = tree.root_node
print(f"Type: {node.type}")
print(f"Text: {node.text}")
```

#### Properties

- `type: str`: Node type
- `symbol: int`: Node's symbol ID
- `grammar_type: str`: Grammar type (ignoring aliases)
- `grammar_symbol: int`: Grammar symbol ID
- `start_byte: int`: Start byte position
- `end_byte: int`: End byte position
- `start_point: Point`: Start point (row, column)
- `end_point: Point`: End point (row, column)
- `text: str`: Text content

#### Methods

- `is_null() -> bool`: Check if node is null
- `is_named() -> bool`: Check if node is named
- `is_missing() -> bool`: Check if node is missing
- `is_extra() -> bool`: Check if node is extra
- `has_changes() -> bool`: Check if node has changes
- `has_error() -> bool`: Check if node has errors
- `is_error() -> bool`: Check if node is an error
- `parse_state() -> int`: Get parse state
- `next_parse_state() -> int`: Get next parse state
- `parent() -> Optional[Node]`: Get parent node
- `child(index: int) -> Optional[Node]`: Get child by index
- `child_count() -> int`: Get number of children
- `named_child(index: int) -> Optional[Node]`: Get named child by index
- `named_child_count() -> int`: Get number of named children
- `child_by_field_name(field_name: str) -> Optional[Node]`: Get child by field name
- `child_by_field_id(field_id: int) -> Optional[Node]`: Get child by field ID
- `field_name_for_child(child_index: int) -> Optional[str]`: Get field name for child
- `next_sibling() -> Optional[Node]`: Get next sibling
- `prev_sibling() -> Optional[Node]`: Get previous sibling
- `next_named_sibling() -> Optional[Node]`: Get next named sibling
- `prev_named_sibling() -> Optional[Node]`: Get previous named sibling
- `first_child_for_byte(byte: int) -> Optional[Node]`: Get first child for byte
- `first_named_child_for_byte(byte: int) -> Optional[Node]`: Get first named child for byte
- `descendant_count() -> int`: Get descendant count
- `descendant_for_byte_range(start_byte: int, end_byte: int) -> Optional[Node]`: Get descendant for byte range
- `descendant_for_point_range(start_point: Point, end_point: Point) -> Optional[Node]`: Get descendant for point range
- `named_descendant_for_byte_range(start_byte: int, end_byte: int) -> Optional[Node]`: Get named descendant for byte range
- `named_descendant_for_point_range(start_point: Point, end_point: Point) -> Optional[Node]`: Get named descendant for point range
- `edit(edit: InputEdit) -> None`: Edit the node
- `equals(other: Node) -> bool`: Check if nodes are equal
- `to_string() -> str`: Get S-expression representation
- `children() -> Iterator[Node]`: Iterate over children
- `named_children() -> Iterator[Node]`: Iterate over named children
- `walk() -> TreeCursor`: Create a tree cursor

### TreeCursor

A cursor for efficiently walking through a syntax tree.

```python
cursor = node.walk()
cursor.goto_first_child()
print(f"Current node: {cursor.current_node.type}")
```

#### Properties

- `current_node: Node`: Current node
- `current_field_name: Optional[str]`: Current field name
- `current_field_id: int`: Current field ID
- `current_depth: int`: Current depth
- `current_descendant_index: int`: Current descendant index

#### Methods

- `reset(node: Node) -> None`: Reset to a different node
- `reset_to(other_cursor: TreeCursor) -> None`: Reset to another cursor's position
- `goto_parent() -> bool`: Move to parent
- `goto_next_sibling() -> bool`: Move to next sibling
- `goto_prev_sibling() -> bool`: Move to previous sibling
- `goto_first_child() -> bool`: Move to first child
- `goto_last_child() -> bool`: Move to last child
- `goto_descendant(goal_descendant_index: int) -> None`: Move to descendant
- `goto_first_child_for_byte(goal_byte: int) -> int`: Move to first child for byte
- `goto_first_child_for_point(goal_point: Point) -> int`: Move to first child for point
- `copy() -> TreeCursor`: Create a copy

### Query

A tree-sitter query for matching patterns in syntax trees.

```python
from delphi_tree_sitter import Query

query_string = """
(function_definition
  name: (identifier) @function_name
  body: (block) @function_body)
"""
query = Query(language, query_string)
```

#### Properties

- `capture_count: int`: Number of captures
- `pattern_count: int`: Number of patterns
- `string_count: int`: Number of string literals

#### Methods

- `start_byte_for_pattern(pattern_index: int) -> int`: Get start byte for pattern
- `predicates_for_pattern(pattern_index: int) -> List[QueryPredicateStep]`: Get predicates for pattern
- `capture_name_for_id(capture_id: int) -> Optional[str]`: Get capture name by ID
- `string_value_for_id(string_id: int) -> Optional[str]`: Get string value by ID
- `quantifier_for_capture(pattern_index: int, capture_index: int) -> Quantifier`: Get quantifier for capture
- `is_pattern_rooted(pattern_index: int) -> bool`: Check if pattern is rooted
- `is_pattern_non_local(pattern_index: int) -> bool`: Check if pattern is non-local
- `is_pattern_guaranteed_at_step(byte_offset: int) -> bool`: Check if pattern is guaranteed at step
- `disable_capture(name: str) -> None`: Disable a capture
- `disable_pattern(pattern_index: int) -> None`: Disable a pattern

### QueryCursor

A cursor for executing queries on syntax trees.

```python
from delphi_tree_sitter import QueryCursor

cursor = QueryCursor()
cursor.execute(query, root_node)

while True:
    match = cursor.next_match()
    if match is None:
        break
    print(f"Match: {match.pattern_id}")
```

#### Methods

- `execute(query: Query, node: Node) -> None`: Execute a query
- `did_exceed_match_limit() -> bool`: Check if match limit exceeded
- `set_match_limit(limit: int) -> None`: Set match limit
- `get_match_limit() -> int`: Get match limit
- `set_max_start_depth(max_start_depth: int) -> None`: Set max start depth
- `set_byte_range(start_byte: int, end_byte: int) -> None`: Set byte range
- `set_point_range(start_point: Point, end_point: Point) -> None`: Set point range
- `next_match() -> Optional[QueryMatch]`: Get next match
- `next_capture() -> Optional[tuple[QueryMatch, int]]`: Get next capture
- `remove_match(match_id: int) -> None`: Remove a match

## Types and Enums

### Point

Represents a point in source code (row, column).

```python
from delphi_tree_sitter import Point, create_point

point = create_point(10, 5)  # Row 10, column 5
print(f"Row: {point.row}, Column: {point.column}")
```

### Range

Represents a range in source code.

```python
from delphi_tree_sitter import Range, create_range, create_point

start = create_point(0, 0)
end = create_point(5, 10)
range_obj = create_range(start, end, 0, 50)
```

### Input

Input configuration for parsing.

```python
from delphi_tree_sitter import Input, create_input_from_string

input_obj = create_input_from_string("def example(): pass")
```

### Enums

- `InputEncoding`: UTF8, UTF16
- `SymbolType`: REGULAR, ANONYMOUS, AUXILIARY
- `Quantifier`: ZERO, ZERO_OR_ONE, ZERO_OR_MORE, ONE, ONE_OR_MORE
- `QueryError`: NONE, SYNTAX, NODE_TYPE, FIELD, CAPTURE, STRUCTURE, LANGUAGE

## Exceptions

- `TreeSitterException`: Base exception
- `TreeSitterParseError`: Parse-related errors
- `TreeSitterQueryError`: Query-related errors
- `TreeSitterLanguageError`: Language-related errors
- `TreeSitterLibraryError`: Library-related errors

## Advanced Features

### LookAheadIterator

For generating completion suggestions and error diagnostics.

```python
from delphi_tree_sitter import LookAheadIterator

iterator = LookAheadIterator(language, state_id)
for symbol in iterator:
    print(f"Symbol: {iterator.current_symbol_name()}")
```

### WebAssembly Support

```python
from delphi_tree_sitter import WasmEngine, WasmStore, WasmParser

engine = WasmEngine()
store = WasmStore(engine)
language = store.load_language("python", wasm_data)

parser = WasmParser(store)
parser.set_language(language)
```

## Utility Functions

### Tree Walking

```python
from delphi_tree_sitter import TreeWalker

walker = TreeWalker(root_node)
functions = walker.find_nodes_by_type("function_definition")
```

### Query Building

```python
from delphi_tree_sitter import QueryBuilder

builder = QueryBuilder()
query = builder.add_capture("function", "function_definition").build()
```

### Input Creation

```python
from delphi_tree_sitter import create_input_from_string, create_input_from_file

# From string
input_obj = create_input_from_string("def example(): pass")

# From file
input_obj = create_input_from_file("example.py")
```

### Point and Range Utilities

```python
from delphi_tree_sitter import create_point, create_range, point_to_string, range_to_string

point = create_point(10, 5)
range_obj = create_range(point, point, 0, 10)

print(point_to_string(point))
print(range_to_string(range_obj))
```

## Examples

See the `examples/` directory for comprehensive examples demonstrating all features of the library.

### Basic Usage

```python
from delphi_tree_sitter import Parser, Language

# Create parser and load language
parser = Parser()
language = Language.from_library("path/to/language.so", "tree_sitter_python")
parser.set_language(language)

# Parse source code
source_code = "def hello(): print('Hello, World!')"
tree = parser.parse_string(source_code)

# Navigate the tree
root = tree.root_node
print(f"Root type: {root.type}")

# Use queries
from delphi_tree_sitter import Query, QueryCursor

query = Query(language, "(function_definition) @function")
cursor = QueryCursor()
cursor.execute(query, root)

while True:
    match = cursor.next_match()
    if match is None:
        break
    print(f"Found function: {match.pattern_id}")
```

### Advanced Usage

```python
from delphi_tree_sitter import TreeWalker, QueryBuilder, create_input_from_file

# Tree walking
walker = TreeWalker(root)
functions = walker.find_nodes_by_type("function_definition")

# Query building
builder = QueryBuilder()
query_string = builder.add_capture("function", "function_definition").build()

# File input
input_obj = create_input_from_file("source.py")
tree = parser.parse(input_obj)
```

## Notes

This is a comprehensive Python binding for tree-sitter that covers all the functionality available in the original C library. The implementation includes placeholder methods that would need to be connected to the actual tree-sitter C API using ctypes or similar binding mechanisms.

To use this library with real tree-sitter functionality, you would need to:

1. Load actual tree-sitter shared libraries
2. Implement the ctypes bindings to the C API
3. Load language grammars from shared libraries
4. Connect the placeholder methods to the actual C functions

The library is designed to be a complete and exhaustive implementation that matches the functionality of the original Delphi tree-sitter bindings.
