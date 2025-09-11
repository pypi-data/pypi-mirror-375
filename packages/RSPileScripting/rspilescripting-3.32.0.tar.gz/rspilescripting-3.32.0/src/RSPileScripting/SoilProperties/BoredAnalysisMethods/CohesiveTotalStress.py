from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesiveTotalStressService_pb2 as BoredCohesiveTotalStressService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesiveTotalStressService_pb2_grpc as BoredCohesiveTotalStressService_pb2_grpc

class TotalStress:
	"""
	Examples:
	:ref:`soil properties bored`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesiveTotalStressService_pb2_grpc.BoredCohesiveTotalStressServiceStub(self._client.channel)

	def _getTotalStressProperties(self) -> BoredCohesiveTotalStressService_pb2.TotalStressProperties:
		request = BoredCohesiveTotalStressService_pb2.GetTotalStressRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetTotalStressProperties, request)
		return response.total_stress_props

	def _setTotalStressProperties(self, totalStressProps: BoredCohesiveTotalStressService_pb2.TotalStressProperties):
		request = BoredCohesiveTotalStressService_pb2.SetTotalStressRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, total_stress_props=totalStressProps)
		self._client.callFunction(self._stub.SetTotalStressProperties, request)

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getTotalStressProperties()
		properties.undrained_shear_strength_su_alpha = undrainedShearStrength
		self._setTotalStressProperties(properties)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getTotalStressProperties()
		return properties.undrained_shear_strength_su_alpha

	def setAlpha(self, alpha: float):
		properties = self._getTotalStressProperties()
		properties.alpha = alpha
		self._setTotalStressProperties(properties)

	def getAlpha(self) -> float:
		properties = self._getTotalStressProperties()
		return properties.alpha

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		properties = self._getTotalStressProperties()
		properties.skin_friction_limit_alpha = skinFrictionLimit
		self._setTotalStressProperties(properties)

	def getSkinFrictionLimit(self) -> float:
		properties = self._getTotalStressProperties()
		return properties.skin_friction_limit_alpha

	def setEndBearingLimit(self, endBearingLimit: float):
		properties = self._getTotalStressProperties()
		properties.end_bearing_limit_alpha = endBearingLimit
		self._setTotalStressProperties(properties)

	def getEndBearingLimit(self) -> float:
		properties = self._getTotalStressProperties()
		return properties.end_bearing_limit_alpha

	def setBearingCapacityFactorNc(self, Nc: float):
		properties = self._getTotalStressProperties()
		properties.bearing_capacity_factor_nc_alpha = Nc
		self._setTotalStressProperties(properties)

	def getBearingCapacityFactorNc(self) -> float:
		properties = self._getTotalStressProperties()
		return properties.bearing_capacity_factor_nc_alpha
