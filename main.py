import sys
import inputhandler as ih
import testCaseData, canLog, fillFifo

def Main(from_bat):
    inputs = []
    globalOutput = []
    if len(from_bat) > 2: # Tool run only for 1 frame
        inputs.append({"path":from_bat[1], "message":from_bat[2], "pruefpunkt":from_bat[3], "projekt":from_bat[4]})
        #Inp = ih.InputHandler(from_bat[1], from_bat[2], from_bat[3], from_bat[4])
    else: # Tool runs for whole SAFE/Problem Report
        StrIL = ih.StructuredInputList(from_bat[1])
        [inputs.append(elem) for elem in StrIL.inputList]

    for input in inputs:
        Inp = ih.InputHandler(input["path"], input["message"], input["pruefpunkt"], input["projekt"])
        HTMLDetail = testCaseData.TestCaseData(Inp.getMessage().getName(), Inp.getHTMLFileAccess())
        analysis = fillFifo.FIFOData(canLog.Scenario(Inp, HTMLDetail))
        analysis.addToGlobalComment(globalOutput)
        analysis.writeIntoFile()   # --> The filtered analysis is written into an output file. This is not for testing purpose only

    if len(globalOutput) > 0: # Tool run for all complained frame
        with open("full_analysis.txt", 'w') as outfile:
            [outfile.writelines(elem) for elem in globalOutput]

if __name__ == '__main__':
    Main(sys.argv)
    


# input[0] --> main.py
# input[1] --> CAN-log with absolute path
# input[2] --> frame
# input[3] --> Pruepunkt
# input[4] --> Projekt

