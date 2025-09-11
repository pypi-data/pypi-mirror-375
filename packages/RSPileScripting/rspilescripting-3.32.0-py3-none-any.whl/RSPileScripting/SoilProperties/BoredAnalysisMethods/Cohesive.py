from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesiveService_pb2 as BoredCohesiveService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesiveService_pb2_grpc as BoredCohesiveService_pb2_grpc
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesiveEffectiveStress import EffectiveStress
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesiveTotalStress import TotalStress
from enum import Enum

class CohesiveMethod(Enum):
	TOTAL_STRESS = BoredCohesiveService_pb2.CohesiveType.E_SR_ALPHA
	EFFECTIVE_STRESS = BoredCohesiveService_pb2.CohesiveType.E_SR_BETA

class Cohesive:
	"""
	Examples:
	:ref:`soil properties bored`
	"""
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesiveService_pb2_grpc.BoredCohesiveServiceStub(self._client.channel)
		self.TotalStress = TotalStress(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.EffectiveStress = EffectiveStress(model_id=self._model_id, soil_id=self._soil_id, client=self._client)

	def _getCohesiveProperties(self) -> BoredCohesiveService_pb2.CohesiveProperties:
		request = BoredCohesiveService_pb2.GetCohesiveRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCohesiveProperties, request)
		return response.cohesive_props

	def _setCohesiveProperties(self, cohesiveProps: BoredCohesiveService_pb2.CohesiveProperties):
		request = BoredCohesiveService_pb2.SetCohesiveRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, 
			cohesive_props=cohesiveProps)
		self._client.callFunction(self._stub.SetCohesiveProperties, request)

	def getCohesiveMethod(self) -> CohesiveMethod:
		properties = self._getCohesiveProperties()
		return CohesiveMethod(properties.cohesive_type)

	def setCohesiveMethod(self, cohesiveMethod: CohesiveMethod):
		properties = self._getCohesiveProperties()
		properties.cohesive_type = cohesiveMethod.value
		self._setCohesiveProperties(properties)