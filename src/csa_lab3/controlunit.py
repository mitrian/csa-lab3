from csa_lab3.datapath import DataPath, MuxLeftSel, MuxRightSel
from csa_lab3.isa import Instruction, Opcode, Register

class ControlUnit:
    data_path: DataPath = None

    def __init__(self, data_path: DataPath):
        self.data_path = data_path

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