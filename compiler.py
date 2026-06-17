"""
OrbScript Bytecode Compiler
Converts AST into executable bytecode
"""

from ast import (
    ProgramNode, SetVariableNode, ShowVariableNode, SayNode,
    MathNode, IfNode, RepeatNode, FunctionDefNode, FunctionCallNode,
    StringLiteralNode, IntegerLiteralNode, VariableReferenceNode,
    ConditionNode, NodeType, Operator
)
from bytecode import Instruction, OpCode, BytecodeProgram

class CompilerError(Exception):
    """Exception raised for compilation errors"""
    def __init__(self, message: str, node=None):
        self.message = message
        self.node = node
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        if self.node:
            return f"Compiler Error in {self.node.source_file}:{self.node.line_number}: {self.message}"
        return f"Compiler Error: {self.message}"

class Compiler:
    """Compiles AST into bytecode"""
    
    def __init__(self):
        self.program = BytecodeProgram()
        self.current_function = None
        self.function_bodies = {}
    
    def compile(self, ast: ProgramNode) -> BytecodeProgram:
        """Compile an AST into bytecode"""
        for statement in ast.statements:
            self.compile_statement(statement)
        
        # Add HALT instruction at the end
        self.program.add_instruction(Instruction(OpCode.HALT))
        
        # Add function definitions
        for func_name, body in self.function_bodies.items():
            self.program.functions[func_name] = len(self.program.instructions)
            for stmt in body:
                self.compile_statement(stmt)
            self.program.add_instruction(Instruction(OpCode.RETURN))
        
        return self.program
    
    def compile_statement(self, statement):
        """Compile a single statement"""
        if isinstance(statement, SetVariableNode):
            self.compile_set(statement)
        elif isinstance(statement, ShowVariableNode):
            self.compile_show(statement)
        elif isinstance(statement, SayNode):
            self.compile_say(statement)
        elif isinstance(statement, MathNode):
            self.compile_math(statement)
        elif isinstance(statement, IfNode):
            self.compile_if(statement)
        elif isinstance(statement, RepeatNode):
            self.compile_repeat(statement)
        elif isinstance(statement, FunctionDefNode):
            self.compile_function_def(statement)
        elif isinstance(statement, FunctionCallNode):
            self.compile_function_call(statement)
    
    def compile_set(self, node: SetVariableNode):
        """Compile variable assignment"""
        # Push value onto stack
        self.compile_expression(node.value)
        
        # Store to variable
        self.program.add_instruction(Instruction(
            OpCode.STORE_VAR,
            node.name,
            node.line_number,
            node.source_file
        ))
    
    def compile_show(self, node: ShowVariableNode):
        """Compile variable display"""
        self.program.add_instruction(Instruction(
            OpCode.PRINT_VAR,
            node.name,
            node.line_number,
            node.source_file
        ))
    
    def compile_say(self, node: SayNode):
        """Compile print statement"""
        self.compile_expression(node.expression)
        self.program.add_instruction(Instruction(
            OpCode.PRINT,
            line_number=node.line_number,
            source_file=node.source_file
        ))
    
    def compile_math(self, node: MathNode):
        """Compile mathematical operation"""
        # Push operands onto stack
        self.compile_expression(node.left)
        self.compile_expression(node.right)
        
        # Perform operation
        opcode_map = {
            NodeType.ADD: OpCode.ADD,
            NodeType.SUB: OpCode.SUB,
            NodeType.MUL: OpCode.MUL,
            NodeType.DIV: OpCode.DIV,
        }
        
        self.program.add_instruction(Instruction(
            opcode_map[node.type],
            line_number=node.line_number,
            source_file=node.source_file
        ))
    
    def compile_if(self, node: IfNode):
        """Compile conditional statement"""
        # Compile condition
        self.compile_condition(node.condition)
        
        # Add jump if false (skip the body)
        jump_if_false_pos = len(self.program.instructions)
        self.program.add_instruction(Instruction(
            OpCode.JUMP_IF_FALSE,
            None,  # Will be backpatched
            node.line_number,
            node.source_file
        ))
        
        # Compile body
        for stmt in node.body:
            self.compile_statement(stmt)
        
        # Backpatch the jump
        self.program.instructions[jump_if_false_pos].operand = len(self.program.instructions)
    
    def compile_repeat(self, node: RepeatNode):
        """Compile loop statement"""
        # Push counter onto stack
        counter_var = f"__repeat_counter_{node.line_number}"
        self.program.add_instruction(Instruction(
            OpCode.PUSH_INTEGER,
            0,
            node.line_number,
            node.source_file
        ))
        self.program.add_instruction(Instruction(
            OpCode.STORE_VAR,
            counter_var,
            node.line_number,
            node.source_file
        ))
        
        # Start of loop
        loop_start = len(self.program.instructions)
        
        # Load counter and compare
        self.program.add_instruction(Instruction(
            OpCode.LOAD_VAR,
            counter_var,
            node.line_number,
            node.source_file
        ))
        self.program.add_instruction(Instruction(
            OpCode.PUSH_INTEGER,
            node.count,
            node.line_number,
            node.source_file
        ))
        self.program.add_instruction(Instruction(
            OpCode.COMPARE_LT,
            line_number=node.line_number,
            source_file=node.source_file
        ))
        
        # Jump if false (exit loop)
        jump_if_false_pos = len(self.program.instructions)
        self.program.add_instruction(Instruction(
            OpCode.JUMP_IF_FALSE,
            None,  # Will be backpatched
            node.line_number,
            node.source_file
        ))
        
        # Execute body
        for stmt in node.body:
            self.compile_statement(stmt)
        
        # Increment counter
        self.program.add_instruction(Instruction(
            OpCode.LOAD_VAR,
            counter_var,
            node.line_number,
            node.source_file
        ))
        self.program.add_instruction(Instruction(
            OpCode.PUSH_INTEGER,
            1,
            node.line_number,
            node.source_file
        ))
        self.program.add_instruction(Instruction(
            OpCode.ADD,
            line_number=node.line_number,
            source_file=node.source_file
        ))
        self.program.add_instruction(Instruction(
            OpCode.STORE_VAR,
            counter_var,
            node.line_number,
            node.source_file
        ))
        
        # Jump back to start
        self.program.add_instruction(Instruction(
            OpCode.JUMP,
            loop_start,
            node.line_number,
            node.source_file
        ))
        
        # Backpatch the exit jump
        self.program.instructions[jump_if_false_pos].operand = len(self.program.instructions)
    
    def compile_function_def(self, node: FunctionDefNode):
        """Compile function definition"""
        self.function_bodies[node.name] = node.body
    
    def compile_function_call(self, node: FunctionCallNode):
        """Compile function call"""
        self.program.add_instruction(Instruction(
            OpCode.CALL_FUNC,
            node.name,
            node.line_number,
            node.source_file
        ))
    
    def compile_expression(self, expression):
        """Compile an expression"""
        if isinstance(expression, StringLiteralNode):
            self.program.add_instruction(Instruction(
                OpCode.PUSH_STRING,
                expression.value,
                expression.line_number,
                expression.source_file
            ))
        elif isinstance(expression, IntegerLiteralNode):
            self.program.add_instruction(Instruction(
                OpCode.PUSH_INTEGER,
                expression.value,
                expression.line_number,
                expression.source_file
            ))
        elif isinstance(expression, VariableReferenceNode):
            self.program.add_instruction(Instruction(
                OpCode.LOAD_VAR,
                expression.name,
                expression.line_number,
                expression.source_file
            ))
    
    def compile_condition(self, condition: ConditionNode):
        """Compile a comparison condition"""
        self.compile_expression(condition.left)
        self.compile_expression(condition.right)
        
        opcode_map = {
            Operator.EQUALS: OpCode.COMPARE_EQ,
            Operator.NOT_EQUALS: OpCode.COMPARE_NE,
            Operator.GREATER: OpCode.COMPARE_GT,
            Operator.LESS: OpCode.COMPARE_LT,
            Operator.GREATER_EQUAL: OpCode.COMPARE_GTE,
            Operator.LESS_EQUAL: OpCode.COMPARE_LTE,
        }
        
        self.program.add_instruction(Instruction(
            opcode_map[condition.operator],
            line_number=condition.line_number,
            source_file=condition.source_file
        ))