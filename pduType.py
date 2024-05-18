class PDU:
    def __init__(self, message):
        self.FIFOLength = message.getFIFOLength()
        self.q = message.getQ()
        self.FIFO = [0 for n in range(0, self.FIFOLength)]  # Init buffer with 0-s
        self.KD_FIFO = [0 for n in range(0, self.FIFOLength)]  # Init buffer with 0-s
    def getFIFOLength(self):
        return self.FIFOLength
    def getQ(self):
        return self.q
    def printFIFO(self):
        print("\n", 20 * "=")
        [print(i) for i in self.FIFO]
        print(20 * "=")

class S_PDU(PDU):
    def __init__(self, message):
        super().__init__(message)
        self.WaitDueToSequencelostInit = message.getWaitDueToSequencelostInit()
        self.BSZ_DeltaMax_ReSync = message.getBSZ_DeltaMax_ReSync()
        self.BSZ_DeltaMaxInit = message.getBSZ_DeltaMaxInit()
        self.BSZ_DeltaMax = self.BSZ_DeltaMaxInit
        self.Lost_BSZ_Cnt = 0
        self.WaitDueToSequencelost = 0
        self.FIFO_Cnt_Init = 0
        self.FIFO_Cnt_SafeState = 0
        self.No_FSP_Init = True
        self.No_FSP_SafeState = True
        
        