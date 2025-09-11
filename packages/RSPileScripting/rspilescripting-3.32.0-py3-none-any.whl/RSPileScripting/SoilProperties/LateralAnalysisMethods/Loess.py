from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralLoessService_pb2 as LateralLoessService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralLoessService_pb2_grpc as LateralLoessService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralLoessDatumProperties(Enum):
	CPT_TIP_RESISTANCE = "LAT_LOESS_CPT"

class Loess:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralLoessService_pb2_grpc.LateralLoessServiceStub(self._client.channel)
		self.Datum: Datum[LateralLoessDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getLoessProperties(self) -> LateralLoessService_pb2.LoessProperties:
		request = LateralLoessService_pb2.GetLoessRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetLoessProperties, request)
		return response.loess_props

	def _setLoessProperties(self, loessProps: LateralLoessService_pb2.LoessProperties):
		request = LateralLoessService_pb2.SetLoessRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, loess_props=loessProps)
		self._client.callFunction(self._stub.SetLoessProperties, request)

	def getConePenetrationTipResistance(self) -> float:
		properties = self._getLoessProperties()
		return properties.cone_penetration_loess

	def setConePenetrationTipResistance(self, conePenetrationTipResistance: float):
		properties = self._getLoessProperties()
		properties.cone_penetration_loess = conePenetrationTipResistance
		self._setLoessProperties(properties)