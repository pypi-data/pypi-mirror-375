from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.HelicalCohesiveService_pb2 as HelicalCohesiveService_pb2
import RSPileScripting.generated_python_files.soil_services.HelicalCohesiveService_pb2_grpc as HelicalCohesiveService_pb2_grpc

class Cohesive:
	"""
	Examples:
	:ref:`soil properties helical`
	"""
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = HelicalCohesiveService_pb2_grpc.HelicalCohesiveServiceStub(self._client.channel)

	def _getCohesiveProperties(self) -> HelicalCohesiveService_pb2.CohesiveProperties:
		request = HelicalCohesiveService_pb2.GetCohesiveRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCohesiveProperties, request)
		return response.helical_cohesive_props

	def _setCohesiveProperties(self, cohesiveProperties: HelicalCohesiveService_pb2.CohesiveProperties):
		request = HelicalCohesiveService_pb2.SetCohesiveRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, helical_cohesive_props=cohesiveProperties)
		self._client.callFunction(self._stub.SetCohesiveProperties, request)

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getCohesiveProperties()
		properties.undrained_shear_strength = undrainedShearStrength
		self._setCohesiveProperties(properties)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getCohesiveProperties()
		return properties.undrained_shear_strength

	def setNcPrime(self, ncPrime: float):
		properties = self._getCohesiveProperties()
		properties.NcPrime = ncPrime
		self._setCohesiveProperties(properties)

	def getNcPrime(self) -> float:
		properties = self._getCohesiveProperties()
		return properties.NcPrime
	
	def setAdhesionFactorForShaft(self, adhesionFactor: float):
		properties = self._getCohesiveProperties()
		properties.adhesion_factor = adhesionFactor
		self._setCohesiveProperties(properties)

	def getAdhesionFactorForShaft(self) -> float:
		properties = self._getCohesiveProperties()
		return properties.adhesion_factor