from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesiveEffectiveStressService_pb2 as BoredCohesiveEffectiveStressService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesiveEffectiveStressService_pb2_grpc as BoredCohesiveEffectiveStressService_pb2_grpc

class EffectiveStress:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesiveEffectiveStressService_pb2_grpc.BoredCohesiveEffectiveStressServiceStub(self._client.channel)

	def _getEffectiveStressProperties(self) -> BoredCohesiveEffectiveStressService_pb2.EffectiveStressProperties:
		request = BoredCohesiveEffectiveStressService_pb2.GetEffectiveStressRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetEffectiveStressProperties, request)
		return response.effective_stress_props

	def _setEffectiveStressProperties(self, effectiveStressProps: BoredCohesiveEffectiveStressService_pb2.EffectiveStressProperties):
		request = BoredCohesiveEffectiveStressService_pb2.SetEffectiveStressRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, effective_stress_props=effectiveStressProps)
		self._client.callFunction(self._stub.SetEffectiveStressProperties, request)

	def setBeta(self, beta: float):
		properties = self._getEffectiveStressProperties()
		properties.beta = beta
		self._setEffectiveStressProperties(properties)

	def getBeta(self) -> float:
		properties = self._getEffectiveStressProperties()
		return properties.beta

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		properties = self._getEffectiveStressProperties()
		properties.limit_skin_resitance_beta = skinFrictionLimit
		self._setEffectiveStressProperties(properties)

	def getSkinFrictionLimit(self) -> float:
		properties = self._getEffectiveStressProperties()
		return properties.limit_skin_resitance_beta

	def setEndBearingLimit(self, endBearingLimit: float):
		properties = self._getEffectiveStressProperties()
		properties.end_bearing_limit_beta = endBearingLimit
		self._setEffectiveStressProperties(properties)

	def getEndBearingLimit(self) -> float:
		properties = self._getEffectiveStressProperties()
		return properties.end_bearing_limit_beta

	def setEffectiveCohesion(self, effectiveCohesion: float):
		properties = self._getEffectiveStressProperties()
		properties.effective_cohesion_c_beta = effectiveCohesion
		self._setEffectiveStressProperties(properties)

	def getEffectiveCohesion(self) -> float:
		properties = self._getEffectiveStressProperties()
		return properties.effective_cohesion_c_beta

	def setBearingCapacityFactorNc(self, Nc: float):
		properties = self._getEffectiveStressProperties()
		properties.bearing_capacity_factor_nc_beta = Nc
		self._setEffectiveStressProperties(properties)

	def getBearingCapacityFactorNc(self) -> float:
		properties = self._getEffectiveStressProperties()
		return properties.bearing_capacity_factor_nc_beta

	def setBearingCapacityFactorNq(self, Nq: float):
		properties = self._getEffectiveStressProperties()
		properties.bearing_capacity_factor_nq_beta = Nq
		self._setEffectiveStressProperties(properties)

	def getBearingCapacityFactorNq(self) -> float:
		properties = self._getEffectiveStressProperties()
		return properties.bearing_capacity_factor_nq_beta