import pduType

class FIFOData:
    def __init__(self, eventLog):
        self.ownScenario = eventLog # Class Scenario type from canLog modul
        self.state = "Init"
        self.initDone = False # Check whether monitor is over to the Init phase
        self.MQANLastRun = 0.00000 # The time stamp when the MQAN logic ran
        self.__createPDU()  # FIFO Buffer, as long as much
        self.__calculation()
    def __createPDU(self):
        if self.ownScenario.msgData.getE2E() == "NO":
            self.PDU = pduType.PDU(self.ownScenario.msgData)  # Scenario has attribute msgData
        else:
            self.PDU = pduType.S_PDU(self.ownScenario.msgData)
    def __calculation(self):
        entryPointFound = False
        currentTime = 0.00000
        for elem in self.ownScenario.essenceOfCanLog:
            if entryPointFound == True and elem[2] == "MSG":
                currentTime = self.ownScenario.getTimeIdxStamp(self.ownScenario.essenceOfCanLog.index(elem))
                # Calculate time difference
                timeJump = currentTime - self.MQANLastRun
                # Check if it is real message or just MQAN turn
                if self.ownScenario.msgData.getID() in elem[1]:
                    # Run statemachine with arrived message
                    self.__callMQANStateMachine(timeJump, True)
                else:
                    # Run statemachine with missing message
                    self.__callMQANStateMachine(timeJump, False)
                self.MQANLastRun = currentTime
                # FIFO evaluation needed
                self.__evaluateFIFO()

            # First important run of monitoring logic, fill up FIFO with starter values
            # It must be the placed after normal line check, because the first line would be checked twice
            # This line is going to be a message event for 100% sure, due the class method implementation
            if entryPointFound == False and self.ownScenario.essenceOfCanLog.index(elem) == self.ownScenario.getCalculationStartingPoint():
                # Determine the first timetamp when logic run
                entryPointFound = True
                self.MQANLastRun = self.ownScenario.getTimeIdxStamp(self.ownScenario.getCalculationStartingPoint())
                self.__enterStartValuesToFIFO()
            # If a MSG type event is read from Scenario, then moitoring logic ran
            #self.PDU.printFIFO()

    def __enterStartValuesToFIFO(self):
        # In case of 1800 msec tDiagSTart, the Init values can remain, everything is 0
        # In case of SafeState inspection, the FIFO is full of valid
        if self.ownScenario.getDwType() == "SafeState":
            self.PDU.FIFO = [1 for i in range(len(self.PDU.FIFO))]
            self.initDone = True
    def __evaluateFIFO(self):
        if sum(self.PDU.FIFO) >= self.PDU.getQ():
            self.state = "Normal"
        else:
            self.__setInvalidState()
    def __setInvalidState(self):
        # if current state is Init, then it can remain, if SafeStet, then it can also remain
        if self.state == "Normal":
            self.state = "SafeState"
    
    def __callMQANStateMachine(self, timeDiff, isMessage):
        pass
        
    def getInitDone(self):
        return self.initDone
    def addToGlobalComment(self, argList):
        firstLine = str(self.ownScenario.getCANLogName()) + " "
        firstLine += ("tested message --> " + str(self.ownScenario.msgData.getName()) + ":\n")
        argList.append(firstLine)
        argList.append(70*"-" + "\n")
        argList.append("n - "+str(self.ownScenario.msgData.getFIFOLength())+"\n")
        argList.append("reprate - "+str(self.ownScenario.msgData.getCycle())+"\n")
        argList.append("FTT - "+str((self.ownScenario.msgData.getFIFOLength() - 1) * (self.ownScenario.msgData.getCycle()))+"\n")
        argList.append(70*"-" + "\n")        
        for elem in self.ownScenario.essenceOfCanLog:
            argList.append(str(format(elem[0], '.5f')) + "  " + elem[1] + "\n")
        argList.append(70*"-" + "\n")
        argList.append("DiagWait started at: " + str(self.ownScenario.getSuppressionPhase()["start"][0]) + "\n")
        argList.append("DiagWait ended at: " + str(self.ownScenario.getSuppressionPhase()["end"][0]) + "\n")
        argList.append("Length of DiagWait: " + str(self.ownScenario.getSuppressionPhase()["length"]) + "\n")
        argList.append("\n")
        argList.append("\n")
        
    def writeIntoFile(self):
        fname = self.ownScenario.msgData.getName() + "___" + self.ownScenario.pruefpunkt.replace('.', '_')
        fname += ("___" + self.ownScenario.getCANLogName().replace('.', '_') + ".txt")
        with open(fname, 'w') as outfile:
            firstLine = str(self.ownScenario.getCANLogName()) + " "
            firstLine += ("tested message --> " + str(self.ownScenario.msgData.getName()) + ":\n")
            outfile.writelines(firstLine)
            outfile.writelines(70*"-" + "\n")
            outfile.writelines("n - "+str(self.ownScenario.msgData.getFIFOLength())+"\n")
            outfile.writelines("reprate - "+str(self.ownScenario.msgData.getCycle())+"\n")
            outfile.writelines("FTT - "+str((self.ownScenario.msgData.getFIFOLength() - 1) * (self.ownScenario.msgData.getCycle()))+"\n")
            outfile.writelines(70*"-" + "\n")        
            for elem in self.ownScenario.essenceOfCanLog:
                outfile.writelines(str(format(elem[0], '.5f')) + "  " + elem[1] + "\n")
    def printBufferData(self):
        print(self.buffer.getFIFOLength())
    def printFileContentToConsole(self):
        for elem in self.ownScenario.essenceOfCanLog:
            print()
            print(str(format(elem[0], '.5f')) + "  " + elem[1])
    def testDataTransfer(self):
        self.PDU.printFIFO()