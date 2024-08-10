import logging
from typing import Callable
from csa_lab3.datapath import DataPath, MuxLeftSel, MuxRightSel
from csa_lab3.isa import AddressingMode, Instruction, MemoryCell, Opcode, Register

class ControlUnit:
    data_path: DataPath = None

    def __init__(self, data_path: DataPath):
        self.data_path = data_path

    def _fetch_instruction(self) -> Instruction:

        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.IP)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        self.data_path.latch_register(Register.AR, self.data_path.alu.alu_add(mux_left_out, mux_right_out))

        cell: MemoryCell = self.data_path.memory[self.data_path.register_output_wire(Register.AR)]
        
        if cell.is_instruction and cell.instruction.opcode == Opcode.HLT:
            return cell.instruction

        instruction: Instruction = cell.instruction
        self.data_path.latch_register(Register.DRR, instruction)
        self.data_path.latch_register(Register.CR, self.data_path.register_output_wire(Register.DRR))
        
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.IP)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        self.data_path.latch_register(Register.IP, self.data_path.alu.alu_inc(mux_left_out, mux_right_out))
        
        if instruction.addressing_mode == AddressingMode.DIRECT:
            self.data_path.latch_register(Register.DRR, instruction.operand)
            if instruction.opcode != Opcode.JMP and instruction.opcode != Opcode.JZ and instruction.opcode != Opcode.JN:
                mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
                mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
                self.data_path.latch_register(Register.AR, self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out))
                if instruction.opcode != Opcode.ST and instruction.opcode != Opcode.LEA:
                    self.data_path.work_with_memory(True, False)  # memory[AR] -> DR
        
        if instruction.addressing_mode == AddressingMode.INDIRECT:
            self.data_path.latch_register(Register.DRR, instruction.operand)
            mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
            mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
            self.data_path.latch_register(Register.AR, self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out))
            self.data_path.work_with_memory(True, False)  # memory[AR] -> DR
            if instruction.opcode != Opcode.JMP and instruction.opcode != Opcode.JZ and instruction.opcode != Opcode.JN:
                mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
                mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
                self.data_path.latch_register(Register.AR, self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out))
                if instruction.opcode != Opcode.ST:
                    self.data_path.work_with_memory(True, False)  # memory[AR] -> DR

        if instruction.addressing_mode == AddressingMode.IMMEDIATE:
            if instruction.opcode != Opcode.JMP and instruction.opcode != Opcode.JZ and instruction.opcode != Opcode.JN:
                self.data_path.latch_register(Register.DRR, instruction.operand)
            else:
                raise IncorrectAddressFormat('Unable to use control flow instruction with immediate addressing mode')
            
        return instruction

    def add(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def sub(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def inc(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def dec(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def cu_and(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def cu_or(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def cu_not(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def cu_neg(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        result: int = self.data_path.execute_arithmetic(instruction.opcode, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def ld(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        self.data_path.latch_register(Register.AC, self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out))

    def st(self, instructon: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)
        self.data_path.latch_register(Register.DRW, self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out))
        self.data_path.work_with_memory(False, True)
        
    def cmp(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        self.data_path.execute_arithmetic(Opcode.CMP, mux_left_out, mux_right_out)        

    def jmp(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        self.data_path.latch_register(Register.IP, self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out))

    def jz(self, instruction: Instruction) -> None:
        if (self.data_path.is_zero()):
            mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
            mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
            self.data_path.latch_register(Register.IP, self.data_path.alu.alu_add(mux_left_out, mux_right_out))
    
    def jn(self, instruction: Instruction) -> None:
        if (self.data_path.is_negative()):
            mux_left_out = self.data_path.mux_left.run(MuxLeftSel.ZERO)
            mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
            self.data_path.latch_register(Register.IP, self.data_path.alu.alu_add(mux_left_out, mux_right_out))

    def mod(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.DRR)
        result: int = self.data_path.execute_arithmetic(Opcode.MOD, mux_left_out, mux_right_out)
        self.data_path.latch_register(Register.AC, result)

    def outt(self, instruction: Instruction) -> None:
        mux_left_out = self.data_path.mux_left.run(MuxLeftSel.AC)
        mux_right_out = self.data_path.mux_right.run(MuxRightSel.ZERO)    
        data: int = self.data_path.execute_arithmetic(Opcode.ADD, mux_left_out, mux_right_out)
        port: int = instruction.operand
        self.data_path.write(data, port)
        
    def inpp(self, instruction: Instruction) -> None:
        port: int = instruction.operand
        data: int = self.data_path.read(port)
        self.data_path.latch_register(Register.AC, data)

    def lea(self, instruction: Instruction) -> None:
        self.data_path.latch_register(Register.AC, instruction.operand)

    def decode_and_execute_instr(self):
        opcode_mapping: dict[Opcode, Callable] = {
            Opcode.ADD: self.add,
            Opcode.SUB: self.sub,
            Opcode.INC: self.inc,
            Opcode.DEC: self.dec,
            Opcode.AND: self.cu_and,
            Opcode.OR: self.cu_or,
            Opcode.NOT: self.cu_not,
            Opcode.NEG: self.cu_neg,
            Opcode.MOD: self.mod,
            Opcode.LD: self.ld,
            Opcode.ST: self.st,
            Opcode.CMP: self.cmp,
            Opcode.JMP: self.jmp,
            Opcode.JZ: self.jz,
            Opcode.JN: self.jn,
            Opcode.INPP: self.inpp,
            Opcode.OUTT: self.outt,
            Opcode.LEA: self.lea
        }
        
        instr: Instruction = self._fetch_instruction()
        opcode: Opcode = instr.opcode

        if opcode in opcode_mapping:
            opcode_mapping[opcode](instr)
            logging.debug("%s, Z_Flag: %s, N_Flag: %s, Op: %s, operand: %s, addressing: %s",self, self.data_path.is_zero(), self.data_path.is_negative(), opcode, instr.operand, instr.addressing_mode)
            return True
        logging.debug("%s, Z_Flag: %s, N_Flag: %s, Op: %s, operand: %s, addressing: %s",self, self.data_path.is_zero(), self.data_path.is_negative(), opcode, instr.operand, instr.addressing_mode)
        return False

class IncorrectAddressFormat(Exception):
    pass