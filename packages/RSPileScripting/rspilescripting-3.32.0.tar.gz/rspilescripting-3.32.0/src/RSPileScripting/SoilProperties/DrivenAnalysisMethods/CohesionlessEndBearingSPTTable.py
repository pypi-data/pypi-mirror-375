from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.DrivenCohesionlessEndBearingSPTTableService_pb2 as DrivenCohesionlessEndBearingSPTTableService_pb2
import RSPileScripting.generated_python_files.soil_services.DrivenCohesionlessEndBearingSPTTableService_pb2_grpc as DrivenCohesionlessEndBearingSPTTableService_pb2_grpc

class EndBearingSPTTable:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = DrivenCohesionlessEndBearingSPTTableService_pb2_grpc.DrivenCohesionlessEndBearingSPTTableServiceStub(self._client.channel)

	def _getEndBearingSPTTableProperties(self) -> DrivenCohesionlessEndBearingSPTTableService_pb2.SPTTableProperties:
		request = DrivenCohesionlessEndBearingSPTTableService_pb2.GetSPTTableRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSPTTableProperties, request)
		return response.spt_table_props

	def _setEndBearingSPTTableProperties(self, SPTProperties: DrivenCohesionlessEndBearingSPTTableService_pb2.SPTTableProperties):
		request = DrivenCohesionlessEndBearingSPTTableService_pb2.SetSPTTableRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, spt_table_props=SPTProperties)
		self._client.callFunction(self._stub.SetSPTTableProperties, request)

	def setSPTTable(self, SPTTable: list[tuple[float, float]]):
		"""
		Accepts an array of tuples, where each tuple contains (Depth, SPT 'N' Value).
		- depth -> corresponds to spt_depth_array_end_bearing.
		- spt_count -> corresponds to sptn_array_end_bearing.

		Examples:
		:ref:`soil properties driven`
		"""
		properties = self._getEndBearingSPTTableProperties()
		depths, spt_counts = zip(*SPTTable)
		del properties.spt_depth_array_end_bearing[:]
		del properties.sptn_array_end_bearing[:]
		properties.spt_depth_array_end_bearing.extend(depths)
		properties.sptn_array_end_bearing.extend(spt_counts)
		self._setEndBearingSPTTableProperties(properties)

	def getSPTTable(self) -> list[tuple[float, float]]:
		"""
		Examples:
		:ref:`soil properties driven`
		"""
		properties = self._getEndBearingSPTTableProperties()
		return list(zip(properties.spt_depth_array_end_bearing, properties.sptn_array_end_bearing))
	
	def setUseSPTCorrectionForOverburdenPressure(self, useSPTCorrection: bool):
		properties = self._getEndBearingSPTTableProperties()
		properties.spt_correction_end_bearing = useSPTCorrection
		self._setEndBearingSPTTableProperties(properties)

	def getUseSPTCorrectionForOverburdenPressure(self) -> bool:
		properties = self._getEndBearingSPTTableProperties()
		return properties.spt_correction_end_bearing
