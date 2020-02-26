"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.pc = 0
        self.reg = [0]*8
        self.SP = 7 # Stack Pointer starts at R7.

    def ram_read(self, mar):
        return self.ram[mar]
    def ram_write(self, mar, value):
        self.ram[mar] = value


    def load(self, filename):
        """Load a program into memory."""

        address = 0
        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.strip().split("#")
                    instruction = comment_split[0].strip()

                    if instruction == "":
                        continue
                    num = int(instruction, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)
            

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def run(self):
        while True:
            command = self.ram[self.pc]
            if command == LDI:
                # Sets specified register to specified value.
                num = self.ram_read(self.pc + 2)
                regI = self.ram_read(self.pc + 1)
                self.reg[regI] = num
                self.pc += 3
            elif command == PRN:
                # Print numeric value stored in the given register.
                regI = self.ram_read(self.pc + 1)
                print(self.reg[regI])
                self.pc += 2
            elif command == MUL:
                # Uses ALU to multiply first register by second register and save that value in the first register.
                firstReg = self.ram_read(self.pc + 1)
                secReg = self.ram_read(self.pc + 2)
                self.alu('MUL', firstReg, secReg)
                self.pc += 3
            elif command == PUSH:
                # Grab the register argument
                regI = self.ram_read(self.pc + 1)
                val = self.reg[regI]
                # Decrement the SP.
                self.reg[self.SP] -= 1
                # Copy the value in the given register to the address pointed to by SP.
                self.ram[self.reg[self.SP]] = val
                self.pc += 2
            elif command == POP:
                # Grab the value from the top of the stack
                regI = self.ram_read(self.pc + 1)
                val = self.ram_read(self.reg[self.SP])
                # Copy the value from the address pointed to by SP to the given register.
                self.reg[regI] = val
                # Increment SP.
                self.reg[self.SP] += 1
                self.pc += 2
            elif command == HLT:
                # Halt the CPU and exit the emulator
                sys.exit(0)
            else:
                print("I did not understand that command: {command}")
                sys.exit(1)

