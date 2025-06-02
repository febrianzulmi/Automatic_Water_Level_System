import json
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import CalibrateFormulaDB, CalibrateSampleDB


class calibrationFormula():
    def insert(name):
        try:
            CalibrateFormulaDB.insert(name, 0)
            result = {'state': '1', 'message': 'Calibration Formula Added successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Add Calibration Formula. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def update(formulaId, name):
        try:
            CalibrateFormulaDB.updateNameByFormula(name, formulaId)
            result = {'state': '1', 'message': 'Calibration Formula Update successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Update Calibration Formula. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def delete(formulaId):
        try:
            CalibrateFormulaDB.deleteOne(formulaId)
            result = {'state': '1', 'message': 'Calibration Formula Delete successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Delete Calibration Formula. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def calculate(formulaId):
        def sumValue(list_value):
            value = 0
            for x in range(len(list_value)):
                value += list_value[x]
            return value 
        try:
            datetimes = times.getDatetime()
            sampleData = CalibrateSampleDB.selectByFormula(formulaId)
            if len(sampleData) > 1:
                value_sample, value_reference, value_xy, value_x2 = [], [], [], []
                for i in range(len(sampleData)):
                    sample = float(sampleData[i]['value_sample'])
                    reference = float(sampleData[i]['value_reference'])
                    value_sample.append(sample)
                    value_reference.append(reference)
                    value_xy.append(sample*reference)
                    value_x2.append(sample*sample)
                sumValueSample = sumValue(value_sample)
                sumValueReference = sumValue(value_reference)
                sumValueXY = sumValue(value_xy)
                sumValueX2 = sumValue(value_x2)
                valueSXX = sumValueX2 - ((sumValueSample*sumValueSample)/len(sampleData))
                valueSXY = sumValueXY - (sumValueSample*sumValueReference/len(sampleData))
                coefA = valueSXY/valueSXX
                coefB = 1/len(sampleData)*(sumValueReference-(coefA*sumValueSample))
                coefA = round(coefA, 4)
                coefB = round(coefB, 4)
                CalibrateFormulaDB.updateCoefByFormula(coefA, coefB, datetimes, formulaId)
            else:   
                CalibrateFormulaDB.updateCoefByFormula(1, 0, datetimes, formulaId)
            result = {'state': '1', 'message': 'Calibration Formula Calculate successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Calculate Calibration Formula. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def check(formulaId, sampleValue):
        try:
            datetimes = times.getDatetime()
            formulaData = CalibrateFormulaDB.selectById(formulaId)
            if len(formulaData) == 1:
                formulaName = formulaData[0]['name']
                coefA = float(formulaData[0]['koef_a'])
                coefB = float(formulaData[0]['koef_b'])
                formula = str(coefA) + "x + (" + str(coefB) + ")"   
                calibrateValue = (coefA*float(sampleValue)) + coefB
                calibrateValue = round(calibrateValue,2)
            result = {}
            result['message'] = {'state': '1', 'message': 'Calibration Formula Calculate successfully!'}
            result['data'] = {'name': formulaName, 'timestamp': datetimes, 'formula': formula, 'coefA': coefA, 'coefB': coefB, 'calibrateValue': calibrateValue}      
        except Exception as e:
            result = {}
            result['message'] = {'state': '0', 'message': 'Failed to Calculate Calibration Formula. There is an issue - ' + str(e)}
            result['data'] = {}
        return result