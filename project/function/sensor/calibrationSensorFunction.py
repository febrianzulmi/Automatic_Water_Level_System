import sys

sys.path.append('/home/connex/project/database')
from query_project_db import CalibrateFormulaDB


class CalibrateSensorFunction:    
    def getFormulaCalibration():
        getData = CalibrateFormulaDB.select()
        formula = {}
        count = 0
        for item in getData :
            formula[count]={
                'id': item['id'],
                'name': item['name'],
                'sample': item['sample'],
                'koef_a': item['koef_a'],
                'koef_b': item['koef_b'],
                'calculate_time': item['calculate_time'].isoformat().replace('T',' ')            
            }
            count+=1
        return formula


    def calculateCalibration(dataSensor, value):
        
        calibrateValue = []
        for i in range(dataSensor['numSensor']):
            global values
            values = ''
            if str(dataSensor['sensorCalibration'][i]) == '0':
                coefA, coefB = 1, 0
                values = value[i]
            elif str(dataSensor['sensorCalibration'][i]) == '1':
                getFormula = CalibrateFormulaDB.selectById(dataSensor['sensorFormula'][i])
                for y in getFormula:
                    coefA = float(y[3])
                    coefB = float(y[4])
                values = (coefA*value[i]) + coefB
                values = round(values,2)
                if values < 0:
                    values = 0.00
            calibrateValue.append(values)
        
        
        return calibrateValue

    # def calculateCalibration(dataSensor, value):
    #     calibrateValue = []
    #     # Debug prints untuk panjang list
    #     print(f"numSensor: {dataSensor['numSensor']}")
    #     print(f"len(sensorCalibration): {len(dataSensor['sensorCalibration'])}")
    #     print(f"len(value): {len(value)}")
        
    #     for i in range(dataSensor['numSensor']):
    #         try:
    #             print(f"Processing sensor index {i}")
    #             print(f"Calibration setting: {dataSensor['sensorCalibration'][i]}")
    #             global values
    #             values = ''
    #             if str(dataSensor['sensorCalibration'][i]) == '0':
    #                 coefA, coefB = 1, 0
    #                 values = value[i]
    #                 print(f"Using default calibration: {values}")
    #             elif str(dataSensor['sensorCalibration'][i]) == '1':
    #                 getFormula = CalibrateFormulaDB.selectById(dataSensor['sensorFormula'][i])
    #                 for y in getFormula:
    #                     coefA = float(y[3])
    #                     coefB = float(y[4])
    #                 values = (coefA * value[i]) + coefB
    #                 values = round(values, 2)
    #                 if values < 0:
    #                     values = 0.00
    #             print(f"Calibrated value: {values}")
    #             calibrateValue.append(values)
    #         except IndexError as e:
    #             print(f"IndexError at sensor index {i}: {str(e)}")
    #             raise
    #     print(f"Final calibrated values: {calibrateValue}")
    #     return calibrateValue

