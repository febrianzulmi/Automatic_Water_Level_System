import sys
sys.path.append('/home/connex/project/function')

# from actuatorFunction import ActuatorFunction
from collectDataSensorFunction import CollectDataSensorFuntion
from calibrationSensorFunction import CalibrateSensorFunction
from generalFunction import GeneralFunction
from notificationFunction import NotificationFunction
from oidSensorFunction import OidSensorFunction
from serviceProjectFunction import ServiceProjectFunction

# call = OidSensorFunction()
test = OidSensorFunction.generateOidAtBoot(call)
print(test)

# random = GeneralFunction.getRandomID(10)
# print(random)