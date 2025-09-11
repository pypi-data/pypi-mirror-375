from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralStrongRockService_pb2 as LateralStrongRockService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralStrongRockService_pb2_grpc as LateralStrongRockService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralStrongRockDatumProperties(Enum):
	UNIAXIAL_COMPRESSIVE_STRENGTH = "LAT_STRONG_ROCK_UNIAXIAL_COMP_STR"

class StrongRock:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralStrongRockService_pb2_grpc.LateralStrongRockServiceStub(self._client.channel)
		self.Datum: Datum[LateralStrongRockDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getStrongRockProperties(self) -> LateralStrongRockService_pb2.StrongRockProperties:
		request = LateralStrongRockService_pb2.GetStrongRockRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetStrongRockProperties, request)
		return response.strong_rock_props

	def _setStrongRockProperties(self, strongRockProps: LateralStrongRockService_pb2.StrongRockProperties):
		request = LateralStrongRockService_pb2.SetStrongRockRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, strong_rock_props=strongRockProps)
		self._client.callFunction(self._stub.SetStrongRockProperties, request)

	def getUniaxialCompressiveStrength(self) -> float:
		properties = self._getStrongRockProperties()
		return properties.uniaxial_compressive_strength_SR

	def setUniaxialCompressiveStrength(self, uniaxialCompressiveStrength: float):
		properties = self._getStrongRockProperties()
		properties.uniaxial_compressive_strength_SR = uniaxialCompressiveStrength
		self._setStrongRockProperties(properties)