import sys 


class SensorFunction():
    sys.path.append('/home/connex/project/function/sensor')
    from alarmSensorFunction import alarmSensorFunction	
    from serviceSensorFunction import serviceSensor	
    from collectDataSensorFunction import CollectDataSensorFunction
    from calibrationSensorFunction import CalibrateSensorFunction