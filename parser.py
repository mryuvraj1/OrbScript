"""
OrbScript Parser
Converts tokens into an Abstract Syntax Tree (AST)
"""

from typing import List, Optional
from lexer import Token, TokenType, LexerError
from ast import (
    ProgramNode, SetVariableNode, ShowVariableNode, SayNode,
    MathNode, IfNode, RepeatNode, FunctionDefNode, FunctionCallNode,
    StringLiteralNode, IntegerLiteralNode, VariableReferenceNode,
    ConditionNode, NodeType, Operator
)

class ParserError(Exception):
    """Exception raised for parsing errors"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        return f"Parser Error in {self.token.source_file}:{self.token.line}:{self.token.column}: {self.message}\n  Got token: {self.token.type.name} '{self.token.value}'"

class Parser:
    """Recursive descent parser for OrbScript"""
    
    def __init__(self, tokens: List[Token], source_file: str = ""):
        self.tokens = tokens
        self.source_file = source_file
        self.current = 0
        # Filter out comments and newlines for easier parsing
        self.relevant_tokens = [t for t in tokens if t.type not in [TokenType.COMMENT, TokenType.NEWLINE]]
    
    def parse(self) -> ProgramNode:
        """Parse the token stream into an AST"""
        statements = []
        
        while not self.is_at_end():
            try:
                statement = self.parse_statement()
                if statement:
                    statements.append(statement)
            except ParserError as e:
                print(f"Warning: {e}")
                self.synchronize()
        
        return ProgramNode(statements, source_file=self.source_file)
    
    def parse_statement(self):
        """Parse a single statement"""
        token = self.peek()
        
        if token.type == TokenType.SET:
            return self.parse_set()
        elif token.type == TokenType.SHOW:
            return self.parse_show()
        elif token.type == TokenType.SAY:
            return self.parse_say()
        elif token.type == TokenType.ADD:
            return self.parse_math(NodeType.ADD)
        elif token.type == TokenType.SUB:
            return self.parse_math(NodeType.SUB)
        elif token.type == TokenType.MUL:
            return self.parse_math(NodeType.MUL)
        elif token.type == TokenType.DIV:
            return self.parse_math(NodeType.DIV)
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.REPEAT:
            return self.parse_repeat()
        elif token.type == TokenType.FUNC:
            return self.parse_function_def()
        elif token.type == TokenType.CALL:
            return self.parse_function_call()
        else:
            raise ParserError(f"Unexpected token at start of statement", token)
    
    def parse_set(self) -> SetVariableNode:
        """Parse variable assignment: set name value"""
        set_token = self.consume(TokenType.SET, "Expected 'set'")
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'set'")
        
        value = self.parse_expression()
        
        return SetVariableNode(
            name=name_token.value,
            value=value,
            line_number=set_token.line,
            source_file=self.source_file
        )
    
    def parse_show(self) -> ShowVariableNode:
        """Parse variable display: show name"""
        show_token = self.consume(TokenType.SHOW, "Expected 'show'")
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'show'")
        
        return ShowVariableNode(
            name=name_token.value,
            line_number=show_token.line,
            source_file=self.source_file
        )
    
    def parse_say(self) -> SayNode:
        """Parse print statement: say expression"""
        say_token = self.consume(TokenType.SAY, "Expected 'say'")
        expression = self.parse_expression()
        
        return SayNode(
            expression=expression,
            line_number=say_token.line,
            source_file=self.source_file
        )
    
    def parse_math(self, operation_type: NodeType):
        """Parse mathematical operation: add/sub/mul/div left right"""
        op_token = self.advance()  # Consume the operator
        
        left = self.parse_expression()
        right = self.parse_expression()
        
        return MathNode(
            type=operation_type,
            left=left,
            right=right,
            line_number=op_token.line,
            source_file=self.source_file
        )
    
    def parse_if(self) -> IfNode:
        """Parse conditional: if condition ... endif"""
        if_token = self.consume(TokenType.IF, "Expected 'if'")
        
        condition = self.parse_condition()
        
        body = []
        while not self.check(TokenType.ENDIF) and not self.is_at_end():
            body.append(self.parse_statement())
        
        self.consume(TokenType.ENDIF, "Expected 'endif'")
        
        return IfNode(
            condition=condition,
            body=body,
            line_number=if_token.line,
            source_file=self.source_file
        )
    
    def parse_repeat(self) -> RepeatNode:
        """Parse loop: repeat count ... endrepeat"""
        repeat_token = self.consume(TokenType.REPEAT, "Expected 'repeat'")
        
        count_token = self.consume(TokenType.INTEGER, "Expected repeat count")
        
        body = []
        while not self.check(TokenType.ENDREPEAT) and not self.is_at_end():
            body.append(self.parse_statement())
        
        self.consume(TokenType.ENDREPEAT, "Expected 'endrepeat'")
        
        return RepeatNode(
            count=count_token.value,
            body=body,
            line_number=repeat_token.line,
            source_file=self.source_file
        )
    
    def parse_function_def(self) -> FunctionDefNode:
        """Parse function definition: func name ... endfunc"""
        func_token = self.consume(TokenType.FUNC, "Expected 'func'")
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        
        body = []
        while not self.check(TokenType.ENDFUNC) and not self.is_at_end():
            body.append(self.parse_statement())
        
        self.consume(TokenType.ENDFUNC, "Expected 'endfunc'")
        
        return FunctionDefNode(
            name=name_token.value,
            body=body,
            line_number=func_token.line,
            source_file=self.source_file
        )
    
    def parse_function_call(self) -> FunctionCallNode:
        """Parse function call: call name"""
        call_token = self.consume(TokenType.CALL, "Expected 'call'")
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        
        return FunctionCallNode(
            name=name_token.value,
            line_number=call_token.line,
            source_file=self.source_file
        )
    
    def parse_expression(self):
        """Parse an expression (value or variable reference)"""
        if self.check(TokenType.STRING):
            token = self.advance()
            return StringLiteralNode(
                value=token.value,
                line_number=token.line,
                source_file=self.source_file
            )
        elif self.check(TokenType.INTEGER):
            token = self.advance()
            return IntegerLiteralNode(
                value=token.value,
                line_number=token.line,
                source_file=self.source_file
            )
        elif self.check(TokenType.IDENTIFIER):
            token = self.advance()
            return VariableReferenceNode(
                name=token.value,
                line_number=token.line,
                source_file=self.source_file
            )
        else:
            raise ParserError("Expected expression (string, integer, or variable)", self.peek())
    
    def parse_condition(self) -> ConditionNode:
        """Parse a comparison condition"""
        left = self.parse_expression()
        
        operator_token = self.advance()
        operator = self.get_operator(operator_token)
        
        right = self.parse_expression()
        
        return ConditionNode(
            left=left,
            operator=operator,
            right=right,
            line_number=operator_token.line,
            source_file=self.source_file
        )
    
    def get_operator(self, token: Token) -> Operator:
        """Convert token to operator enum"""
        op_map = {
            TokenType.EQUALS: Operator.EQUALS,
            TokenType.NOT_EQUALS: Operator.NOT_EQUALS,
            TokenType.GREATER: Operator.GREATER,
            TokenType.LESS: Operator.LESS,
            TokenType.GREATER_EQUAL: Operator.GREATER_EQUAL,
            TokenType.LESS_EQUAL: Operator.LESS_EQUAL,
        }
        
        if token.type in op_map:
            return op_map[token.type]
        else:
            raise ParserError(f"Expected comparison operator, got {token.type.name}", token)
    
    def peek(self) -> Token:
        """Look at current token without consuming"""
        return self.relevant_tokens[self.current]
    
    def advance(self) -> Token:
        """Consume and return current token"""
        if not self.is_at_end():
            token = self.relevant_tokens[self.current]
            self.current += 1
            return token
        return self.relevant_tokens[-1]  # Return EOF token
    
    def check(self, token_type: TokenType) -> bool:
        """Check if current token matches type"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def consume(self, token_type: TokenType, error_message: str) -> Token:
        """Consume token if it matches expected type"""
        if self.check(token_type):
            return self.advance()
        
        raise ParserError(error_message, self.peek())
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end of tokens"""
        return self.current >= len(self.relevant_tokens) or self.peek().type == TokenType.EOF
    
    def synchronize(self):
        """Recover from parsing error by skipping to next statement"""
        self.advance()
        
        while not self.is_at_end():
            if self.peek().type in [
                TokenType.SET, TokenType.SHOW, TokenType.SAY,
                TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV,
                TokenType.IF, TokenType.REPEAT, TokenType.FUNC, TokenType.CALL
            ]:
                return
            self.advance()