from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessSPTAASHTOService_pb2 as BoredCohesionlessSPTAASHTOService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessSPTAASHTOService_pb2_grpc as BoredCohesionlessSPTAASHTOService_pb2_grpc

class SPTAASHTO:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesionlessSPTAASHTOService_pb2_grpc.BoredCohesionlessSPTAASHTOServiceStub(self._client.channel)

	def _getSPTAASHTOProperties(self) -> BoredCohesionlessSPTAASHTOService_pb2.SPTAASHTOProperties:
		request = BoredCohesionlessSPTAASHTOService_pb2.GetSPTAASHTORequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSPTAASHTOProperties, request)
		return response.spt_aashto_props

	def _setSPTAASHTOProperties(self, sptAASHTOProperties: BoredCohesionlessSPTAASHTOService_pb2.SPTAASHTOProperties):
		request = BoredCohesionlessSPTAASHTOService_pb2.SetSPTAASHTORequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, spt_aashto_props=sptAASHTOProperties)
		self._client.callFunction(self._stub.SetSPTAASHTOProperties, request)

	def setSkinFrictionLimit(self, skinFrictionLimit: float):
		sptAASHTOProperties = self._getSPTAASHTOProperties()
		sptAASHTOProperties.aashto_skin_friction_limit = skinFrictionLimit
		self._setSPTAASHTOProperties(sptAASHTOProperties)

	def getSkinFrictionLimit(self) -> float:
		sptAASHTOProperties = self._getSPTAASHTOProperties()
		return sptAASHTOProperties.aashto_skin_friction_limit

	def setEndBearingLimit(self, endBearingLimit: float):
		sptAASHTOProperties = self._getSPTAASHTOProperties()
		sptAASHTOProperties.aashto_end_bearing_limit = endBearingLimit
		self._setSPTAASHTOProperties(sptAASHTOProperties)

	def getEndBearingLimit(self) -> float:
		sptAASHTOProperties = self._getSPTAASHTOProperties()
		return sptAASHTOProperties.aashto_end_bearing_limit