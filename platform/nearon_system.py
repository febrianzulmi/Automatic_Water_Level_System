import sys
import time
sys.path.append('/home/connex/platform/function')
from boardFunction import boardFunction
from systemFunction import systemFunction


device = boardFunction.initDevice()
error, fan = 0, 1
globalVariable = {"device": device, "error": error, "fan": fan}

def main():
    global globalVariable
    
    systemFunction.readInformationSBC(globalVariable)
    systemFunction.checkSyncTime()
    systemFunction.checkServiceProject()

    print("")
    time.sleep(10)
    
    
while True:
    if __name__ == '__main__':
        try:
            main()
        except Exception as e:
            pass