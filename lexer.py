"""
OrbScript Lexer (Tokenizer)
Converts source code into tokens for parsing
"""

from enum import Enum, auto
from typing import List
from dataclasses import dataclass

class TokenType(Enum):
    """Types of tokens in OrbScript"""
    # Keywords
    SET = auto()
    SHOW = auto()
    SAY = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    IF = auto()
    ENDIF = auto()
    REPEAT = auto()
    ENDREPEAT = auto()
    FUNC = auto()
    ENDFUNC = auto()
    CALL = auto()
    
    # Literals
    STRING = auto()
    INTEGER = auto()
    IDENTIFIER = auto()
    
    # Operators
    EQUALS = auto()
    NOT_EQUALS = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    
    # Special
    COMMENT = auto()
    NEWLINE = auto()
    EOF = auto()
    ERROR = auto()

@dataclass
class Token:
    """Represents a single token from the lexer"""
    type: TokenType
    value: str
    line: int
    column: int
    source_file: str = ""

class LexerError(Exception):
    """Exception raised for lexer errors"""
    def __init__(self, message: str, line: int, column: int, source_file: str = ""):
        self.message = message
        self.line = line
        self.column = column
        self.source_file = source_file
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        return f"Lexer Error in {self.source_file}:{self.line}:{self.column}: {self.message}"

class Lexer:
    """Tokenizer for OrbScript source code"""
    
    KEYWORDS = {
        'set': TokenType.SET,
        'show': TokenType.SHOW,
        'say': TokenType.SAY,
        'add': TokenType.ADD,
        'sub': TokenType.SUB,
        'mul': TokenType.MUL,
        'div': TokenType.DIV,
        'if': TokenType.IF,
        'endif': TokenType.ENDIF,
        'repeat': TokenType.REPEAT,
        'endrepeat': TokenType.ENDREPEAT,
        'func': TokenType.FUNC,
        'endfunc': TokenType.ENDFUNC,
        'call': TokenType.CALL,
    }
    
    def __init__(self, source: str, source_file: str = ""):
        self.source = source
        self.source_file = source_file
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Convert source code into a list of tokens"""
        while self.position < len(self.source):
            char = self.source[self.position]
            
            # Skip whitespace (except newlines)
            if char in ' \t\r':
                self.advance()
                continue
            
            # Handle newlines
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column, self.source_file))
                self.line += 1
                self.column = 1
                self.advance()
                continue
            
            # Handle comments
            if char == '#':
                self.tokenize_comment()
                continue
            
            # Handle strings
            if char == '"':
                self.tokenize_string()
                continue
            
            # Handle numbers
            if char.isdigit():
                self.tokenize_number()
                continue
            
            # Handle operators (two-character first)
            if self.position + 1 < len(self.source):
                two_char = self.source[self.position:self.position + 2]
                if two_char == '==':
                    self.tokens.append(Token(TokenType.EQUALS, '==', self.line, self.column, self.source_file))
                    self.advance(2)
                    continue
                elif two_char == '!=':
                    self.tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.line, self.column, self.source_file))
                    self.advance(2)
                    continue
                elif two_char == '>=':
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column, self.source_file))
                    self.advance(2)
                    continue
                elif two_char == '<=':
                    self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line, self.column, self.source_file))
                    self.advance(2)
                    continue
            
            # Handle single-character operators
            if char == '>':
                self.tokens.append(Token(TokenType.GREATER, '>', self.line, self.column, self.source_file))
                self.advance()
                continue
            elif char == '<':
                self.tokens.append(Token(TokenType.LESS, '<', self.line, self.column, self.source_file))
                self.advance()
                continue
            
            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokenize_identifier()
                continue
            
            # Unknown character
            raise LexerError(
                f"Unexpected character: '{char}'",
                self.line,
                self.column,
                self.source_file
            )
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column, self.source_file))
        return self.tokens
    
    def advance(self, steps: int = 1):
        """Move position forward"""
        self.position += steps
        if steps == 1:
            self.column += 1
        else:
            self.column += steps
    
    def tokenize_comment(self):
        """Handle comment tokens"""
        start_column = self.column
        self.advance()  # Skip #
        
        comment_text = ""
        while self.position < len(self.source) and self.source[self.position] != '\n':
            comment_text += self.source[self.position]
            self.advance()
        
        self.tokens.append(Token(TokenType.COMMENT, comment_text.strip(), self.line, start_column, self.source_file))
    
    def tokenize_string(self):
        """Handle string literal tokens"""
        start_column = self.column
        self.advance()  # Skip opening quote
        
        string_value = ""
        while self.position < len(self.source) and self.source[self.position] != '"':
            if self.source[self.position] == '\\':
                self.advance()
                if self.position < len(self.source):
                    escape_char = self.source[self.position]
                    if escape_char == 'n':
                        string_value += '\n'
                    elif escape_char == 't':
                        string_value += '\t'
                    elif escape_char == '"':
                        string_value += '"'
                    elif escape_char == '\\':
                        string_value += '\\'
                    else:
                        string_value += escape_char
                    self.advance()
                else:
                    raise LexerError("Unterminated string", self.line, start_column, self.source_file)
            else:
                string_value += self.source[self.position]
                self.advance()
        
        if self.position >= len(self.source):
            raise LexerError("Unterminated string", self.line, start_column, self.source_file)
        
        self.advance()  # Skip closing quote
        self.tokens.append(Token(TokenType.STRING, string_value, self.line, start_column, self.source_file))
    
    def tokenize_number(self):
        """Handle integer literal tokens"""
        start_column = self.column
        number_value = ""
        
        while self.position < len(self.source) and self.source[self.position].isdigit():
            number_value += self.source[self.position]
            self.advance()
        
        self.tokens.append(Token(TokenType.INTEGER, int(number_value), self.line, start_column, self.source_file))
    
    def tokenize_identifier(self):
        """Handle identifier and keyword tokens"""
        start_column = self.column
        identifier = ""
        
        while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
            identifier += self.source[self.position]
            self.advance()
        
        # Check if it's a keyword
        token_type = self.KEYWORDS.get(identifier.lower(), TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, identifier, self.line, start_column, self.source_file))