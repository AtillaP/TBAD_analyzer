import re

class TestCaseData:
    def __init__(self, message, file):
        self.failureBit = 'CCan_WHATEVER'
        self.testPhase = (-1, -1)
        self.__setFailureBit(message)
        self.__setContent(file)
    
    def __setFailureBit(self, message):
        if message == "Rear_View_05":
            message = "REAR_VIEW_05"
        elif message == "Parken_01":
            message = "PARKEN_01"
        self.failureBit = 'CCan_' + message + '_Timeout'
    def __setContent(self, file):        
        cascades = []  # Naming convention by Gregor Feller
        HTML =  open(file, 'r').readlines()
        nominalValueTest, realTest = False, True
        for line in HTML:
            nominalValueTest = self.__allKWordsInLine(line, "Nominal", "value", "test")
            if nominalValueTest:
                realTest = False
                break            
        for line in HTML:
            if nominalValueTest:
                realTest = self.__allKWordsInLine(line, "Complete", "test")
            if realTest:
                nominalValueTest = False
                z = re.match('(Test\s+#)(\d+)(\s+\()(\d+)(ms\))', line)
                if z:
                    i = HTML.index(line) + 1
                    while True:
                        if self.failureBit in HTML[i]:
                            cascades.append((int(z.groups()[1]),int(z.groups()[3])))
                            break
                        if '</tbody>' in HTML[i]:
                            break
                        i += 1
        if nominalValueTest or len(cascades) == 0:
            for line in HTML:
                z = re.match('(Test\s+#)(\d+)(\s+\()(\d+)(ms\))', line)
                if z:
                    i = HTML.index(line) + 1
                    while True:
                        if self.failureBit in HTML[i]:
                            cascades.append((int(z.groups()[1]),int(z.groups()[3])))
                            break
                        if '</tbody>' in HTML[i]:
                            break
                        i += 1
        cascades.sort(key= lambda x : x[1])

        
        if len(cascades) != 0:
            newTuple = list(self.testPhase)
            newTuple[0] = cascades[0][0]
            newTuple[1] = cascades[0][1]
            self.testPhase = tuple(newTuple)
    def __allKWordsInLine(self, line, *keywords):
        for keyword in keywords:
            if keyword not in line:
                return False
        return True
    def getFailureBit(self):
        return self.failureBit
    def getTestPhase(self):
        return self.testPhase
