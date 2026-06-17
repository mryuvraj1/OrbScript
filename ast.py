"""
OrbScript Abstract Syntax Tree Node Definitions
Defines all possible AST nodes for the language
"""

from dataclasses import dataclass
from typing import List, Any, Optional
from enum import Enum, auto

class NodeType(Enum):
    """Enumeration of all AST node types"""
    PROGRAM = auto()
    SET_VARIABLE = auto()
    SHOW_VARIABLE = auto()
    SAY = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    IF = auto()
    REPEAT = auto()
    FUNCTION_DEF = auto()
    FUNCTION_CALL = auto()
    COMMENT = auto()
    STRING_LITERAL = auto()
    INTEGER_LITERAL = auto()
    VARIABLE_REFERENCE = auto()
    CONDITION = auto()
    BLOCK = auto()

class Operator(Enum):
    """Comparison operators for conditions"""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER = ">"
    LESS = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="

@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    type: NodeType
    line_number: int
    source_file: str

@dataclass
class ProgramNode(ASTNode):
    """Root node of the program"""
    statements: List[ASTNode]
    
    def __init__(self, statements: List[ASTNode], line_number: int = 0, source_file: str = ""):
        super().__init__(NodeType.PROGRAM, line_number, source_file)
        self.statements = statements

@dataclass
class SetVariableNode(ASTNode):
    """Variable assignment: set name value"""
    name: str
    value: Any
    
    def __init__(self, name: str, value: Any, line_number: int, source_file: str = ""):
        super().__init__(NodeType.SET_VARIABLE, line_number, source_file)
        self.name = name
        self.value = value

@dataclass
class ShowVariableNode(ASTNode):
    """Variable display: show name"""
    name: str
    
    def __init__(self, name: str, line_number: int, source_file: str = ""):
        super().__init__(NodeType.SHOW_VARIABLE, line_number, source_file)
        self.name = name

@dataclass
class SayNode(ASTNode):
    """Print statement: say expression"""
    expression: Any
    
    def __init__(self, expression: Any, line_number: int, source_file: str = ""):
        super().__init__(NodeType.SAY, line_number, source_file)
        self.expression = expression

@dataclass
class MathNode(ASTNode):
    """Mathematical operation"""
    left: Any
    right: Any
    
    def __init__(self, type: NodeType, left: Any, right: Any, line_number: int, source_file: str = ""):
        super().__init__(type, line_number, source_file)
        self.left = left
        self.right = right

@dataclass
class IfNode(ASTNode):
    """Conditional statement"""
    condition: 'ConditionNode'
    body: List[ASTNode]
    
    def __init__(self, condition: 'ConditionNode', body: List[ASTNode], line_number: int, source_file: str = ""):
        super().__init__(NodeType.IF, line_number, source_file)
        self.condition = condition
        self.body = body

@dataclass
class RepeatNode(ASTNode):
    """Loop statement"""
    count: int
    body: List[ASTNode]
    
    def __init__(self, count: int, body: List[ASTNode], line_number: int, source_file: str = ""):
        super().__init__(NodeType.REPEAT, line_number, source_file)
        self.count = count
        self.body = body

@dataclass
class FunctionDefNode(ASTNode):
    """Function definition"""
    name: str
    body: List[ASTNode]
    
    def __init__(self, name: str, body: List[ASTNode], line_number: int, source_file: str = ""):
        super().__init__(NodeType.FUNCTION_DEF, line_number, source_file)
        self.name = name
        self.body = body

@dataclass
class FunctionCallNode(ASTNode):
    """Function call"""
    name: str
    
    def __init__(self, name: str, line_number: int, source_file: str = ""):
        super().__init__(NodeType.FUNCTION_CALL, line_number, source_file)
        self.name = name

@dataclass
class StringLiteralNode(ASTNode):
    """String literal value"""
    value: str
    
    def __init__(self, value: str, line_number: int, source_file: str = ""):
        super().__init__(NodeType.STRING_LITERAL, line_number, source_file)
        self.value = value

@dataclass
class IntegerLiteralNode(ASTNode):
    """Integer literal value"""
    value: int
    
    def __init__(self, value: int, line_number: int, source_file: str = ""):
        super().__init__(NodeType.INTEGER_LITERAL, line_number, source_file)
        self.value = value

@dataclass
class VariableReferenceNode(ASTNode):
    """Reference to a variable"""
    name: str
    
    def __init__(self, name: str, line_number: int, source_file: str = ""):
        super().__init__(NodeType.VARIABLE_REFERENCE, line_number, source_file)
        self.name = name

@dataclass
class ConditionNode(ASTNode):
    """Comparison condition"""
    left: Any
    operator: Operator
    right: Any
    
    def __init__(self, left: Any, operator: Operator, right: Any, line_number: int, source_file: str = ""):
        super().__init__(NodeType.CONDITION, line_number, source_file)
        self.left = left
        self.operator = operator
        self.right = right