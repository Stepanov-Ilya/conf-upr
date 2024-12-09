# Assembler and Interpreter for a Virtual Machine (VM)

import sys
import struct
import xml.etree.ElementTree as ET

# Define opcodes
OPCODES = {
    'LOAD_CONST': 0,
    'READ_MEM': 7,
    'WRITE_MEM': 12,
    'NOT_EQUAL': 13
}

# Assembler class
class Assembler:
    def __init__(self):
        self.instructions = []
        self.log_entries = []

    def assemble(self, source_code):
        for line_num, line in enumerate(source_code.splitlines(), 1):
            # Remove inline comments
            line = line.split('#', 1)[0].strip()
            if not line:
                continue  # Skip empty lines
            parts = line.split()
            opcode = parts[0]
            args = parts[1:]
            if opcode not in OPCODES:
                raise ValueError(f"Unknown opcode '{opcode}' on line {line_num}")
            method = getattr(self, f"_assemble_{opcode.lower()}")
            method(args, line_num)

    def _assemble_load_const(self, args, line_num):
        if len(args) != 1:
            raise ValueError(f"LOAD_CONST requires 1 argument on line {line_num}")
        value = int(args[0])
        opcode = OPCODES['LOAD_CONST']
        # Encode instruction: 4 bytes
        instruction = (opcode & 0xF) | ((value & 0x1FFFF) << 4)
        self.instructions.append(instruction)
        self.log_entries.append({'opcode': 'LOAD_CONST', 'value': value})

    def _assemble_read_mem(self, args, line_num):
        if len(args) != 1:
            raise ValueError(f"READ_MEM requires 1 argument on line {line_num}")
        offset = int(args[0])
        opcode = OPCODES['READ_MEM']
        instruction = (opcode & 0xF) | ((offset & 0x1FFFF) << 4)
        self.instructions.append(instruction)
        self.log_entries.append({'opcode': 'READ_MEM', 'offset': offset})

    def _assemble_write_mem(self, args, line_num):
        if len(args) != 0:
            raise ValueError(f"WRITE_MEM requires no arguments on line {line_num}")
        opcode = OPCODES['WRITE_MEM']
        instruction = opcode & 0xF
        self.instructions.append(instruction)
        self.log_entries.append({'opcode': 'WRITE_MEM'})

    def _assemble_not_equal(self, args, line_num):
        if len(args) != 1:
            raise ValueError(f"NOT_EQUAL requires 1 argument on line {line_num}")
        address = int(args[0])
        opcode = OPCODES['NOT_EQUAL']
        instruction = (opcode & 0xF) | ((address & 0xFFFFFFF) << 4)
        self.instructions.append(instruction)
        self.log_entries.append({'opcode': 'NOT_EQUAL', 'address': address})

    def save_binary(self, filename):
        with open(filename, 'wb') as f:
            for instr in self.instructions:
                f.write(struct.pack('<I', instr))

    def save_log(self, filename):
        root = ET.Element('log')
        for entry in self.log_entries:
            instr_elem = ET.SubElement(root, 'instruction')
            for key, value in entry.items():
                ET.SubElement(instr_elem, key).text = str(value)
        tree = ET.ElementTree(root)
        tree.write(filename)

# Interpreter class
class Interpreter:
    def __init__(self):
        self.stack = []
        self.memory = {}
        self.result_entries = []

    def load_binary(self, filename):
        with open(filename, 'rb') as f:
            self.instructions = []
            while True:
                bytes_read = f.read(4)
                if not bytes_read:
                    break
                instr, = struct.unpack('<I', bytes_read)
                self.instructions.append(instr)

    def execute(self):
        pc = 0
        while pc < len(self.instructions):
            instr = self.instructions[pc]
            opcode = instr & 0xF
            operand = instr >> 4

            if opcode == OPCODES['LOAD_CONST']:
                self.stack.append(operand)
            elif opcode == OPCODES['READ_MEM']:
                addr = self.stack.pop() + operand
                value = self.memory.get(addr, 0)
                self.stack.append(value)
            elif opcode == OPCODES['WRITE_MEM']:
                value = self.stack.pop()
                addr = self.stack.pop()
                self.memory[addr] = value
            elif opcode == OPCODES['NOT_EQUAL']:
                addr = self.stack.pop()
                value1 = self.memory.get(addr, 0)
                value2 = self.memory.get(operand, 0)
                result = int(value1 != value2)
                self.memory[addr] = result
            else:
                raise ValueError(f"Unknown opcode '{opcode}' at instruction {pc}")
            pc += 1

    def save_result(self, filename, mem_range):
        start_addr, end_addr = mem_range
        root = ET.Element('memory')
        for addr in range(start_addr, end_addr + 1):
            if addr in self.memory:
                value = self.memory[addr]
                mem_elem = ET.SubElement(root, 'cell', address=str(addr))
                mem_elem.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(filename)

# Test Program Source Code
test_program = """
# Test Program to perform '!=' operation on a vector of length 6 and the number 95
# Loop for i = 0 to 5
LOAD_CONST 3000      # RES_ADDR + i (for i = 0)
LOAD_CONST 2000      # VEC_ADDR + i (for i = 0)
READ_MEM 0           # Read VEC_ADDR + i
WRITE_MEM            # Write to RES_ADDR + i
LOAD_CONST 3000      # RES_ADDR + i
NOT_EQUAL 1000       # VAL_ADDR (95)

# Repeat the above instructions for i = 1 to 5, adjusting addresses accordingly
LOAD_CONST 3001
LOAD_CONST 2001
READ_MEM 0
WRITE_MEM
LOAD_CONST 3001
NOT_EQUAL 1000

LOAD_CONST 3002
LOAD_CONST 2002
READ_MEM 0
WRITE_MEM
LOAD_CONST 3002
NOT_EQUAL 1000

LOAD_CONST 3003
LOAD_CONST 2003
READ_MEM 0
WRITE_MEM
LOAD_CONST 3003
NOT_EQUAL 1000

LOAD_CONST 3004
LOAD_CONST 2004
READ_MEM 0
WRITE_MEM
LOAD_CONST 3004
NOT_EQUAL 1000

LOAD_CONST 3005
LOAD_CONST 2005
READ_MEM 0
WRITE_MEM
LOAD_CONST 3005
NOT_EQUAL 1000
"""

# Main function
def main():
    if len(sys.argv) < 5:
        print("Usage: python vm.py <source.asm> <binary.bin> <log.xml> <result.xml>")
        return

    source_file = sys.argv[1]
    binary_file = sys.argv[2]
    log_file = sys.argv[3]
    result_file = sys.argv[4]

    # Assemble
    assembler = Assembler()
    with open(source_file, 'r') as f:
        source_code = f.read()
    assembler.assemble(source_code)
    assembler.save_binary(binary_file)
    assembler.save_log(log_file)

    # Interpret
    interpreter = Interpreter()
    interpreter.load_binary(binary_file)
    # Initialize memory (example)
    interpreter.memory[1000] = 95  # VAL_ADDR
    # Initialize vector VEC_ADDR
    vector_addr = 2000
    interpreter.memory[vector_addr] = 90
    interpreter.memory[vector_addr + 1] = 95
    interpreter.memory[vector_addr + 2] = 100
    interpreter.memory[vector_addr + 3] = 95
    interpreter.memory[vector_addr + 4] = 80
    interpreter.memory[vector_addr + 5] = 95
    interpreter.execute()
    interpreter.save_result(result_file, (3000, 3005))

if __name__ == "__main__":
    main()
