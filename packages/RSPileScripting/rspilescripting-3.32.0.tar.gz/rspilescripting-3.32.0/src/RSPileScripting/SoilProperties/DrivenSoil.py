from RSPileScripting._client import Client
from RSPileScripting.SoilProperties.DrivenAnalysisMethods.Cohesive import Cohesive
from RSPileScripting.SoilProperties.DrivenAnalysisMethods.Cohesionless import Cohesionless
import RSPileScripting.generated_python_files.soil_services.DrivenSoilService_pb2 as DrivenSoilService_pb2
import RSPileScripting.generated_python_files.soil_services.DrivenSoilService_pb2_grpc as DrivenSoilService_pb2_grpc
from enum import Enum

class DrivenType(Enum):
	COHESIONLESS = DrivenSoilService_pb2.DrivenSoilType.E_COHESIONLESS
	COHESIVE = DrivenSoilService_pb2.DrivenSoilType.E_COHESIVE

class DrivenProperties:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = DrivenSoilService_pb2_grpc.DrivenSoilServiceStub(self._client.channel)
		self.Cohesive = Cohesive(self._model_id, self._soil_id, self._client)
		self.Cohesionless = Cohesionless(self._model_id, self._soil_id, self._client)

	def _getDrivenSoilProperties(self) -> DrivenSoilService_pb2.DrivenSoilProperties:
		request = DrivenSoilService_pb2.GetDrivenSoilRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetDrivenSoilProperties, request)
		return response.driven_soil_props

	def _setDrivenSoilProperties(self, drivenSoilProps: DrivenSoilService_pb2.DrivenSoilProperties):
		request = DrivenSoilService_pb2.SetDrivenSoilRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, driven_soil_props=drivenSoilProps)
		self._client.callFunction(self._stub.SetDrivenSoilProperties, request)

	def getDrivenSoilType(self) -> DrivenType:
		properties = self._getDrivenSoilProperties()
		return DrivenType(properties.driven_soil_type)

	def setDrivenSoilType(self, driven_type: DrivenType):
		properties = self._getDrivenSoilProperties()
		properties.driven_soil_type = driven_type.value
		self._setDrivenSoilProperties(properties)

	def getDrivingStrengthLoss(self) -> float:
		properties = self._getDrivenSoilProperties()
		return properties.driving_strength_loss

	def setDrivingStrengthLoss(self, drivingStrengthLoss: float):
		properties = self._getDrivenSoilProperties()
		properties.driving_strength_loss = drivingStrengthLoss
		self._setDrivenSoilProperties(properties)