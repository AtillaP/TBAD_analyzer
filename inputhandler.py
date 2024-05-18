import message as msg
import sys

class InputHandler:
    def __init__(self, path, message, pruefpunkt, projekt):
        self.project = projekt     # this input will be get later from the ticket description, now from user input
        self.message = msg.Message(message, self.project)       # this input will be get later from the ticket description, now from user input
        self.pruefpunkt = pruefpunkt # this input will be get later from the ticket description, now from user input
        self.data = {}
        self.validity = False
        self.__setData(path)
    def __setData(self, path):
        if self.__setHTML(path) == True:
            self.data.update({"absPath":'\\'.join(path.split('\\')[:-1])})
            self.data.update({"CANlog":path.split('\\')[-1]})
            self.validity = True            
    def __setHTML(self, path):
        HTMLName = ""
        HTMLNameList = path.split('\\')[-1].split('_')
        HTMLNameList[1] = str(int(HTMLNameList[1]) + 1)
        HTMLNameList[2] = HTMLNameList[2].split('.')[0] + '.html'
        HTMLName = '_'.join(HTMLNameList)
        self.data.update({"HTMLName":HTMLName})
        return self.__htmlAvailable('\\'.join(path.split('\\')[:-1]) + '\\' + HTMLName)
    def __htmlAvailable(self, fname):
        try: 
            f = open(fname, 'r')
            f.close()
            return True
        except FileNotFoundError:
            return False
    def getMessage(self):
        return self.message
    def getPruefpunkt(self):
        return self.pruefpunkt
    def getValidity(self):
        return self.validity
    def getCANLogName(self):
        return self.data["CANlog"]
    def getHTMLFileAccess(self):
        return self.data['absPath'] + '\\' + self.data['HTMLName']
    def getCANLogFileAccess(self):
        return self.data['absPath'] + '\\' + self.data['CANlog']

class StructuredInputList:
    def __init__(self, sys_arg):
        self.inputList = []
        self.pruefpunkt = ""
        self.projekt = ""
        self.commonPath = ""
        self.__workFolderPath(sys_arg)
        self.__checkRawInput(sys_arg)
    def __workFolderPath(self, file):
        self.commonPath = '\\'.join(file.split('\\')[:-1])
    def __checkRawInput(self, file):
        rawInput = []
        with open(file, 'r') as inputFile:
            rawInput = [line[:-1] if (line[-1] == '\n') else line for line in inputFile]
        if not ("Pr" in rawInput[0]) and not ("fpunkt:" in rawInput[0]):
            with open(self.commonPath + "\\error.txt", "w") as errorlog:
                errorlog.writelines("Inputfile does not contain correct Pruefpunkt")
            sys.exit(0)
        elif not ("37w" in rawInput[-1].lower()) and not ("klassik" in rawInput[-1].lower()):
            with open(self.commonPath + "\\error.txt", "w") as errorlog:
                errorlog.writelines("Inputfile does not contain correct projectname")
            sys.exit(0)
        else:
            self.setPruefPunkt(rawInput)
            self.setProjekt(rawInput)
            self.setFilteredInputList(rawInput)
    def setFilteredInputList(self, rwIp):
        for line in rwIp:
            if "_MSG_" in line and "Soll" in line:
                self.inputList.append({
                    "path" : self.commonPath + "\\" + line[line.index("Logdatei_"):(line.index(".asc")+4)],
                    "message" : str(line[(line.index("_MSG_")+5):(line.index("_ID_"))]),
                    "pruefpunkt" : self.pruefpunkt,
                    "projekt" : self.projekt
                })
            elif "MSG_" in line and "Soll" in line:
                self.inputList.append({
                    "path" : self.commonPath + "\\" + line[line.index("Logdatei_"):(line.index(".asc")+4)],
                    "message" : str(line[(line.index("MSG_")+4):(line.index("_ID_"))]),
                    "pruefpunkt" : self.pruefpunkt,
                    "projekt" : self.projekt
                })
    def setPruefPunkt(self, rwIp):
        self.pruefpunkt = rwIp[1]
    def setProjekt(self, rwIp):
        self.projekt = rwIp[-1]
    def getInputList(self):
        return self.inputList
    def getPruefPunkt(self):
        return self.pruefpunkt
    def getProjekt(self):
        return self.projekt

