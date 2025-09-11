from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockTipResistanceService_pb2 as BoredWeakRockTipResistanceService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockTipResistanceService_pb2_grpc as BoredWeakRockTipResistanceService_pb2_grpc
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRockTipResistanceTomlinsonAndWoodward import TomlinsonAndWoodward
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRockTipResistanceUserDefinedB import UserDefinedB
from enum import Enum

class TipResistanceMethod(Enum):
	USER_DEFINED = BoredWeakRockTipResistanceService_pb2.TipResistanceType.E_WR_TP_USER_DEF
	ZHANG_EINSTEIN = BoredWeakRockTipResistanceService_pb2.TipResistanceType.E_WR_TP_ZHANG_EINSTEIN
	TOMLINSON_WOODWARD = BoredWeakRockTipResistanceService_pb2.TipResistanceType.E_WR_TP_TOMLINSON

class TipResistance:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockTipResistanceService_pb2_grpc.BoredWeakRockTipResistanceServiceStub(self._client.channel)
		self.TomlinsonAndWoodward = TomlinsonAndWoodward(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.UserDefinedB = UserDefinedB(model_id=self._model_id, soil_id=self._soil_id, client=self._client)

	def _getWeakRockTipResistanceProperties(self) -> BoredWeakRockTipResistanceService_pb2.TipResistanceProperties:
		request = BoredWeakRockTipResistanceService_pb2.GetTipResistanceRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetTipResistanceProperties, request)
		return response.tip_resistance_props

	def _setWeakRockTipResistanceProperties(self, tipResistanceProps: BoredWeakRockTipResistanceService_pb2.TipResistanceProperties):
		request = BoredWeakRockTipResistanceService_pb2.SetTipResistanceRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, 
			tip_resistance_props=tipResistanceProps)
		self._client.callFunction(self._stub.SetTipResistanceProperties, request)

	def getTipResistanceMethod(self) -> TipResistanceMethod:
		properties = self._getWeakRockTipResistanceProperties()
		return TipResistanceMethod(properties.tip_resistance_type)

	def setTipResistanceMethod(self, tipResistanceMethod: TipResistanceMethod):
		properties = self._getWeakRockTipResistanceProperties()
		properties.tip_resistance_type = tipResistanceMethod.value
		self._setWeakRockTipResistanceProperties(properties)