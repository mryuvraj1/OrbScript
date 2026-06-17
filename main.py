#!/usr/bin/env python3
"""
OrbScript Compiler CLI
Main entry point for compiling and running OrbScript programs
"""

import sys
import os
import argparse
from pathlib import Path
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from compiler import Compiler, CompilerError
from vm import VirtualMachine, VMError

class OrbScriptCompiler:
    """Main compiler class for OrbScript"""
    
    def __init__(self):
        self.verbose = False
    
    def compile_file(self, filepath: str) -> bytes:
        """Compile a .orb file to bytecode"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if filepath.suffix != '.orb':
            print(f"Warning: {filepath} doesn't have .orb extension")
        
        # Read source code
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        if self.verbose:
            print(f"Compiling {filepath}...")
        
        # Lexical analysis
        lexer = Lexer(source, str(filepath))
        tokens = lexer.tokenize()
        
        if self.verbose:
            print(f"Tokenization complete: {len(tokens)} tokens")
        
        # Parsing
        parser = Parser(tokens, str(filepath))
        ast = parser.parse()
        
        if self.verbose:
            print(f"Parsing complete: AST generated")
        
        # Compilation
        compiler = Compiler()
        bytecode = compiler.compile(ast)
        
        if self.verbose:
            print(f"Compilation complete: {len(bytecode.instructions)} instructions")
        
        return bytecode.serialize()
    
    def compile_string(self, source: str, source_name: str = "<string>") -> bytes:
        """Compile a string of OrbScript code to bytecode"""
        # Lexical analysis
        lexer = Lexer(source, source_name)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens, source_name)
        ast = parser.parse()
        
        # Compilation
        compiler = Compiler()
        bytecode = compiler.compile(ast)
        
        return bytecode.serialize()
    
    def run_file(self, filepath: str):
        """Compile and run a .orb file"""
        bytecode_data = self.compile_file(filepath)
        self.execute_bytecode(bytecode_data)
    
    def run_string(self, source: str, source_name: str = "<string>"):
        """Compile and run a string of OrbScript code"""
        bytecode_data = self.compile_string(source, source_name)
        self.execute_bytecode(bytecode_data)
    
    def execute_bytecode(self, bytecode_data: bytes):
        """Execute compiled bytecode"""
        from bytecode import BytecodeProgram
        
        program = BytecodeProgram.deserialize(bytecode_data)
        vm = VirtualMachine()
        
        try:
            vm.execute(program)
        except VMError as e:
            print(f"Runtime Error: {e}")
            sys.exit(1)
    
    def run_bytecode_file(self, filepath: str):
        """Run a .orbc bytecode file directly"""
        with open(filepath, 'rb') as f:
            bytecode_data = f.read()
        
        self.execute_bytecode(bytecode_data)
    
    def save_bytecode(self, bytecode_data: bytes, output_path: str):
        """Save bytecode to file"""
        with open(output_path, 'wb') as f:
            f.write(bytecode_data)
        
        if self.verbose:
            print(f"Bytecode saved to {output_path}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="OrbScript Compiler and Runtime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  orbscript run example.orb
  orbscript compile example.orb -o example.orbc
  orbscript exec example.orbc
  orbscript run -c 'say "Hello World"'
  orbscript run example1.orb example2.orb
        """
    )
    
    parser.add_argument(
        'command',
        choices=['run', 'compile', 'exec'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Source files to process'
    )
    
    parser.add_argument(
        '-c', '--code',
        help='Run OrbScript code directly from command line'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for compiled bytecode'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='OrbScript 1.0.0'
    )
    
    args = parser.parse_args()
    
    compiler = OrbScriptCompiler()
    compiler.verbose = args.verbose
    
    try:
        if args.command == 'run':
            if args.code:
                compiler.run_string(args.code)
            elif args.files:
                for filepath in args.files:
                    compiler.run_file(filepath)
            else:
                # Interactive mode
                print("OrbScript Interactive Mode")
                print("Type 'exit' to quit, 'help' for help")
                
                while True:
                    try:
                        line = input("orb> ")
                        if line.lower() == 'exit':
                            break
                        elif line.lower() == 'help':
                            print("OrbScript Commands:")
                            print("  set name value  - Set variable")
                            print("  show name       - Show variable")
                            print("  say expression  - Print expression")
                            print("  add a b         - Add numbers")
                            print("  sub a b         - Subtract numbers")
                            print("  mul a b         - Multiply numbers")
                            print("  div a b         - Divide numbers")
                            print("  if condition    - Conditional")
                            print("  repeat count    - Loop")
                            print("  func name       - Define function")
                            print("  call name       - Call function")
                            print("  # comment       - Comment")
                        elif line.strip():
                            compiler.run_string(line, "<interactive>")
                    except KeyboardInterrupt:
                        print("\nGoodbye!")
                        break
                    except EOFError:
                        break
        
        elif args.command == 'compile':
            if not args.files:
                print("Error: No source files specified")
                sys.exit(1)
            
            for filepath in args.files:
                bytecode = compiler.compile_file(filepath)
                
                if args.output:
                    output_path = args.output
                else:
                    output_path = Path(filepath).with_suffix('.orbc')
                
                compiler.save_bytecode(bytecode, str(output_path))
        
        elif args.command == 'exec':
            if not args.files:
                print("Error: No bytecode files specified")
                sys.exit(1)
            
            for filepath in args.files:
                compiler.run_bytecode_file(filepath)
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except LexerError as e:
        print(f"Lexer Error: {e}")
        sys.exit(1)
    except ParserError as e:
        print(f"Parser Error: {e}")
        sys.exit(1)
    except CompilerError as e:
        print(f"Compiler Error: {e}")
        sys.exit(1)
    except VMError as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()