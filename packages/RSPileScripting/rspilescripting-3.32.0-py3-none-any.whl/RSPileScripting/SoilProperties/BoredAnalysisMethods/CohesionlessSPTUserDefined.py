from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessSPTUserFactorsService_pb2 as BoredCohesionlessSPTUserFactorsService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessSPTUserFactorsService_pb2_grpc as BoredCohesionlessSPTUserFactorsService_pb2_grpc

class SPTUserFactors:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesionlessSPTUserFactorsService_pb2_grpc.BoredCohesionlessSPTUserFactorsServiceStub(self._client.channel)

	def _getSPTUserFactorsProperties(self) -> BoredCohesionlessSPTUserFactorsService_pb2.SPTUserFactorsProperties:
		request = BoredCohesionlessSPTUserFactorsService_pb2.GetSPTUserFactorsRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSPTUserFactorsProperties, request)
		return response.spt_user_factors_props

	def _setSPTUserFactorsProperties(self, sptUserFactorsProperties: BoredCohesionlessSPTUserFactorsService_pb2.SPTUserFactorsProperties):
		request = BoredCohesionlessSPTUserFactorsService_pb2.SetSPTUserFactorsRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, spt_user_factors_props=sptUserFactorsProperties)
		self._client.callFunction(self._stub.SetSPTUserFactorsProperties, request)

	def setA(self, a: float):
		properties = self._getSPTUserFactorsProperties()
		properties.a = a
		self._setSPTUserFactorsProperties(properties)

	def getA(self) -> float:
		properties = self._getSPTUserFactorsProperties()
		return properties.a

	def setB(self, b: float):
		properties = self._getSPTUserFactorsProperties()
		properties.b = b
		self._setSPTUserFactorsProperties(properties)

	def getB(self) -> float:
		properties = self._getSPTUserFactorsProperties()
		return properties.b

	def setC(self, c: float):
		properties = self._getSPTUserFactorsProperties()
		properties.c = c
		self._setSPTUserFactorsProperties(properties)

	def getC(self) -> float:
		properties = self._getSPTUserFactorsProperties()
		return properties.c

	def setD(self, d: float):
		properties = self._getSPTUserFactorsProperties()
		properties.d = d
		self._setSPTUserFactorsProperties(properties)

	def getD(self) -> float:
		properties = self._getSPTUserFactorsProperties()
		return properties.d

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		properties = self._getSPTUserFactorsProperties()
		properties.user_fs_limit = skinFrictionLimit
		self._setSPTUserFactorsProperties(properties)

	def getSkinFrictionLimit(self) -> float:
		properties = self._getSPTUserFactorsProperties()
		return properties.user_fs_limit

	def setEndBearingLimit(self, endBearing: float):
		properties = self._getSPTUserFactorsProperties()
		properties.user_qb_limit = endBearing
		self._setSPTUserFactorsProperties(properties)

	def getEndBearingLimit(self) -> float:
		properties = self._getSPTUserFactorsProperties()
		return properties.user_qb_limit
