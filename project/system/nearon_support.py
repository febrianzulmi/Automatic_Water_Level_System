import schedule
import sys 
import time

sys.path.append("/home/connex/project/function")
from logFunction import logFunction
from supportFunction import supportFunctionSystem
from serviceProjectFunction import ServiceProjectFunction


schedule.every().day.at("00:00").do(logFunction.backupFunction.runBackup)

def main():
    schedule.run_pending()
    supportFunctionSystem.ledErrorCheck()
    supportFunctionSystem.resetSystem()
    time.sleep(5)

while True:
    if __name__ == "__main__": 
        try:
            main()
        except Exception as e:
            ServiceProjectFunction.handlingServiceError("Support System", e)
