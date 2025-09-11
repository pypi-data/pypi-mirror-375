from RSPileScripting._client import Client
from RSPileScripting.SoilProperties.HelicalAnalysisMethods.Cohesive import Cohesive
from RSPileScripting.SoilProperties.HelicalAnalysisMethods.Cohesionless import Cohesionless
import RSPileScripting.generated_python_files.soil_services.HelicalSoilService_pb2 as HelicalSoilService_pb2
import RSPileScripting.generated_python_files.soil_services.HelicalSoilService_pb2_grpc as HelicalSoilService_pb2_grpc
from enum import Enum

class HelicalType(Enum):
	COHESIONLESS = "E_HELICAL_COHESIONLESS"
	COHESIVE = "E_HELICAL_COHESIVE"

class HelicalProperties:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = HelicalSoilService_pb2_grpc.HelicalSoilServiceStub(self._client.channel)
		self.Cohesive = Cohesive(self._model_id, self._soil_id, self._client)
		self.Cohesionless = Cohesionless(self._model_id, self._soil_id, self._client)

	def _getHelicalSoilProperties(self) -> HelicalSoilService_pb2.HelicalSoilProperties:
		request = HelicalSoilService_pb2.GetHelicalSoilRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetHelicalSoilProperties, request)
		return response.helical_soil_props

	def _setHelicalSoilProperties(self, helicalSoilProps: HelicalSoilService_pb2.HelicalSoilProperties):
		request = HelicalSoilService_pb2.SetHelicalSoilRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, helical_soil_props=helicalSoilProps)
		self._client.callFunction(self._stub.SetHelicalSoilProperties, request)

	def getHelicalSoilType(self) -> HelicalType:
		properties = self._getHelicalSoilProperties()
		return HelicalType(properties.m_soilType)

	def setHelicalSoilType(self, helical_type: HelicalType):
		properties = self._getHelicalSoilProperties()
		properties.m_soilType = helical_type.value
		self._setHelicalSoilProperties(properties)