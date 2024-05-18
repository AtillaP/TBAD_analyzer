import re
import sys
from pruefPunktData import pruefPunktData

class Scenario():
    def __init__(self, refinedInput, htmlInput):
        self.essenceOfCanLog = []
        self.htmlSession = htmlInput.getTestPhase()
        self.pruefpunkt = refinedInput.getPruefpunkt()
        self.pruefpunktIdx = -1
        self.msgData = refinedInput.getMessage()   # Dict with the important attributes of the frame
        self.tempStorage = []
        self.failureEndurance = 0.00000
        self.dwType = ""
        self.calculationStartIdx = 0
        self.suppressionPhase = {
            "start" : (0.00000, ""),
            "end" : (0.00000, ""),
            "length" : 0.00000
        }
        self.CANLogName = refinedInput.getCANLogName()
        self.__setPruefpunktIdx()
        self.__cutTestCase(refinedInput.getCANLogFileAccess(), htmlInput)    
        self.__findEndPoints(refinedInput.getCANLogFileAccess())
        self.__detMonitoringLogic()
        self.__addTempBufferElements()
        self.__detCalculationStartingPoint()
    def __setPruefpunktIdx(self):
        for n in range(0, len(pruefPunktData)):
            if self.pruefpunkt == pruefPunktData[n]["pruefpunkt"]:
                self.pruefpunktIdx = n
        self.__setDiagWaitType(self.pruefpunktIdx)        
    def __cutTestCase(self, inputf, htmlInput):
        stLStr = 'TEST #' + str(htmlInput.getTestPhase()[0]) + ' (' + str(htmlInput.getTestPhase()[1])
        enLStr = 'TEST #' + str(htmlInput.getTestPhase()[0] + 1)
        fcontent = open(inputf, 'r').readlines()
        appending = False
        for i in range(0, len(fcontent)):
            if appending:
                if enLStr in fcontent[i]:
                    break
                if "//" in fcontent[i]:
                    self.essenceOfCanLog.append((float(re.search("(\d+\.\d+)",fcontent[i]).group()), re.search("(\*+.+\*+)",fcontent[i]).group(), "DESC"))
                elif (self.msgData.getID() + " TX") in fcontent[i]:
                    self.essenceOfCanLog.append((float(re.search("(\d+\.\d+)",fcontent[i]).group()), re.search("(\d+\s+\w+\s+TX.*$)",fcontent[i]).group(), "MSG"))
                elif self.pruefpunkt == "4.12.7" and "errorframe" in fcontent[i].lower():
                    self.essenceOfCanLog.append((float(re.search("(\d+\.\d+)",fcontent[i]).group()), re.search("errorframe|ErrorFrame",fcontent[i]).group(), "SPEC"))
            elif stLStr in fcontent[i]:
                self.essenceOfCanLog.append((float(re.search("(\d+\.\d+)",fcontent[i]).group()), re.search("(\*+.+\*+)",fcontent[i]).group(), "DESC"))
                appending = True
        # Sorting according timestamps:
        self.essenceOfCanLog.sort(key= lambda x : x[0])
    def __findEndPoints(self, inputf):
        lastMsgIndex = -1  # index of last sent valid message in the simulation session
        firstMsgIndex = -1 # index of fist sent valid message in the simulation session        
        refTime = 0.0000
        # search in backward direction
        i = len(self.essenceOfCanLog) - 1
        while True:
            # Find the RESTART of correct message simulation
            if pruefPunktData[self.pruefpunktIdx]["restart"] in self.essenceOfCanLog[i][1]:
                refTime = self.essenceOfCanLog[i][0]
                # start search backwards, in order to find last and firs correctly sent message events
                lineNum = i
                while True:
                    lineNum -= 1
                    try:
                        if self.essenceOfCanLog[lineNum][2] == "MSG": # Message event found
                            refTime = refTime - self.essenceOfCanLog[lineNum][0] # Earliest MSG event gives the new time reference
                            if refTime > (2 * (self.getMsgCycleInSecond())): # Timestamp of last valid message found
                                lastMsgIndex = lineNum
                                break # Start to look for the first correctly sent message
                            else:
                                firstMsgIndex = lineNum
                    except IndexError:
                        #print(self.essenceOfCanLog[lineNum+1][0]," ",self.essenceOfCanLog[lineNum+1][1])
                        print(self.msgData.getName())
                        print(self.htmlSession)
                        print(self.CANLogName)
                        sys.exit(0)
                # if only lastvalid found, the firstvalid must be still find
                lineNum = i
                if firstMsgIndex == -1:
                    while True:
                        lineNum += 1
                        if self.essenceOfCanLog[lineNum][2] == "MSG": # Message event found
                            firstMsgIndex = lineNum
                            break
            if firstMsgIndex != -1 and lastMsgIndex != -1 :
                break
            i -= 1
        self.__setFailureEndurance(lastMsgIndex, firstMsgIndex)
        self.__removeFromEnd(firstMsgIndex)
        self.__removeFromBeginning(lastMsgIndex)
        self.__removeSpecialLines()
        if self.pruefpunkt == "4.12.7":
            self.__addEndOfDisturbance(inputf)
        self.__addEOFTDiag(self.pruefpunktIdx)
    def __removeFromEnd(self, f_MSGI):
        i = f_MSGI + 1
        buffering = True
        while True:
            if self.essenceOfCanLog[i][2] == "MSG":
                if buffering:
                    buffering = self.__updateTempStorage(self.essenceOfCanLog[i])
                del self.essenceOfCanLog[i]
            else:
                i += 1
            if i == len(self.essenceOfCanLog):
                break
    def __removeFromBeginning(self, l_MSGI):
        i = l_MSGI - 1
        while True:
            if self.essenceOfCanLog[i][2] == "MSG":
                del self.essenceOfCanLog[i]
                i -= 1
            else:
                i -= 1                
            if i == 0:
                break
    def __removeSpecialLines(self):
        i = len(self.essenceOfCanLog) - 1
        latest = 0.00000
        latestFound = False
        while True:
            if self.essenceOfCanLog[i][2] == "SPEC" and latest < self.essenceOfCanLog[i][0]:
                latest = self.essenceOfCanLog[i][0]
                i -= 1
            elif self.essenceOfCanLog[i][0] < latest and self.essenceOfCanLog[i][2] == "SPEC":
                del self.essenceOfCanLog[i]
            else:
                i -= 1                
            if i == 0:
                break
    def __addEndOfDisturbance(self, inputf):
        refTime = 0.00000
        fcontent = open(inputf, 'r').readlines()
        for line in self.essenceOfCanLog:
            if line[2] == "SPEC":
                refTime = line[0]
                break
        for i in range(0, len(fcontent)):
            if "CAN" in fcontent[i] and " RX " in fcontent[i] and float(re.search("(\d+\.\d+)",fcontent[i]).group()) > refTime:
                self.essenceOfCanLog.append((float(re.search("(\d+\.\d+)",fcontent[i]).group()), re.search("(\d+\s+\w+\s+RX.*$)",fcontent[i]).group(), "SPEC"))
                break
        # Sorting according timestamps:
        self.essenceOfCanLog.sort(key= lambda x : x[0])
    def __addEOFTDiag(self, globalIndex):
        timeStamp = 0
        for i in range(len(self.essenceOfCanLog)-1, -1, -1):
            if pruefPunktData[globalIndex]["tDiagStart"] in self.essenceOfCanLog[i][1]:
                self.suppressionPhase["start"] = (float(format(self.essenceOfCanLog[i][0], '.5f')), str(self.essenceOfCanLog[i][1]))
                if pruefPunktData[globalIndex]["pruefpunkt"] == "4.12.7":
                    timeStamp = self.__specialTDiagEnd(i, globalIndex)
                else:
                    timeStamp = float(self.essenceOfCanLog[i][0]) + float(pruefPunktData[globalIndex]["tDiagTime"])
                self.suppressionPhase["end"] = (float(format(timeStamp, '.5f')), "*** tDiagStart expired ***")
                break
        self.essenceOfCanLog.append((float(format(timeStamp, '.5f')), "*** tDiagStart expired ***","DESC"))
        self.suppressionPhase["length"] = float(format(self.suppressionPhase["end"][0] - self.suppressionPhase["start"][0], '.5f'))
        self.essenceOfCanLog.sort(key= lambda x : x[0])
    def __specialTDiagEnd(self, index, globalIndex):
        realDisturbance = False
        for i in range(index, len(self.essenceOfCanLog)):
            if "errorframe" in self.essenceOfCanLog[i][1].lower():
                realDisturbance = True
            if realDisturbance and (" RX " in self.essenceOfCanLog[i][1]):
                return float(self.essenceOfCanLog[i][0] + float(pruefPunktData[globalIndex]["tDiagTime"]))
        return float(self.essenceOfCanLog[index][0]) + float(pruefPunktData[globalIndex]["tDiagTime"])
    def __detMonitoringLogic(self):
        addMQANDuringDiagWait, refTime, until, lastMessageIdx, diagWaitExpirationTime, dwStartIdx, tDiagExpFound = False, 0.00000, 0, 0, 0.00000, 0, False
        for elem in self.essenceOfCanLog:
            if elem[2] == "MSG" and refTime == 0.00000:   # Find the first MESSAGE event before timeout in the collected list
                refTime = elem[0]    # Timestamp of first MESSAGE event is written into ${refTime}
                lastMessageIdx = self.essenceOfCanLog.index(elem) # index of first MESSAGE event will be used later
            elif elem[2] == "MSG" and tDiagExpFound:   # Find the first MESSAGE event after tDiagStart expired
                tDiagExpFound = False
                until = elem[0]  # Write into the ${until} variable the timestamp of the first MESSAGE event after tDiagStart expiration
                break
            if pruefPunktData[self.pruefpunktIdx]["tDiagStart"] in elem[1]:
                dwStartIdx = self.essenceOfCanLog.index(elem)
            if "tDiagStart expired" in elem[1]:  # Find expiration of tDiagStart
                tDiagExpFound = True
                diagWaitExpirationTime = float(format(elem[0], '.5f'))
                # Find the difference between tDiagStart expiration, and last MESSAGE event before timeout
                # and divide this tie range with the cycletime of the inspected message
                # and take its MODULO, and write it into the ${refTime}
                refTime = float(format(((elem[0] - refTime) % (self.getMsgCycleInSecond())), '.5f'))
                refTime = float(format(((self.getMsgCycleInSecond()) - refTime), '.5f'))
                refTime = elem[0] + refTime  # We get the timestamp of the first event, when MQAN logic runs after DiagWait
        # Add timestmaps of possible MQAN logic before DiagWait runs is not needed for SystemInit related Prüfpunkts
        if self.dwType == 'SafeState':
            addMQANDuringDiagWait = True
        while addMQANDuringDiagWait:
            timeStamp = self.essenceOfCanLog[lastMessageIdx][0] + self.getMsgCycleInSecond()
            if timeStamp < diagWaitExpirationTime:
                if timeStamp < self.essenceOfCanLog[dwStartIdx][0]:
                    self.essenceOfCanLog.append((float(format(timeStamp, '.5f')), "MQAN before DiagWait","MSG"))
                    self.essenceOfCanLog.sort(key= lambda x : x[0])
                else:
                    self.essenceOfCanLog.append((float(format(timeStamp, '.5f')), "MQAN during DiagWait","MSG"))
                    self.essenceOfCanLog.sort(key= lambda x : x[0])
                lastMessageIdx += 1
            else:
                break
        while True:
            # When timestamp of the monitoring logic event is higher then the timestamp of the 
            # first MESSAGE after tDiagStart, then break the loop
            if refTime >= until:
                break
            self.essenceOfCanLog.append((float(format(refTime, '.5f')), "MQAN after DiagWait","MSG"))
            refTime += self.getMsgCycleInSecond()   # Increase ${refTime} with the cycletime to find timestamps, when monitoring logic ran
        self.essenceOfCanLog.sort(key= lambda x : x[0])
    def __updateTempStorage(self, ttuple):
        if len(self.tempStorage) < self.msgData.getFIFOLength():
            self.tempStorage.append(ttuple)
            return True
        return False
    def __addTempBufferElements(self):
        for elem in self.tempStorage:
            self.essenceOfCanLog.append(elem)
        self.essenceOfCanLog.sort(key= lambda x : x[0])
    def __setFailureEndurance(self, lastV, firstV):
        self.failureEndurance = self.essenceOfCanLog[firstV][0] - self.essenceOfCanLog[lastV][0]
    def __setDiagWaitType(self, idx):
        if pruefPunktData[idx]["tDiagTime"] == 1.8:
            self.dwType = "Init"
        elif pruefPunktData[idx]["tDiagTime"] == 0.5:
            self.dwType = "SafeState"
    def __detCalculationStartingPoint(self):
        for elem in self.essenceOfCanLog:
            if (self.msgData.getID() + " TX") in elem[1]:
                self.calculationStartIdx = self.essenceOfCanLog.index(elem)
                break
    def getFailureEndurance(self):
        return self.failureEndurance
    def getMsgCycleInSecond(self):
        return (float)((self.msgData.getCycle()) / 1000)
    def getCalculationStartingPoint(self):
        return self.calculationStartIdx
    def getDwType(self):
        return self.dwType
    def getTimeIdxStamp(self, idx):
        return float(format(self.essenceOfCanLog[idx][0], '.5f'))
    def getCANLogName(self):
        return self.CANLogName
    def getSuppressionPhase(self):
        return self.suppressionPhase
    def printLine(self, idx):
        print(self.essenceOfCanLog[idx][0], "  ", self.essenceOfCanLog[idx][1])
    def printEssence(self):
        for elem in self.essenceOfCanLog:
            print(elem[0], "  ", elem[1], "  ", elem[2])
