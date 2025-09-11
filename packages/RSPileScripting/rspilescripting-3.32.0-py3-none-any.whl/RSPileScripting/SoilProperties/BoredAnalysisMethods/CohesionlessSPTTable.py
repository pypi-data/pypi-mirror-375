from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessSPTTableService_pb2 as BoredCohesionlessSPTTableService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessSPTTableService_pb2_grpc as BoredCohesionlessSPTTableService_pb2_grpc

class SPTTable:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesionlessSPTTableService_pb2_grpc.BoredCohesionlessSPTTableServiceStub(self._client.channel)

	def _getSPTTableProperties(self) -> BoredCohesionlessSPTTableService_pb2.SPTTableProperties:
		request = BoredCohesionlessSPTTableService_pb2.GetSPTTableRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSPTTableProperties, request)
		return response.spt_table_props

	def _setSPTTableProperties(self, SPTProperties: BoredCohesionlessSPTTableService_pb2.SPTTableProperties):
		request = BoredCohesionlessSPTTableService_pb2.SetSPTTableRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, spt_table_props=SPTProperties)
		self._client.callFunction(self._stub.SetSPTTableProperties, request)

	def setSPTTable(self, SPTTable: list[tuple[float, float]]):
		"""
		Accepts an array of tuples, where each tuple contains (Depth, SPT 'N' Value).
		"""
		properties = self._getSPTTableProperties()
		depths, sptCounts = zip(*SPTTable)
		del properties.spt_depth_array_skin_friction[:]
		del properties.sptn_array_skin_friction[:]
		properties.spt_depth_array_skin_friction.extend(depths)
		properties.sptn_array_skin_friction.extend(sptCounts)
		self._setSPTTableProperties(properties)

	def getSPTTable(self) -> list[tuple[float, float]]:
		properties = self._getSPTTableProperties()
		return list(zip(properties.spt_depth_array_skin_friction, properties.sptn_array_skin_friction))