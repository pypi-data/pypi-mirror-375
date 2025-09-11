from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.DrivenCohesionlessSkinFrictionSPTTableService_pb2 as DrivenCohesionlessSkinFrictionSPTTableService_pb2
import RSPileScripting.generated_python_files.soil_services.DrivenCohesionlessSkinFrictionSPTTableService_pb2_grpc as DrivenCohesionlessSkinFrictionSPTTableService_pb2_grpc

class SkinFrictionSPTTable:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = DrivenCohesionlessSkinFrictionSPTTableService_pb2_grpc.DrivenCohesionlessSkinFrictionSPTTableServiceStub(self._client.channel)

	def _getSkinFrictionSPTTableProperties(self) -> DrivenCohesionlessSkinFrictionSPTTableService_pb2.SPTTableProperties:
		request = DrivenCohesionlessSkinFrictionSPTTableService_pb2.GetSPTTableRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSPTTableProperties, request)
		return response.spt_table_props

	def _setSkinFrictionSPTTableProperties(self, SPTProperties: DrivenCohesionlessSkinFrictionSPTTableService_pb2.SPTTableProperties):
		request = DrivenCohesionlessSkinFrictionSPTTableService_pb2.SetSPTTableRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, spt_table_props=SPTProperties)
		self._client.callFunction(self._stub.SetSPTTableProperties, request)

	def setSPTTable(self, SPTTable: list[tuple[float, float]]):
		"""
		Accepts an array of tuples, where each tuple contains (Depth, SPT 'N' Value).
		"""
		properties = self._getSkinFrictionSPTTableProperties()
		depths, sptCounts = zip(*SPTTable)
		del properties.spt_depth_array_skin_friction[:]
		del properties.sptn_array_skin_friction[:]
		properties.spt_depth_array_skin_friction.extend(depths)
		properties.sptn_array_skin_friction.extend(sptCounts)
		self._setSkinFrictionSPTTableProperties(properties)

	def getSPTTable(self) -> list[tuple[float, float]]:
		properties = self._getSkinFrictionSPTTableProperties()
		return list(zip(properties.spt_depth_array_skin_friction, properties.sptn_array_skin_friction))
	
	def setUseSPTCorrectionForOverburdenPressure(self, useSPTCorrectionForOverburdenPressure: bool):
		properties = self._getSkinFrictionSPTTableProperties()
		properties.spt_correction_skin_friction = useSPTCorrectionForOverburdenPressure
		self._setSkinFrictionSPTTableProperties(properties)

	def getUseSPTCorrectionForOverburdenPressure(self) -> bool:
		properties = self._getSkinFrictionSPTTableProperties()
		return properties.spt_correction_skin_friction