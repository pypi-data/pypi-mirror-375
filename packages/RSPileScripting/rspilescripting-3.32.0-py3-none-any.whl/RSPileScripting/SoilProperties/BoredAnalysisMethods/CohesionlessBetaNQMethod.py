from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessBetaNQService_pb2 as BoredCohesionlessBetaNQService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessBetaNQService_pb2_grpc as BoredCohesionlessBetaNQService_pb2_grpc

class BetaNQ:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesionlessBetaNQService_pb2_grpc.BoredCohesionlessBetaNQServiceStub(self._client.channel)

	def _getBetaNQProperties(self) -> BoredCohesionlessBetaNQService_pb2.BetaNQProperties:
		request = BoredCohesionlessBetaNQService_pb2.GetBetaNQRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetBetaNQProperties, request)
		return response.beta_nq_props

	def _setBetaNQProperties(self, betaNQProperties: BoredCohesionlessBetaNQService_pb2.BetaNQProperties):
		request = BoredCohesionlessBetaNQService_pb2.SetBetaNQRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, beta_nq_props=betaNQProperties)
		self._client.callFunction(self._stub.SetBetaNQProperties, request)

	def setBeta(self, beta: float):
		properties = self._getBetaNQProperties()
		properties.beta_nq_beta = beta
		self._setBetaNQProperties(properties)

	def getBeta(self) -> float:
		properties = self._getBetaNQProperties()
		return properties.beta_nq_beta

	def setBearingCapacityFactorNq(self, Nq: float):
		properties = self._getBetaNQProperties()
		properties.beta_nq_bearing_capacity_factor_nq = Nq
		self._setBetaNQProperties(properties)

	def getBearingCapacityFactorNq(self) -> float:
		properties = self._getBetaNQProperties()
		return properties.beta_nq_bearing_capacity_factor_nq

	def setUseAutoBearingCapacityFactorNq(self, useAutoBearingCapacityFactor: bool):
		properties = self._getBetaNQProperties()
		properties.beta_nq_nq_auto = useAutoBearingCapacityFactor
		self._setBetaNQProperties(properties)

	def getUseAutoBearingCapacityFactorNq(self) -> bool:
		properties = self._getBetaNQProperties()
		return properties.beta_nq_nq_auto

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		properties = self._getBetaNQProperties()
		properties.beta_nq_skin_friction_limit = skinFrictionLimit
		self._setBetaNQProperties(properties)

	def getSkinFrictionLimit(self) -> float:
		properties = self._getBetaNQProperties()
		return properties.beta_nq_skin_friction_limit

	def setEndBearingLimit(self, endBearingLimit: float):
		properties = self._getBetaNQProperties()
		properties.beta_nq_end_bearing_limit = endBearingLimit
		self._setBetaNQProperties(properties)

	def getEndBearingLimit(self) -> float:
		properties = self._getBetaNQProperties()
		return properties.beta_nq_end_bearing_limit