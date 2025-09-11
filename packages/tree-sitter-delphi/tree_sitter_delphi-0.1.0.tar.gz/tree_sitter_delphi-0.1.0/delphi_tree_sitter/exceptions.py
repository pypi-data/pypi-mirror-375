"""
Exceptions for the delphi-tree-sitter library.
"""


class TreeSitterException(Exception):
    """Base exception for tree-sitter related errors."""
    pass


class TreeSitterParseError(TreeSitterException):
    """Exception raised when parsing fails."""
    pass


class TreeSitterQueryError(TreeSitterException):
    """Exception raised when query operations fail."""
    
    def __init__(self, message: str, error_type: int = 0, error_offset: int = 0):
        """
        Initialize query error.
        
        Args:
            message: Error message
            error_type: Type of query error
            error_offset: Byte offset where error occurred
        """
        super().__init__(message)
        self.error_type = error_type
        self.error_offset = error_offset


class TreeSitterLanguageError(TreeSitterException):
    """Exception raised when language operations fail."""
    pass


class TreeSitterLibraryError(TreeSitterException):
    """Exception raised when tree-sitter library operations fail."""
    pass
