from RSPileScripting._client import Client
from RSPileScripting.SoilProperties.BoredAnalysisMethods.Cohesive import Cohesive
from RSPileScripting.SoilProperties.BoredAnalysisMethods.Cohesionless import Cohesionless
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRock import WeakRock
import RSPileScripting.generated_python_files.soil_services.BoredSoilService_pb2 as BoredSoilService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredSoilService_pb2_grpc as BoredSoilService_pb2_grpc
from enum import Enum

class BoredType(Enum):
	COHESIONLESS = BoredSoilService_pb2.BoredSoilType.E_BORED_COHESIONLESS
	COHESIVE = BoredSoilService_pb2.BoredSoilType.E_BORED_COHESIVE
	WEAK_ROCK = BoredSoilService_pb2.BoredSoilType.E_BORED_WEAK_ROCK

class BoredProperties:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredSoilService_pb2_grpc.BoredSoilServiceStub(self._client.channel)
		self.Cohesive = Cohesive(self._model_id, self._soil_id, self._client)
		self.Cohesionless = Cohesionless(self._model_id, self._soil_id, self._client)
		self.WeakRock = WeakRock(self._model_id, self._soil_id, self._client)

	def _getBoredProperties(self) -> BoredSoilService_pb2.BoredSoilProperties:
		request = BoredSoilService_pb2.GetBoredSoilRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetBoredSoilProperties, request)
		return response.bored_soil_props

	def _setBoredProperties(self, boredSoil_props: BoredSoilService_pb2.BoredSoilProperties):
		request = BoredSoilService_pb2.SetBoredSoilRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id,
			bored_soil_props=boredSoil_props)
		self._client.callFunction(self._stub.SetBoredSoilProperties, request)

	def getBoredSoilType(self) -> BoredType:
		properties = self._getBoredProperties()
		return BoredType(properties.bored_soil_type)

	def setBoredSoilType(self, boredType: BoredType):
		properties = self._getBoredProperties()
		properties.bored_soil_type = boredType.value
		self._setBoredProperties(properties)

	def getUseReductionFactors(self) -> bool:
		properties = self._getBoredProperties()
		return properties.enable_reductions_factor

	def setUseReductionFactors(self, enable_reductions_factor: bool):
		properties = self._getBoredProperties()
		properties.enable_reductions_factor = enable_reductions_factor
		self._setBoredProperties(properties)

	def getSkinResistanceLoss(self) -> float:
		properties = self._getBoredProperties()
		return properties.skin_resistance_loss

	def setSkinResistanceLoss(self, skinResistanceLoss: float):
		properties = self._getBoredProperties()
		properties.skin_resistance_loss = skinResistanceLoss
		self._setBoredProperties(properties)

	def getEndBearingLoss(self) -> float:
		properties = self._getBoredProperties()
		return properties.end_bearing_loss

	def setEndBearingLoss(self, endBearingLoss: float):
		properties = self._getBoredProperties()
		properties.end_bearing_loss = endBearingLoss
		self._setBoredProperties(properties)