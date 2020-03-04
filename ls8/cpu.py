"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101 
JNE = 0b01010110
PRA = 0b01001000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.pc = 0
        self.reg = [0]*8
        self.SP = 7 # Stack Pointer starts at R7.
        self.FL = [0]*8
        self.L = 5
        self.G = 6
        self.E = 7
        self.bt = {}
        self.bt[LDI] = self.handle_LDI
        self.bt[PRN] = self.handle_PRN
        self.bt[HLT] = self.handle_HLT
        self.bt[MUL] = self.handle_MUL
        self.bt[ADD] = self.handle_ADD
        self.bt[PUSH] = self.handle_PUSH
        self.bt[POP] = self.handle_POP
        self.bt[CALL] = self.handle_CALL
        self.bt[RET] = self.handle_RET
        self.bt[CMP] = self.handle_CMP
        self.bt[JMP] = self.handle_JMP
        self.bt[JEQ] = self.handle_JEQ
        self.bt[JNE] = self.handle_JNE
        self.bt[PRA] = self.handle_PRA

    def handle_LDI(self):
        # Sets specified register to specified value.
        num = self.ram_read(self.pc + 2)
        regI = self.ram_read(self.pc + 1)
        self.reg[regI] = num
        self.pc += 3
    def handle_PRN(self):
        # Print numeric value stored in the given register.
        regI = self.ram_read(self.pc + 1)
        print(self.reg[regI])
        self.pc += 2
    def handle_PRA(self):
        regI = self.ram_read(self.pc + 1)
        letter = chr(self.reg[regI])
        print(letter)
        self.pc += 2
    def handle_HLT(self):
        # Halt the CPU and exit the emulator
        sys.exit(0)
    def handle_MUL(self):
        # Uses ALU to multiply first register by second register and save that value in the first register.
        firstReg = self.ram_read(self.pc + 1)
        secReg = self.ram_read(self.pc + 2)
        self.alu('MUL', firstReg, secReg)
        self.pc += 3
    def handle_ADD(self):
        # Uses ALU to add first register by second register and save that value in the first register.
        firstReg = self.ram_read(self.pc + 1)
        secReg = self.ram_read(self.pc + 2)
        self.alu('ADD', firstReg, secReg)
        self.pc += 3
    def handle_PUSH(self):
        # Grab the register argument
        regI = self.ram_read(self.pc + 1)
        val = self.reg[regI]
        # Decrement the SP.
        self.reg[self.SP] -= 1
        # Copy the value in the given register to the address pointed to by SP.
        self.ram[self.reg[self.SP]] = val
        self.pc += 2
    def handle_POP(self):
        # Grab the value from the top of the stack
        regI = self.ram_read(self.pc + 1)
        val = self.ram_read(self.reg[self.SP])
        # Copy the value from the address pointed to by SP to the given register.
        self.reg[regI] = val
        # Increment SP.
        self.reg[self.SP] += 1
        self.pc += 2
    def handle_CALL(self):
        # The address of the instruction directly after CALL
        # is pushed onto the stack.
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.pc + 2
        # This allows us to return to where we left off
        # when the subroutine finishes executing.
        # The PC is set to the address stored in the given register.
        regI = self.ram_read(self.pc + 1)
        self.pc = self.reg[regI]
        # We jump to that location in RAM and execute the first
        # instruction in the subroutine. The PC can move forward or
        # backwards from its current location.
    def handle_RET(self):
        # Return from subroutine.
        # Pop the value from the top of the stack and store it in the PC.
        self.pc = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1
    def handle_CMP(self):
        firstReg = self.ram_read(self.pc + 1)
        secReg = self.ram_read(self.pc + 2)
        self.alu('CMP', firstReg, secReg)
        self.pc += 3
    def handle_JMP(self):
        regI = self.ram_read(self.pc + 1)
        jumpAddress = self.reg[regI]
        self.pc = jumpAddress
    def handle_JEQ(self):
        regI = self.ram_read(self.pc + 1)
        jumpAddress = self.reg[regI]
        if self.FL[self.E] == 1:
            self.pc = jumpAddress
        else:
            self.pc += 2
    def handle_JNE(self):
        regI = self.ram_read(self.pc + 1)
        jumpAddress = self.reg[regI]
        if self.FL[self.E] == 0:
            self.pc = jumpAddress
        else:
            self.pc += 2


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
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:   
                self.FL[self.E] = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL[self.L] = 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL[self.G] = 1
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
            self.bt[command]()