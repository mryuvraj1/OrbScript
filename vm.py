"""
OrbScript Virtual Machine
Executes compiled bytecode
"""

cat > vm.py << 'ENDOFFILE'
# Paste the full code content
ENDOFFILE

from typing import Any, Dict, List
from bytecode import Instruction, OpCode, BytecodeProgram

class VMError(Exception):
    """Exception raised for runtime errors"""
    def __init__(self, message: str, instruction: Instruction = None):
        self.message = message
        self.instruction = instruction
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        if self.instruction:
            return f"Runtime Error in {self.instruction.source_file}:{self.instruction.line_number}: {self.message}"
        return f"Runtime Error: {self.message}"

class VirtualMachine:
    """Executes OrbScript bytecode"""
    
    def __init__(self):
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.program_counter: int = 0
        self.program: BytecodeProgram = None
        self.running: bool = False
        self.call_stack: List[int] = []
    
    def execute(self, program: BytecodeProgram):
        """Execute a bytecode program"""
        self.program = program
        self.program_counter = 0
        self.running = True
        self.variables.clear()
        self.stack.clear()
        self.call_stack.clear()
        
        try:
            while self.running and self.program_counter < len(self.program.instructions):
                instruction = self.program.instructions[self.program_counter]
                self.execute_instruction(instruction)
                self.program_counter += 1
        except VMError as e:
            print(f"Error: {e}")
            raise
    
    def execute_instruction(self, instruction: Instruction):
        """Execute a single instruction"""
        opcode = instruction.opcode
        
        if opcode == OpCode.PUSH_STRING:
            self.stack.append(str(instruction.operand))
        
        elif opcode == OpCode.PUSH_INTEGER:
            self.stack.append(int(instruction.operand))
        
        elif opcode == OpCode.POP:
            if self.stack:
                self.stack.pop()
            else:
                raise VMError("Cannot pop from empty stack", instruction)
        
        elif opcode == OpCode.STORE_VAR:
            if not self.stack:
                raise VMError("Stack is empty, cannot store variable", instruction)
            value = self.stack.pop()
            self.variables[instruction.operand] = value
        
        elif opcode == OpCode.LOAD_VAR:
            name = instruction.operand
            if name not in self.variables:
                raise VMError(f"Variable '{name}' is not defined", instruction)
            self.stack.append(self.variables[name])
        
        elif opcode == OpCode.ADD:
            self.binary_arithmetic(lambda a, b: a + b, "Cannot add", instruction)
        
        elif opcode == OpCode.SUB:
            self.binary_arithmetic(lambda a, b: a - b, "Cannot subtract", instruction)
        
        elif opcode == OpCode.MUL:
            self.binary_arithmetic(lambda a, b: a * b, "Cannot multiply", instruction)
        
        elif opcode == OpCode.DIV:
            def safe_divide(a, b):
                if b == 0:
                    raise VMError("Division by zero", instruction)
                return a / b
            self.binary_arithmetic(safe_divide, "Cannot divide", instruction)
        
        elif opcode == OpCode.PRINT:
            if not self.stack:
                raise VMError("Stack is empty, cannot print", instruction)
            value = self.stack.pop()
            print(value)
        
        elif opcode == OpCode.PRINT_VAR:
            name = instruction.operand
            if name not in self.variables:
                raise VMError(f"Variable '{name}' is not defined", instruction)
            print(self.variables[name])
        
        elif opcode == OpCode.JUMP:
            self.program_counter = instruction.operand - 1  # -1 because we increment after
        
        elif opcode == OpCode.JUMP_IF_TRUE:
            if not self.stack:
                raise VMError("Stack is empty, cannot evaluate condition", instruction)
            condition = self.stack.pop()
            if condition:
                self.program_counter = instruction.operand - 1
        
        elif opcode == OpCode.JUMP_IF_FALSE:
            if not self.stack:
                raise VMError("Stack is empty, cannot evaluate condition", instruction)
            condition = self.stack.pop()
            if not condition:
                self.program_counter = instruction.operand - 1
        
        elif opcode == OpCode.COMPARE_EQ:
            self.compare_operation(lambda a, b: a == b, instruction)
        
        elif opcode == OpCode.COMPARE_NE:
            self.compare_operation(lambda a, b: a != b, instruction)
        
        elif opcode == OpCode.COMPARE_GT:
            self.compare_operation(lambda a, b: a > b, instruction)
        
        elif opcode == OpCode.COMPARE_LT:
            self.compare_operation(lambda a, b: a < b, instruction)
        
        elif opcode == OpCode.COMPARE_GTE:
            self.compare_operation(lambda a, b: a >= b, instruction)
        
        elif opcode == OpCode.COMPARE_LTE:
            self.compare_operation(lambda a, b: a <= b, instruction)
        
        elif opcode == OpCode.CALL_FUNC:
            func_name = instruction.operand
            if func_name not in self.program.functions:
                raise VMError(f"Function '{func_name}' is not defined", instruction)
            
            # Save return address
            self.call_stack.append(self.program_counter)
            
            # Jump to function
            self.program_counter = self.program.functions[func_name] - 1
        
        elif opcode == OpCode.RETURN:
            if self.call_stack:
                self.program_counter = self.call_stack.pop()
            else:
                self.running = False
        
        elif opcode == OpCode.HALT:
            self.running = False
        
        else:
            raise VMError(f"Unknown opcode: {opcode}", instruction)
    
    def binary_arithmetic(self, operation, error_msg, instruction):
        """Perform binary arithmetic operation"""
        if len(self.stack) < 2:
            raise VMError(f"Stack underflow: {error_msg} requires 2 values", instruction)
        
        b = self.stack.pop()
        a = self.stack.pop()
        
        # Convert to appropriate types
        if isinstance(a, str) or isinstance(b, str):
            # String concatenation for ADD
            if instruction.opcode == OpCode.ADD:
                result = str(a) + str(b)
            else:
                raise VMError(f"{error_msg} strings", instruction)
        else:
            result = operation(a, b)
        
        self.stack.append(result)
    
    def compare_operation(self, operation, instruction):
        """Perform comparison operation"""
        if len(self.stack) < 2:
            raise VMError("Stack underflow: comparison requires 2 values", instruction)
        
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(operation(a, b))