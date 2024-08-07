from csa_lab3.datapath import DataPath

class ControlUnit:
    data_path: DataPath = None

    def __init__(self, data_path: DataPath):
        self.data_path = data_path