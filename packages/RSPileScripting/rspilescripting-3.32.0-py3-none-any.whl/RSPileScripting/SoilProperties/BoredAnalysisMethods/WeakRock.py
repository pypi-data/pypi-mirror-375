from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockService_pb2 as BoredWeakRockService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockService_pb2_grpc as BoredWeakRockService_pb2_grpc
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRockSkinResistance import SkinResistance
from RSPileScripting.SoilProperties.BoredAnalysisMethods.WeakRockTipResistance import TipResistance

class WeakRock:
	"""
	Examples:
	:ref:`soil properties bored`
	"""
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockService_pb2_grpc.BoredWeakRockServiceStub(self._client.channel)
		self.SkinResistance = SkinResistance(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.TipResistance = TipResistance(model_id=self._model_id, soil_id=self._soil_id, client=self._client)

	def _getWeakRockProperties(self) -> BoredWeakRockService_pb2.WeakRockProperties:
		request = BoredWeakRockService_pb2.GetWeakRockRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetWeakRockProperties, request)
		return response.weak_rock_props

	def _setWeakRockProperties(self, weakRockProperties: BoredWeakRockService_pb2.WeakRockProperties):
		request = BoredWeakRockService_pb2.SetWeakRockRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, weak_rock_props=weakRockProperties)
		self._client.callFunction(self._stub.SetWeakRockProperties, request)

	def setUnconfinedCompressiveStrength(self, unconfinedCompressiveStrength: float):
		properties = self._getWeakRockProperties()
		properties.unconfined_compressive_strength_quc = unconfinedCompressiveStrength
		self._setWeakRockProperties(properties)

	def getUnconfinedCompressiveStrength(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.unconfined_compressive_strength_quc

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		properties = self._getWeakRockProperties()
		properties.wr_skin_friction_limit = skinFrictionLimit
		self._setWeakRockProperties(properties)

	def getSkinFrictionLimit(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.wr_skin_friction_limit

	def setEndBearingLimit(self, endBearingLimit: float):
		properties = self._getWeakRockProperties()
		properties.wr_end_bearing_limit = endBearingLimit
		self._setWeakRockProperties(properties)

	def getEndBearingLimit(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.wr_end_bearing_limit