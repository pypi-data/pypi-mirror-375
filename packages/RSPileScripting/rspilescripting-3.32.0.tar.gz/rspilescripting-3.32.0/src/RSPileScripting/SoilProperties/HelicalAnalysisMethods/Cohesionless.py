from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.HelicalCohesionlessService_pb2 as HelicalCohesionlessService_pb2
import RSPileScripting.generated_python_files.soil_services.HelicalCohesionlessService_pb2_grpc as HelicalCohesionlessService_pb2_grpc

class Cohesionless:
	"""
	Examples:
	:ref:`soil properties helical`
	"""
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = HelicalCohesionlessService_pb2_grpc.HelicalCohesionlessServiceStub(self._client.channel)

	def _getCohesionlessProperties(self) -> HelicalCohesionlessService_pb2.CohesionlessProperties:
		request = HelicalCohesionlessService_pb2.GetCohesionlessRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCohesionlessProperties, request)
		return response.helical_cohesionless_props

	def _setCohesionlessProperties(self, cohesionlessProperties: HelicalCohesionlessService_pb2.CohesionlessProperties):
		request = HelicalCohesionlessService_pb2.SetCohesionlessRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, helical_cohesionless_props=cohesionlessProperties)
		self._client.callFunction(self._stub.SetCohesionlessProperties, request)

	def setInternalFrictionAngle(self, frictionAngle: float):
		properties = self._getCohesionlessProperties()
		properties.phi = frictionAngle
		self._setCohesionlessProperties(properties)

	def getInternalFrictionAngle(self) -> float:
		properties = self._getCohesionlessProperties()
		return properties.phi

	def setFrictionAngleBetweenShaftAndSoil(self, frictionAngleBetweenShaftAndSoil: float):
		properties = self._getCohesionlessProperties()
		properties.delta = frictionAngleBetweenShaftAndSoil
		self._setCohesionlessProperties(properties)

	def getFrictionAngleBetweenShaftAndSoil(self) -> float:
		properties = self._getCohesionlessProperties()
		return properties.delta
	
	def setCoefficientOfLateralEarthPressureForShaft(self, coefficientOfLateralEarthPressure: float):
		properties = self._getCohesionlessProperties()
		properties.k = coefficientOfLateralEarthPressure
		self._setCohesionlessProperties(properties)

	def getCoefficientOfLateralEarthPressureForShaft(self) -> float:
		properties = self._getCohesionlessProperties()
		return properties.k