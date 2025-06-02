import json
import subprocess
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import CalibrateFormulaDB, CalibrateSampleDB
sys.path.append("/home/connex/project/function")
from serviceProjectFunction import ServiceProjectFunction
sys.path.append('/home/connex/project/function/dashboard')
from calibrationFormulaFunction import calibrationFormula


class calibrationSample():
    def insert(formula, valueSample, valueReference):
        try:
            CalibrateSampleDB.insert(formula, valueSample, valueReference)
            calculate = CalibrateSampleDB.selectByFormula(formula)
            CalibrateFormulaDB.updateSampleByFormula(len(calculate), formula)
            calibrationFormula.calculate(formula)
            result = {'state': '1', 'message': 'Calibration Sample Added successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Add Calibration Sample. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def update(sampleId, formula, valueSample, valueReference, formulaLast):
        try:
            CalibrateSampleDB.update(formula, valueSample, valueReference, sampleId)
            calculate = CalibrateSampleDB.selectByFormula(formula)
            CalibrateFormulaDB.updateSampleByFormula(len(calculate), formula)
            calculate2 = CalibrateSampleDB.selectByFormula(formulaLast)
            CalibrateFormulaDB.updateSampleByFormula(len(calculate2), formulaLast)
            calibrationFormula.calculate(formula)
            calibrationFormula.calculate(formulaLast)
            result = {'state': '1', 'message': 'Calibration Sample Update successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Update Calibration Sample. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def delete(sampleId, formula):
        try:
            CalibrateSampleDB.deleteOne(sampleId)
            calculate = CalibrateSampleDB.selectByFormula(formula)
            CalibrateFormulaDB.updateSampleByFormula(len(calculate), formula)
            calibrationFormula.calculate(formula)
            result = {'state': '1', 'message': 'Calibration Sample Delete successfully!'}      
        except Exception as e:
            result = {'state': '0', 'message': 'Failed to Delete Calibration Sample. There is an issue - ' + str(e)}
        return json.dumps(result) 
    
    def check(groupSensorId):
        try:
            service = ServiceProjectFunction.checkActiveService('sensor' + str(groupSensorId))
            if service == 'active':
                output = ['Please stop service sensor' + str(groupSensorId) + " first before check the sensor"]
            else:
                filename = "check_sensor" + groupSensorId + ".py"
                output = subprocess.Popen(["python3", "/home/connex/project/sensor/" + filename, "-t", "0"], stdout=subprocess.PIPE)
                (out, err) = output.communicate()
                output = out.decode('utf-8')
                output = output.split('\n')
            result = {}
            result['message'] = {'state': '1', 'message': 'Check Calibration Sample for Sensor successfully!'}
            result['data'] = {'output': output}      
        except Exception as e:
            result = {}
            result['message'] = {'state': '0', 'message': 'Failed to Check Calibration Sample for Sensor. There is an issue - ' + str(e)}
            result['data'] = {}
        return result
    
    
