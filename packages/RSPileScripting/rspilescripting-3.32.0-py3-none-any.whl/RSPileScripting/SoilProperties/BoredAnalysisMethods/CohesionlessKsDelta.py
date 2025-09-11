from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessKsDeltaService_pb2 as BoredCohesionlessKsDeltaService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessKsDeltaService_pb2_grpc as BoredCohesionlessKsDeltaService_pb2_grpc

class KsDelta:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesionlessKsDeltaService_pb2_grpc.BoredCohesionlessKsDeltaServiceStub(self._client.channel)

	def _getKsDeltaProperties(self) -> BoredCohesionlessKsDeltaService_pb2.KsDeltaProperties:
		request = BoredCohesionlessKsDeltaService_pb2.GetKsDeltaRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetKsDeltaProperties, request)
		return response.ks_delta_props

	def _setKsDeltaProperties(self, ksDeltaProperties: BoredCohesionlessKsDeltaService_pb2.KsDeltaProperties):
		request = BoredCohesionlessKsDeltaService_pb2.SetKsDeltaRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, ks_delta_props=ksDeltaProperties)
		self._client.callFunction(self._stub.SetKsDeltaProperties, request)

	def setOCR(self, ocr: float):
		properties = self._getKsDeltaProperties()
		properties.ocr = ocr
		self._setKsDeltaProperties(properties)

	def getOCR(self) -> float:
		properties = self._getKsDeltaProperties()
		return properties.ocr

	def setKsKoRatio(self, KsKo: float):
		properties = self._getKsDeltaProperties()
		properties.ks_ko = KsKo
		self._setKsDeltaProperties(properties)

	def getKsKoRatio(self) -> float:
		properties = self._getKsDeltaProperties()
		return properties.ks_ko

	def setDeltaPhiRatio(self, deltaPhiRatio: float):
		properties = self._getKsDeltaProperties()
		properties.delta_phi = deltaPhiRatio
		self._setKsDeltaProperties(properties)

	def getDeltaPhiRatio(self) -> float:
		properties = self._getKsDeltaProperties()
		return properties.delta_phi

	def setUseAutoBearingCapacityFactorNq(self, useAutoBearingCapacityFactor: bool):
		properties = self._getKsDeltaProperties()
		properties.use_auto_bearing_capacity_factor=useAutoBearingCapacityFactor
		self._setKsDeltaProperties(properties)

	def getUseAutoBearingCapacityFactorNq(self) -> bool:
		properties = self._getKsDeltaProperties()
		return properties.use_auto_bearing_capacity_factor

	def setBearingCapacityFactorNq(self, Nq: float):
		properties = self._getKsDeltaProperties()
		properties.bearing_capacity_factor=Nq
		self._setKsDeltaProperties(properties)

	def getBearingCapacityFactorNq(self) -> float:
		properties = self._getKsDeltaProperties()
		return properties.bearing_capacity_factor

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		properties = self._getKsDeltaProperties()
		properties.ksdelta_skin_friction_limit = skinFrictionLimit
		self._setKsDeltaProperties(properties)

	def getSkinFrictionLimit(self) -> float:
		properties = self._getKsDeltaProperties()
		return properties.ksdelta_skin_friction_limit

	def setEndBearingLimit(self, endBearingLimit: float):
		properties = self._getKsDeltaProperties()
		properties.ksdelta_end_bearing_limit = endBearingLimit
		self._setKsDeltaProperties(properties)

	def getEndBearingLimit(self) -> float:
		properties = self._getKsDeltaProperties()
		return properties.ksdelta_end_bearing_limit