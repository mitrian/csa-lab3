class ALU:
    is_negative: bool = False
    is_zero: bool = False

    min_value: int = -(2 ** 31)
    max_value: int = 2 ** 31 - 1

    def set_flags(self, value: int) -> None:
        if value > self.max_value:
            value = value & self.min_value

        if value < self.min_value:
            value = value & self.min_value
        self.is_negative = value < 0
        self.is_zero = value == 0