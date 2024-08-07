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