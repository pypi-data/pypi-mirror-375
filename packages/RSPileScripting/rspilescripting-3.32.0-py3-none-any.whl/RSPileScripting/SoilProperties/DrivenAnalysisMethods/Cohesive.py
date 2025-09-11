from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.DrivenCohesiveService_pb2 as DrivenCohesiveService_pb2
import RSPileScripting.generated_python_files.soil_services.DrivenCohesiveService_pb2_grpc as DrivenCohesiveService_pb2_grpc
from RSPileScripting.SoilProperties.DrivenAnalysisMethods.CohesiveUserDefined import UserDefinedAdhesion
from enum import Enum

class AdhesionType(Enum):
	GENERAL_ADHESION_FOR_COHESIVE_SOILS = DrivenCohesiveService_pb2.DrivenCohesiveType.E_GENERAL_ADHESION_FOR_COHESIVE_SOILS
	OVERLYING_SOFT_CLAY = DrivenCohesiveService_pb2.DrivenCohesiveType.E_OVERLYING_SOFT_CLAY
	OVERLYING_SANDS = DrivenCohesiveService_pb2.DrivenCohesiveType.E_OVERLYING_SANDS
	WITHOUT_DIFF_OVERLYING_STRATA = DrivenCohesiveService_pb2.DrivenCohesiveType.E_WITHOUT_DIFF_OVERLYING_STRATA
	USER_DEFINED_ADHESION = DrivenCohesiveService_pb2.DrivenCohesiveType.E_USER_DEFINED_ADHESION

class Cohesive:
	"""
	Examples:
	:ref:`soil properties driven`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = DrivenCohesiveService_pb2_grpc.DrivenCohesiveServiceStub(self._client.channel)
		self.UserDefinedAdhesion = UserDefinedAdhesion(self._model_id, self._soil_id, self._client)

	def _getCohesiveProperties(self) -> DrivenCohesiveService_pb2.DrivenCohesiveProperties:
		request = DrivenCohesiveService_pb2.GetDrivenCohesiveRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCohesiveProperties, request)
		return response.driven_cohesive_props

	def _setCohesiveProperties(self, drivenCohesiveProps: DrivenCohesiveService_pb2.DrivenCohesiveProperties):
		request = DrivenCohesiveService_pb2.SetDrivenCohesiveRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id,
			driven_cohesive_props=drivenCohesiveProps)
		self._client.callFunction(self._stub.SetCohesiveProperties, request)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getCohesiveProperties()
		return properties.undrained_shear_strength

	def setUndrainedShearStrength(self, strength: float):
		properties = self._getCohesiveProperties()
		properties.undrained_shear_strength = strength
		self._setCohesiveProperties(properties)

	def getAdhesionType(self) -> AdhesionType:
		properties = self._getCohesiveProperties()
		return AdhesionType(properties.driven_cohesive_type)

	def setAdhesionType(self, adhesionType: AdhesionType):
		properties = self._getCohesiveProperties()
		properties.driven_cohesive_type = adhesionType.value
		self._setCohesiveProperties(properties)