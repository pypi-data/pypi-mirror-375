# Delphi Tree Sitter Python Library

A Python library providing bindings for tree-sitter parsers, enabling powerful syntax analysis and code manipulation capabilities.

## Features

- **Parser**: Parse source code into syntax trees
- **Language Support**: Work with different programming languages
- **Tree Navigation**: Traverse and analyze syntax trees
- **Query System**: Find patterns in code using tree-sitter queries
- **Node Inspection**: Access detailed information about syntax nodes

## Installation

### From Source

```bash
git clone https://github.com/yourusername/delphi-tree-sitter.git
cd delphi-tree-sitter/python
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/delphi-tree-sitter.git
cd delphi-tree-sitter/python
pip install -e ".[dev]"
```

## Quick Start

```python
from delphi_tree_sitter import Parser, Language

# Create a parser
parser = Parser()

# Set the language (you'll need to load a language library)
# language = Language.from_library("path/to/language.so")
# parser.set_language(language)

# Parse some code
source_code = """
def hello_world():
    print("Hello, World!")
"""

# tree = parser.parse(source_code)
# root = tree.root_node
# print(f"Root node type: {root.type}")
```

## API Reference

### Parser

The `Parser` class is the main entry point for parsing source code.

```python
from delphi_tree_sitter import Parser

parser = Parser()
parser.set_language(language)
tree = parser.parse(source_code)
```

### Tree and Node

Work with syntax trees and their nodes:

```python
tree = parser.parse(source_code)
root = tree.root_node

# Navigate the tree
for child in root.children():
    print(f"Child type: {child.type}")
    print(f"Child text: {child.text}")
```

### Query System

Find patterns in code using tree-sitter queries:

```python
from delphi_tree_sitter import Query, QueryCursor

query = Query(language, """
(function_definition
  name: (identifier) @function_name
  body: (block) @function_body)
""")

cursor = QueryCursor()
cursor.execute(query, tree.root_node)

while True:
    match = cursor.next_match()
    if match is None:
        break
    
    function_name = match.captures.get("function_name")
    function_body = match.captures.get("function_body")
    print(f"Found function: {function_name.text}")
```

## Language Support

This library supports any language that has a tree-sitter grammar. Popular languages include:

- Python
- JavaScript/TypeScript
- C/C++
- Java
- Go
- Rust
- And many more...

To use a language, you need to load its tree-sitter grammar library.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black delphi_tree_sitter/
```

### Type Checking

```bash
mypy delphi_tree_sitter/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [tree-sitter](https://github.com/tree-sitter/tree-sitter) - The core tree-sitter library
- [tree-sitter-python](https://github.com/tree-sitter/tree-sitter-python) - Python grammar for tree-sitter
- [tree-sitter-javascript](https://github.com/tree-sitter/tree-sitter-javascript) - JavaScript grammar for tree-sitter
