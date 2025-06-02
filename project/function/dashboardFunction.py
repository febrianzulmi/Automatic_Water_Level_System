import sys

class dashboardFunction():
    sys.path.append('/home/connex/project/function/dashboard')
    from calibrationFormulaFunction import calibrationFormula
    from calibrationSampleFunction import calibrationSample
    from dashboardHomeFunction import dashboardHome
    from settingSensorFunction import settingSensor
    from settingServerFunction import settingServer
    from settingFeatureFunction import settingFeature
    from settingActuatorFunction import SettingActuator
    from settingDeviceFunction import settingDevice
    from settingExtensionDeviceFunction import settingExtensionDevice
    from logSensorFunction import logSensor
    from logActuatorFunction import logActuatorSystem
    from logMonitoringFunction import logMonitoring
    from logBufferFunction import logBuffer
    from logNotificationFunction import logNotification
    from logErrorFunction import logErrorSystem
