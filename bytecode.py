cat > bytecode.py << 'ENDOFFILE'
# Paste the full code content
ENDOFFILE

"""
OrbScript Bytecode Definitions
Defines the instruction set for the virtual machine
"""

from enum import Enum, auto
from typing import List, Any
from dataclasses import dataclass
import struct
import json

class OpCode(Enum):
    """Bytecode operation codes"""
    # Stack operations
    PUSH_STRING = auto()    # Push string onto stack
    PUSH_INTEGER = auto()   # Push integer onto stack
    POP = auto()            # Pop value from stack
    
    # Variable operations
    STORE_VAR = auto()      # Store top of stack to variable
    LOAD_VAR = auto()       # Load variable onto stack
    
    # Arithmetic operations
    ADD = auto()            # Add top two stack values
    SUB = auto()            # Subtract top two stack values
    MUL = auto()            # Multiply top two stack values
    DIV = auto()            # Divide top two stack values
    
    # Output operations
    PRINT = auto()          # Print top of stack
    PRINT_VAR = auto()      # Print variable
    
    # Control flow
    JUMP = auto()           # Unconditional jump
    JUMP_IF_TRUE = auto()   # Jump if top of stack is true
    JUMP_IF_FALSE = auto()  # Jump if top of stack is false
    COMPARE_EQ = auto()     # Compare equality
    COMPARE_NE = auto()     # Compare not equal
    COMPARE_GT = auto()     # Compare greater than
    COMPARE_LT = auto()     # Compare less than
    COMPARE_GTE = auto()    # Compare greater than or equal
    COMPARE_LTE = auto()    # Compare less than or equal
    
    # Function operations
    DEFINE_FUNC = auto()    # Define function
    CALL_FUNC = auto()      # Call function
    RETURN = auto()         # Return from function
    
    # Program control
    HALT = auto()           # Stop execution

@dataclass
class Instruction:
    """Represents a single bytecode instruction"""
    opcode: OpCode
    operand: Any = None
    line_number: int = 0
    source_file: str = ""
    
    def __repr__(self):
        if self.operand is not None:
            return f"{self.opcode.name} {self.operand}"
        return self.opcode.name

class BytecodeProgram:
    """Container for compiled bytecode"""
    
    def __init__(self):
        self.instructions: List[Instruction] = []
        self.functions: dict = {}
        self.constants: List[Any] = []
    
    def add_instruction(self, instruction: Instruction):
        """Add an instruction to the program"""
        self.instructions.append(instruction)
    
    def add_constant(self, value: Any) -> int:
        """Add a constant and return its index"""
        if value not in self.constants:
            self.constants.append(value)
        return self.constants.index(value)
    
    def serialize(self) -> bytes:
        """Convert bytecode to binary format for storage"""
        data = {
            'instructions': [
                {
                    'opcode': inst.opcode.value,
                    'operand': inst.operand,
                    'line': inst.line_number,
                    'file': inst.source_file
                }
                for inst in self.instructions
            ],
            'functions': self.functions,
            'constants': self.constants
        }
        return json.dumps(data).encode('utf-8')
    
    @classmethod
    def deserialize(cls, data: bytes):
        """Load bytecode from binary format"""
        decoded = json.loads(data.decode('utf-8'))
        program = cls()
        
        for inst_data in decoded['instructions']:
            inst = Instruction(
                opcode=OpCode(inst_data['opcode']),
                operand=inst_data['operand'],
                line_number=inst_data['line'],
                source_file=inst_data['file']
            )
            program.instructions.append(inst)
        
        program.functions = decoded['functions']
        program.constants = decoded['constants']
        
        return program