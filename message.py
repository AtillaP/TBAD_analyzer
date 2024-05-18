import frameStorage

class Message():
    def __init__(self, name, project):
        self.name = name
        self.ID = ""
        self.cycle = 0
        self.fastCycle = 0
        self.FIFOLength = 0
        self.q = 2
        self.WaitDueToSequencelostInit = 0
        self.BSZ_DeltaMax_ReSync = 0
        self.BSZ_DeltaMaxInit = 0
        self.E2E = ""
        self.setAttributes(project)
    def setAttributes(self, project):        
        if project.upper() == "37W":
            CANlist = frameStorage.database_37W___14_07
        else:
            CANlist = frameStorage.database_Klassik___25_02
        for i in CANlist:
            if i["frameName"].lower() == self.name.lower():
                self.name = i["frameName"]
                self.ID = i["ID"]
                self.cycle = i["cycleTime"]
                self.fastCycle = i["fastCycleTime"]
                self.FIFOLength = i["FIFOLength"]
                self.WaitDueToSequencelostInit = i["WaitDueToSequencelostInit"]
                self.BSZ_DeltaMax_ReSync = i["BSZ_DeltaMax_ReSync"]
                self.BSZ_DeltaMaxInit = i["BSZ_DeltaMaxInit"]
                self.E2E = i["E2E"]

    def getName(self):
        return self.name
    def getID(self):
        return self.ID
    def getCycle(self):
        return self.cycle
    def getFastCycle(self):
        return self.fastCycle
    def getFIFOLength(self):
        return self.FIFOLength
    def getQ(self):
        return self.q
    def getWaitDueToSequencelostInit(self):
        return self.WaitDueToSequencelostInit
    def getBSZ_DeltaMax_ReSync(self):
        return self.BSZ_DeltaMax_ReSync
    def getBSZ_DeltaMaxInit(self):
        return self.BSZ_DeltaMaxInit
    def getE2E(self):
        return self.E2E
        