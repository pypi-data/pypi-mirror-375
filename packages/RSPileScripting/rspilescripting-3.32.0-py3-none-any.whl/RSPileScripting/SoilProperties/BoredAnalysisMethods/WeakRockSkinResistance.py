from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockSkinResistanceService_pb2 as BoredWeakRockSkinResistanceService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockSkinResistanceService_pb2_grpc as BoredWeakRockSkinResistanceService_pb2_grpc
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRockSkinResistanceWilliamAndPells import WilliamAndPells
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRockSkinResistanceKulhawyAndPhoon import KulhawyAndPhoon
from enum import Enum

class SkinResistanceMethod(Enum):
	WILLIAM_PELLS = BoredWeakRockSkinResistanceService_pb2.SkinResistanceType.E_WR_SR_WILLIAM_PELLS
	KULHAWY_PHOON = BoredWeakRockSkinResistanceService_pb2.SkinResistanceType.E_WR_SR_KULHAWY_PHOON

class SkinResistance:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockSkinResistanceService_pb2_grpc.BoredWeakRockSkinResistanceServiceStub(self._client.channel)
		self.WilliamAndPells = WilliamAndPells(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.KulhawyAndPhoon = KulhawyAndPhoon(model_id=self._model_id, soil_id=self._soil_id, client=self._client)

	def _getWeakRockSkinResistanceProperties(self) -> BoredWeakRockSkinResistanceService_pb2.SkinResistanceProperties:
		request = BoredWeakRockSkinResistanceService_pb2.GetSkinResistanceRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSkinResistanceProperties, request)
		return response.skin_resistance_props

	def _setWeakRockSkinResistanceProperties(self, skinResistanceProps: BoredWeakRockSkinResistanceService_pb2.SkinResistanceProperties):
		request = BoredWeakRockSkinResistanceService_pb2.SetSkinResistanceRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, 
			skin_resistance_props=skinResistanceProps)
		self._client.callFunction(self._stub.SetSkinResistanceProperties, request)

	def getSkinResistanceMethod(self) -> SkinResistanceMethod:
		properties = self._getWeakRockSkinResistanceProperties()
		return SkinResistanceMethod(properties.skin_resistance_type)

	def setSkinResistanceMethod(self, skinResistanceMethod: SkinResistanceMethod):
		properties = self._getWeakRockSkinResistanceProperties()
		properties.skin_resistance_type = skinResistanceMethod.value
		self._setWeakRockSkinResistanceProperties(properties)